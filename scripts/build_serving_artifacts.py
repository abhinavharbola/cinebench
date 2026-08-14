"""
Builds the production serving artifacts that src/serving/app.py depends on
at startup: a FAISS index over the two-tower item embeddings, and a
LightGBM ranker trained on top of retrieval candidates.

The two-tower model is the designated production path (FastAPI serves one
approach; the Streamlit UI separately compares all 5 for demo purposes).
Run this after scripts/train_two_tower.py has produced
data/processed/two_tower_{item,user}_embeddings.parquet.

Ranker training labels: for each user, the FAISS-retrieved candidates that
are also present in that user's held-out test interactions are labeled
positive. This means scripts/run_phase1.py's test.parquet is used here as
ranker training signal, not as a leaderboard-blind final check -- standard
practice for a re-ranker's own training data, distinct from the harness
evaluation in run_phase1.py which never sees this file.

Usage:
    python scripts/build_serving_artifacts.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl

from src.ranking.features import (
    build_features_for_candidates,
    build_item_genre_map,
    build_user_genre_profiles,
    compute_item_popularity,
    compute_item_recency,
    compute_user_stats,
)
from src.ranking.ranker import build_training_table, save_model, train_ranker
from src.retrieval.faiss_index import FaissRetriever

random.seed(42)

DATA_DIR = Path("data/processed")


def main():
    train_path = DATA_DIR / "train.parquet"
    test_path = DATA_DIR / "test.parquet"
    movies_path = DATA_DIR / "movies.parquet"
    item_emb_path = DATA_DIR / "two_tower_item_embeddings.parquet"
    user_emb_path = DATA_DIR / "two_tower_user_embeddings.parquet"

    for p in [train_path, test_path, movies_path, item_emb_path, user_emb_path]:
        if not p.exists():
            raise FileNotFoundError(
                f"{p} not found. Run scripts/run_phase1.py and "
                "scripts/train_two_tower.py first."
            )

    train = pl.read_parquet(train_path)
    test = pl.read_parquet(test_path)
    movies = pl.read_parquet(movies_path)
    item_embeddings = pl.read_parquet(item_emb_path)
    user_embeddings = pl.read_parquet(user_emb_path)

    (DATA_DIR / "faiss_index").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "ranker").mkdir(parents=True, exist_ok=True)

    retriever = FaissRetriever()
    retriever.build(item_embeddings)
    retriever.save(DATA_DIR / "faiss_index" / "items.index")
    print(f"FAISS index built: {retriever.index.ntotal} items")

    reference_ts = train.select(pl.col("timestamp").max()).item()
    item_genres = build_item_genre_map(movies)
    feature_context = {
        "item_popularity": compute_item_popularity(train),
        "item_recency": compute_item_recency(train, reference_ts),
        "user_stats": compute_user_stats(train, reference_ts),
        "user_genre_profiles": build_user_genre_profiles(train, item_genres),
        "item_genres": item_genres,
    }

    test_positives = (
        test.group_by("userId").agg(pl.col("movieId")).to_dict(as_series=False)
    )
    positive_items = {uid: set(items) for uid, items in zip(test_positives["userId"], test_positives["movieId"])}

    user_emb_lookup = dict(zip(user_embeddings["userId"].to_list(), user_embeddings["embedding"].to_list()))

    per_user_features = {}
    for user_id, embedding in user_emb_lookup.items():
        candidates = retriever.query(embedding, top_n=100)
        per_user_features[user_id] = build_features_for_candidates(user_id, candidates, **feature_context)

    training_table = build_training_table(per_user_features, positive_items)
    print(f"ranker training table: {training_table.height:,} rows")

    ranker = train_ranker(training_table)
    save_model(ranker, DATA_DIR / "ranker" / "lightgbm_ranker.txt")
    print(f"ranker saved to {DATA_DIR / 'ranker' / 'lightgbm_ranker.txt'}")


if __name__ == "__main__":
    main()
