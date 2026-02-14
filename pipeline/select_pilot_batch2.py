"""Select 50 more applicants for rubric pilot batch 2, stratified by tier.

Usage:
    python -m pipeline.select_pilot_batch2
    python -m pipeline.select_pilot_batch2 --n 75  # select 75 instead

Outputs: data/cache/pilot_batch2_ids.json
"""

import argparse
import json
import logging

import numpy as np
import pandas as pd

from pipeline.config import (
    CACHE_DIR,
    ID_COLUMN,
    PROCESSED_DIR,
    TARGET_SCORE,
    TEST_YEAR,
    score_to_tier,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def select_batch2(n: int = 50, seed: int = 42) -> list[int]:
    """Select n applicants from 2024 test set, stratified by tier.

    Excludes applicants already scored in rubric_scores_v2.json.
    Uses proportional stratified sampling to match the full pool distribution.
    """
    # Load 2024 test set
    csv_path = PROCESSED_DIR / f"master_{TEST_YEAR}.csv"
    df = pd.read_csv(csv_path)
    valid = df[TARGET_SCORE].notna()
    df = df[valid].copy()
    logger.info("2024 test set: %d applicants with scores", len(df))

    # Compute tiers
    df["tier"] = df[TARGET_SCORE].apply(score_to_tier)

    # Exclude already-scored
    cache_path = CACHE_DIR / "rubric_scores_v2.json"
    already_scored: set[int] = set()
    if cache_path.exists():
        with open(cache_path) as f:
            already_scored = {int(k) for k in json.load(f).keys()}
    logger.info("Already scored: %d applicants", len(already_scored))

    available = df[~df[ID_COLUMN].isin(already_scored)].copy()
    logger.info("Available for selection: %d applicants", len(available))

    # Tier distribution of full pool
    tier_counts = df["tier"].value_counts().sort_index()
    tier_fracs = tier_counts / len(df)
    logger.info("Full pool tier distribution:")
    for tier, frac in tier_fracs.items():
        logger.info("  Tier %d: %.1f%% (%d)", tier, frac * 100, tier_counts[tier])

    # Proportional allocation
    rng = np.random.default_rng(seed)
    selected_ids: list[int] = []

    for tier in sorted(tier_fracs.index):
        target = max(1, round(n * tier_fracs[tier]))
        tier_pool = available[available["tier"] == tier][ID_COLUMN].values
        actual = min(target, len(tier_pool))
        chosen = rng.choice(tier_pool, size=actual, replace=False)
        selected_ids.extend(int(x) for x in chosen)
        logger.info(
            "  Tier %d: target=%d, available=%d, selected=%d",
            tier, target, len(tier_pool), actual,
        )

    # Trim to exact n if rounding produced extra
    if len(selected_ids) > n:
        selected_ids = list(rng.choice(selected_ids, size=n, replace=False))

    logger.info("Total selected: %d applicants", len(selected_ids))

    # Print tier distribution of selection
    sel_df = df[df[ID_COLUMN].isin(selected_ids)]
    sel_tiers = sel_df["tier"].value_counts().sort_index()
    logger.info("Batch 2 tier distribution:")
    for tier in sorted(sel_tiers.index):
        logger.info("  Tier %d: %d (%.1f%%)", tier, sel_tiers[tier], sel_tiers[tier] / len(sel_df) * 100)

    return selected_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Select stratified pilot batch 2 applicants")
    parser.add_argument("-n", type=int, default=50, help="Number of applicants to select (default: 50)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    ids = select_batch2(n=args.n, seed=args.seed)

    out_path = CACHE_DIR / "pilot_batch2_ids.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(ids, f, indent=2)

    print(f"\nSaved {len(ids)} applicant IDs to {out_path}")
    print(f"Next step: python -m pipeline.run_rubric_scoring_v2 --id-file {out_path} --resume")


if __name__ == "__main__":
    main()
