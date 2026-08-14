"""
Phase 1 runner: ingest -> temporal split -> fit popularity, item-item CF,
ALS/BPR -> evaluate all three through the identical harness -> write
results/comparison_table.csv.

Also persists the artifacts downstream phases depend on:
  - data/processed/train.parquet, read by train_two_tower.py, train_sasrec.py,
    src/serving/app.py, and the Streamlit UI's data access layer.
  - data/processed/models/{popularity,item_item_cf,als}.pkl, read by the
    Streamlit UI's model registry for the 5-way comparison screen.

Usage:
    python scripts/run_phase1.py

Requires data/processed/interactions.parquet and movies.parquet to already
exist (run src/data/ingest.py first, after placing the raw MovieLens 25M
files in data/raw/ml-25m/).
"""

import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import polars as pl

from src.data.split import assert_no_leakage, temporal_split
from src.eval.metrics import evaluate_all
from src.eval.tracking import log_model_run
from src.models.baseline import ItemItemCF, PopularityModel
from src.models.mf import MatrixFactorizationModel

PROCESSED_DIR = Path("data/processed")
MODELS_DIR = PROCESSED_DIR / "models"
RESULTS_DIR = Path("results")
K_VALUES = (10, 20)
TOP_K_FOR_RECS = max(K_VALUES)


def build_item_genres(movies: pl.DataFrame) -> dict:
    out = {}
    for row in movies.iter_rows(named=True):
        out[row["movieId"]] = set(row["genres"].split("|")) if row["genres"] else set()
    return out


def evaluate_model(name: str, model, test: pl.DataFrame, catalog_size: int, item_genres: dict) -> dict:
    test_by_user = (
        test.group_by("userId")
        .agg(pl.col("movieId"))
        .to_dict(as_series=False)
    )
    user_ids = test_by_user["userId"]
    relevant_lists = [set(items) for items in test_by_user["movieId"]]

    all_recommended = [model.recommend(uid, k=TOP_K_FOR_RECS) for uid in user_ids]

    metrics = evaluate_all(all_recommended, relevant_lists, catalog_size, item_genres, ks=K_VALUES)
    metrics["model"] = name
    return metrics


def main():
    interactions = pl.read_parquet(PROCESSED_DIR / "interactions.parquet")
    movies = pl.read_parquet(PROCESSED_DIR / "movies.parquet")
    item_genres = build_item_genres(movies)
    catalog_size = interactions["movieId"].n_unique()

    split = temporal_split(interactions)
    assert_no_leakage(split)  # hard stop if the harness itself is broken
    print(f"train: {split.train.height:,} rows, test: {split.test.height:,} rows, "
          f"cutoff: {split.cutoff_timestamp}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    # persisted here, not just held in memory: train_two_tower.py,
    # train_sasrec.py, src/serving/app.py, and the Streamlit UI all read
    # this same file, so every downstream phase trains/serves on the exact
    # same split the comparison table was scored against.
    split.train.write_parquet(PROCESSED_DIR / "train.parquet")
    split.test.write_parquet(PROCESSED_DIR / "test.parquet")

    results = []

    pop = PopularityModel()
    pop.fit(split.train)
    pop_metrics = evaluate_model("popularity", pop, split.test, catalog_size, item_genres)
    results.append(pop_metrics)
    with log_model_run("popularity", params={}, metrics=pop_metrics):
        pass
    with open(MODELS_DIR / "popularity.pkl", "wb") as f:
        pickle.dump(pop, f)
    print("popularity done")

    cf = ItemItemCF(top_k=50)
    cf.fit(split.train)
    cf_metrics = evaluate_model("item_item_cf", cf, split.test, catalog_size, item_genres)
    results.append(cf_metrics)
    with log_model_run("item_item_cf", params={"top_k": 50}, metrics=cf_metrics):
        pass
    with open(MODELS_DIR / "item_item_cf.pkl", "wb") as f:
        pickle.dump(cf, f)
    print("item-item CF done")

    als = MatrixFactorizationModel(method="als", factors=64, iterations=15)
    als.fit(split.train)
    als_metrics = evaluate_model("als", als, split.test, catalog_size, item_genres)
    results.append(als_metrics)
    with log_model_run("als", params={"factors": 64, "iterations": 15}, metrics=als_metrics):
        pass
    with open(MODELS_DIR / "als.pkl", "wb") as f:
        pickle.dump(als, f)
    print("ALS done")

    RESULTS_DIR.mkdir(exist_ok=True)
    table = pl.DataFrame(results).select(
        ["model"] + [c for c in pl.DataFrame(results).columns if c != "model"]
    )
    table.write_csv(RESULTS_DIR / "comparison_table.csv")
    print(table)
    print(f"\nwritten to {RESULTS_DIR / 'comparison_table.csv'}")
    print(f"models written to {MODELS_DIR}")


if __name__ == "__main__":
    main()
