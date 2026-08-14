"""
Temporal train/test split.

Design note (this fixes an inconsistency in the original spec, where one
section described a global timestamp cutoff and another described a plain
per-user leave-last-N-out split with no shared cutoff):

  A pure per-user leave-last-N-out split, with no global cutoff, does not
  fully prevent leakage: one user's "last N" interactions can be earlier in
  real time than another user's "training" interactions, so models can still
  absorb future signal (item popularity trends, release-driven spikes)
  across the user base even though each individual user's split looks
  temporally correct in isolation.

  Fix used here: a single global timestamp cutoff is the hard train/test
  boundary. No train interaction is ever later than the cutoff, and no test
  interaction is ever earlier than it. Within the post-cutoff pool, each
  user's test set is capped at N interactions (earliest-first) purely to
  keep per-user metric computation comparable across users, never to
  override the global boundary.
"""

from dataclasses import dataclass

import polars as pl


@dataclass
class SplitResult:
    train: pl.DataFrame
    test: pl.DataFrame
    cutoff_timestamp: int


def compute_global_cutoff(interactions: pl.DataFrame, test_quantile: float = 0.9) -> int:
    """
    Pick a single global timestamp cutoff such that roughly
    (1 - test_quantile) of interactions fall after it.
    """
    cutoff = interactions.select(pl.col("timestamp").quantile(test_quantile)).item()
    return int(cutoff)


def temporal_split(
    interactions: pl.DataFrame,
    cutoff_timestamp: int | None = None,
    test_quantile: float = 0.9,
    max_test_per_user: int = 10,
    min_train_interactions: int = 5,
) -> SplitResult:
    """
    Split interactions into train/test using a global cutoff, then cap each
    user's test set at max_test_per_user (earliest-first among their
    post-cutoff interactions).

    Users with fewer than min_train_interactions in train are dropped from
    both train and test — they don't have enough history for a fair
    per-user evaluation, and are handled separately by the cold-start path.
    """
    if cutoff_timestamp is None:
        cutoff_timestamp = compute_global_cutoff(interactions, test_quantile)

    train = interactions.filter(pl.col("timestamp") < cutoff_timestamp)
    test_pool = interactions.filter(pl.col("timestamp") >= cutoff_timestamp)

    train_counts = train.group_by("userId").agg(pl.len().alias("n_train"))
    eligible_users = train_counts.filter(pl.col("n_train") >= min_train_interactions)["userId"].to_list()

    train = train.filter(pl.col("userId").is_in(eligible_users))

    test = (
        test_pool.filter(pl.col("userId").is_in(eligible_users))
        .sort(["userId", "timestamp"])
        .group_by("userId", maintain_order=True)
        .head(max_test_per_user)
    )

    return SplitResult(train=train, test=test, cutoff_timestamp=cutoff_timestamp)


def assert_no_leakage(split: SplitResult) -> None:
    """
    Hard invariant check, also exercised in tests/test_split.py:
      1. no train interaction timestamp >= cutoff
      2. no test interaction timestamp < cutoff
      3. every test user also appears in train (no cold users in eval set)
    """
    max_train_ts = split.train.select(pl.col("timestamp").max()).item()
    min_test_ts = split.test.select(pl.col("timestamp").min()).item()

    if max_train_ts is not None and max_train_ts >= split.cutoff_timestamp:
        raise AssertionError("train contains interactions at/after the cutoff")
    if min_test_ts is not None and min_test_ts < split.cutoff_timestamp:
        raise AssertionError("test contains interactions before the cutoff")

    train_users = set(split.train["userId"].unique().to_list())
    test_users = set(split.test["userId"].unique().to_list())
    if not test_users.issubset(train_users):
        raise AssertionError("test contains users absent from train")
