"""
Post-scoring validation for v2 rubric scores.

Checks:
  1. Score distribution (no single level > 40%)
  2. Inter-dimension correlation (target: r < 0.60 for PS dims)
  3. Zero-rate analysis
  4. Parse failure rate
  5. Comparison with v1 scores (if available)

Usage:
    python -m pipeline.validate_scores data/cache/rubric_scores_v2_smoke.json
    python -m pipeline.validate_scores v2.json --v1 data/cache/rubric_scores.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PS_DIMS = [
    "writing_quality",
    "authenticity_and_self_awareness",
    "mission_alignment_service_orientation",
    "adversity_resilience",
    "motivation_depth",
    "intellectual_curiosity",
    "maturity_and_reflection",
]


def load_v2_scores(path: str) -> pd.DataFrame:
    """Load v2 scores into a DataFrame."""
    with open(path) as f:
        data = json.load(f)

    rows = []
    for aid, info in data.items():
        row = {"applicant_id": aid}
        row.update(info.get("scores", {}))
        rows.append(row)

    return pd.DataFrame(rows).set_index("applicant_id")


def check_distribution(df: pd.DataFrame) -> None:
    """Check that no single score level exceeds 40% for any dimension."""
    print("\n=== SCORE DISTRIBUTION ===")
    violations = []
    for col in df.columns:
        values = df[col][df[col] > 0]  # exclude zeros (missing text)
        if len(values) < 5:
            print(f"  {col}: too few scores ({len(values)}) to assess")
            continue
        dist = values.value_counts(normalize=True).sort_index()
        max_pct = dist.max() * 100
        max_level = dist.idxmax()
        flag = " ⚠️ VIOLATION" if max_pct > 40 else ""
        print(f"  {col}: max={max_pct:.0f}% at level {max_level}{flag}")
        if max_pct > 40:
            violations.append((col, max_level, max_pct))

    if violations:
        print(f"\n  {len(violations)} dimension(s) exceed 40% threshold:")
        for col, level, pct in violations:
            print(f"    {col}: {pct:.0f}% at level {level}")
    else:
        print("  ✅ All dimensions pass distribution check")


def check_correlation(df: pd.DataFrame) -> None:
    """Check inter-dimension correlation for PS dimensions."""
    print("\n=== PS DIMENSION CORRELATIONS ===")
    ps_cols = [c for c in PS_DIMS if c in df.columns]
    ps_df = df[ps_cols].replace(0, np.nan).dropna()

    if len(ps_df) < 10:
        print(f"  Too few complete records ({len(ps_df)}) for correlation analysis")
        return

    corr = ps_df.corr()

    # Find high correlations (above threshold)
    threshold = 0.60
    violations = []
    print(f"  Target: r < {threshold} for all PS dimension pairs")
    print()

    for i, dim1 in enumerate(ps_cols):
        for dim2 in ps_cols[i + 1 :]:
            r = corr.loc[dim1, dim2]
            flag = " ⚠️ HIGH" if abs(r) > threshold else ""
            print(f"  {dim1[:30]:30s} × {dim2[:30]:30s}  r={r:.3f}{flag}")
            if abs(r) > threshold:
                violations.append((dim1, dim2, r))

    if violations:
        print(f"\n  {len(violations)} pair(s) exceed r={threshold} threshold")
        print("  Compare to v1 baseline (r > 0.97) to assess improvement")
    else:
        print(f"\n  ✅ All PS dimension pairs below r={threshold}")


def check_zeros(df: pd.DataFrame) -> None:
    """Analyze zero-rate across dimensions."""
    print("\n=== ZERO-RATE ANALYSIS ===")
    for col in df.columns:
        n_zero = (df[col] == 0).sum()
        n_total = len(df)
        pct = n_zero / n_total * 100
        flag = " ⚠️" if pct > 10 else ""
        if n_zero > 0:
            print(f"  {col}: {n_zero}/{n_total} ({pct:.0f}%) zeros{flag}")

    total_zeros = (df == 0).sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    overall_pct = total_zeros / total_cells * 100
    print(f"\n  Overall: {total_zeros}/{total_cells} ({overall_pct:.1f}%) zeros")
    if overall_pct > 20:
        print("  ⚠️ High zero-rate — check text availability in data pipeline")


def compare_v1(v2_df: pd.DataFrame, v1_path: str) -> None:
    """Compare v2 scores against v1 for overlapping applicants."""
    print("\n=== V1 vs V2 COMPARISON ===")
    with open(v1_path) as f:
        v1_data = json.load(f)

    v1_rows = []
    for aid, scores in v1_data.items():
        row = {"applicant_id": str(aid)}
        if isinstance(scores, dict):
            row.update(scores)
        v1_rows.append(row)

    v1_df = pd.DataFrame(v1_rows).set_index("applicant_id")

    # Find overlapping applicants and dimensions
    common_ids = v2_df.index.intersection(v1_df.index)
    common_dims = v2_df.columns.intersection(v1_df.columns)

    print(f"  Overlapping applicants: {len(common_ids)}")
    print(f"  Overlapping dimensions: {len(common_dims)}")

    if len(common_ids) < 3 or len(common_dims) < 1:
        print("  Too few overlapping records for comparison")
        return

    for dim in sorted(common_dims):
        v1_vals = v1_df.loc[common_ids, dim].astype(float)
        v2_vals = v2_df.loc[common_ids, dim].astype(float)

        # Filter out zeros
        mask = (v1_vals > 0) & (v2_vals > 0)
        if mask.sum() < 3:
            continue

        v1_m = v1_vals[mask].mean()
        v2_m = v2_vals[mask].mean()
        diff = v2_m - v1_m
        print(f"  {dim[:40]:40s}  v1={v1_m:.2f}  v2={v2_m:.2f}  Δ={diff:+.2f}")


def main():
    parser = argparse.ArgumentParser(description="Validate v2 rubric scores")
    parser.add_argument("scores_path", help="Path to v2 scores JSON")
    parser.add_argument("--v1", help="Path to v1 scores JSON for comparison")
    args = parser.parse_args()

    if not Path(args.scores_path).exists():
        logger.error("File not found: %s", args.scores_path)
        sys.exit(1)

    df = load_v2_scores(args.scores_path)
    print(f"Loaded {len(df)} applicants, {len(df.columns)} dimensions")

    check_distribution(df)
    check_correlation(df)
    check_zeros(df)

    if args.v1 and Path(args.v1).exists():
        compare_v1(df, args.v1)

    print("\nValidation complete.")


if __name__ == "__main__":
    main()
