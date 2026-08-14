"""
FastAPI serving layer, CPU-only. Reads only local cached artifacts (FAISS
index, LightGBM ranker, embedding parquet files) -- no live external API
calls at request time, ever, per the project spec.

Run: uvicorn src.serving.app:app --reload
"""

import logging
from pathlib import Path

import numpy as np
import polars as pl
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.ranking.features import (
    build_features_for_candidates,
    build_item_genre_map,
    build_user_genre_profiles,
    compute_item_popularity,
    compute_item_recency,
    compute_user_stats,
)
from src.ranking.ranker import load_model, rank_candidates
from src.retrieval.faiss_index import FaissRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recsys.serving")

ARTIFACTS_DIR = Path("data/processed")
RESULTS_DIR = Path("results")

app = FastAPI(title="MovieLens Recommender")

_state: dict = {}


class RecommendationRequest(BaseModel):
    user_id: int
    top_n: int = 10
    retrieval_pool_size: int = 100


class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    genres: str
    score: float


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: list[RecommendationItem]


@app.on_event("startup")
def load_artifacts() -> None:
    """All artifacts loaded once at startup, held in memory -- no per-request
    disk or network I/O beyond what's already resident."""
    logger.info("loading cached artifacts")

    train = pl.read_parquet(ARTIFACTS_DIR / "train.parquet")
    movies = pl.read_parquet(ARTIFACTS_DIR / "movies.parquet")

    retriever = FaissRetriever()
    retriever.load(ARTIFACTS_DIR / "faiss_index" / "items.index")

    ranker = load_model(ARTIFACTS_DIR / "ranker" / "lightgbm_ranker.txt")

    user_embeddings = pl.read_parquet(ARTIFACTS_DIR / "two_tower_user_embeddings.parquet")
    user_emb_lookup = dict(zip(user_embeddings["userId"].to_list(), user_embeddings["embedding"].to_list()))

    reference_timestamp = train.select(pl.col("timestamp").max()).item()
    item_genres = build_item_genre_map(movies)

    _state.update({
        "train": train,
        "movies": movies,
        "retriever": retriever,
        "ranker": ranker,
        "user_emb_lookup": user_emb_lookup,
        "item_popularity": compute_item_popularity(train),
        "item_recency": compute_item_recency(train, reference_timestamp),
        "user_stats": compute_user_stats(train, reference_timestamp),
        "item_genres": item_genres,
        "user_genre_profiles": build_user_genre_profiles(train, item_genres),
    })
    logger.info("artifacts loaded, serving ready")


@app.get("/health")
def health():
    return {"status": "ok", "artifacts_loaded": len(_state) > 0}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest):
    if req.user_id not in _state["user_emb_lookup"]:
        raise HTTPException(status_code=404, detail=f"user {req.user_id} not found in cached embeddings")

    user_vec = np.array(_state["user_emb_lookup"][req.user_id], dtype=np.float32)
    candidates = _state["retriever"].query(user_vec, top_n=req.retrieval_pool_size)

    features = build_features_for_candidates(
        req.user_id,
        candidates,
        _state["item_popularity"],
        _state["item_recency"],
        _state["user_stats"],
        _state["user_genre_profiles"],
        _state["item_genres"],
    )
    ranked_ids = rank_candidates(_state["ranker"], features, top_k=req.top_n)

    movies = _state["movies"]
    scores_by_id = dict(zip(features["movieId"].to_list(), features["embedding_similarity"].to_list()))

    items = []
    for movie_id in ranked_ids:
        movie_row = movies.filter(pl.col("movieId") == movie_id)
        if movie_row.height == 0:
            continue
        items.append(RecommendationItem(
            movie_id=movie_id,
            title=movie_row["title"][0],
            genres=movie_row["genres"][0],
            score=scores_by_id.get(movie_id, 0.0),
        ))

    return RecommendationResponse(user_id=req.user_id, recommendations=items)
