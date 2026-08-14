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
MODEL_PREFIXES = ["two_tower", "sasrec"]


def build_for_model(prefix: str, train: pl.DataFrame, positive_items: dict, feature_context: dict) -> bool:
    item_emb_path = DATA_DIR / f"{prefix}_item_embeddings.parquet"
    user_emb_path = DATA_DIR / f"{prefix}_user_embeddings.parquet"

    if not item_emb_path.exists() or not user_emb_path.exists():
        print(f"skipping {prefix}: embeddings not found at {item_emb_path}")
        return False

    item_embeddings = pl.read_parquet(item_emb_path)
    user_embeddings = pl.read_parquet(user_emb_path)

    retriever = FaissRetriever()
    retriever.build(item_embeddings)
    (DATA_DIR / "faiss_index").mkdir(parents=True, exist_ok=True)
    retriever.save(DATA_DIR / "faiss_index" / f"{prefix}_items.index")
    embedding_dim = len(item_embeddings["embedding"][0])
    print(f"{prefix}: FAISS index built, {retriever.index.ntotal} items, dim {embedding_dim}")

    user_emb_lookup = dict(zip(user_embeddings["userId"].to_list(), user_embeddings["embedding"].to_list()))

    per_user_features = {}
    for user_id, embedding in user_emb_lookup.items():
        candidates = retriever.query(embedding, top_n=100)
        per_user_features[user_id] = build_features_for_candidates(user_id, candidates, **feature_context)

    training_table = build_training_table(per_user_features, positive_items)
    ranker = train_ranker(training_table)

    (DATA_DIR / "ranker").mkdir(parents=True, exist_ok=True)
    save_model(ranker, DATA_DIR / "ranker" / f"{prefix}_ranker.txt")
    print(f"{prefix}: ranker trained on {training_table.height:,} rows, saved")
    return True


def main():
    train_path = DATA_DIR / "train.parquet"
    test_path = DATA_DIR / "test.parquet"
    movies_path = DATA_DIR / "movies.parquet"

    for p in [train_path, test_path, movies_path]:
        if not p.exists():
            raise FileNotFoundError(f"{p} not found. Run scripts/run_phase1.py first.")

    train = pl.read_parquet(train_path)
    test = pl.read_parquet(test_path)
    movies = pl.read_parquet(movies_path)

    reference_ts = train.select(pl.col("timestamp").max()).item()
    item_genres = build_item_genre_map(movies)
    feature_context = {
        "item_popularity": compute_item_popularity(train),
        "item_recency": compute_item_recency(train, reference_ts),
        "user_stats": compute_user_stats(train, reference_ts),
        "user_genre_profiles": build_user_genre_profiles(train, item_genres),
        "item_genres": item_genres,
    }

    test_positives = test.group_by("userId").agg(pl.col("movieId")).to_dict(as_series=False)
    positive_items = {uid: set(items) for uid, items in zip(test_positives["userId"], test_positives["movieId"])}

    built_any = False
    for prefix in MODEL_PREFIXES:
        if build_for_model(prefix, train, positive_items, feature_context):
            built_any = True

    if not built_any:
        print("no embedding files found for any model -- nothing built. "
              "Copy two_tower_*.parquet and/or sasrec_*.parquet into data/processed/ first.")
    else:
        print("\ndone. restart the Streamlit app to pick up the rebuilt artifacts.")


if __name__ == "__main__":
    main()