"""Run v2 atomic rubric scoring for medical school holistic review.

This is the production scorer using research-grounded atomic prompts (1 dimension per API call)
to eliminate halo effects that caused r > 0.97 multicollinearity in v1.

Architecture:
  - 7 PS dimensions  × 1 call each = 7 calls per applicant (if PS text exists)
  - 9 EXP dimensions × 1 call each = 9 calls per applicant (if exp text exists)
  - Total: up to 16 calls per applicant (was 11 composite calls in v1)
  - Scale: 1-4 (no neutral midpoint, forces evaluator to commit)

Research basis:
  - LLM-Rubric (ACL 2024): atomic scoring eliminates halo effect
  - AutoSCORE (arxiv:2509.21910): evidence extraction before scoring
  - G-Eval (EMNLP 2023): CoT + form-filling paradigm

Usage:
    # Score all applicants (all years)
    python -m pipeline.run_rubric_scoring_v2

    # Score specific years
    python -m pipeline.run_rubric_scoring_v2 --years 2024

    # Score a single applicant (for testing)
    python -m pipeline.run_rubric_scoring_v2 --amcas-id 13149516 -n 1

    # Resume from where you left off (skips already-scored applicants)
    python -m pipeline.run_rubric_scoring_v2 --resume

    # Print prompt structure without calling API
    python -m pipeline.run_rubric_scoring_v2 --dry-run
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.config import (
    CACHE_DIR,
    CURATED_RUBRIC_DIMS,
    ID_COLUMN,
)
from pipeline.data_preparation import (
    load_experiences,
    build_personal_statements_dict,
    build_secondary_texts_dict,
)
from pipeline.rubric_prompts_v2 import (
    EXPERIENCE_DOMAINS,
    EXPERIENCE_PROMPTS,
    PS_DIMENSIONS,
    SYSTEM_PROMPT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Experience domain → AMCAS Exp_Type mapping (v2 domains)
# ---------------------------------------------------------------------------

DOMAIN_EXP_TYPES_V2: dict[str, list[str]] = {
    "direct_patient_care": [
        "Paid Employment - Medical/Clinical",
        "Community Service/Volunteer - Medical/Clinical",
    ],
    "research": [
        "Research/Lab",
    ],
    "community_service": [
        "Community Service/Volunteer - Not Medical/Clinical",
        "Community Service/Volunteer - Medical/Clinical",
    ],
    "leadership": [
        "Leadership - Not Listed Elsewhere",
    ],
    "clinical_exposure": [
        "Physician Shadowing/Clinical Observation",
    ],
    "clinical_employment": [
        "Paid Employment - Medical/Clinical",
    ],
}

# Domains that use keyword search instead of Exp_Type filtering
DOMAIN_KEYWORDS_V2: dict[str, list[str]] = {
    "teaching_mentoring": [
        "tutor", "teach", "mentor", "ta ", "teaching assistant",
        "instructor", "peer educator", "academic coach",
    ],
    "advocacy_policy": [
        "advocacy", "advocate", "policy", "legislative", "lobby",
        "campaign", "public health", "health equity", "social justice",
        "community organizing",
    ],
    "global_crosscultural": [
        "global", "international", "abroad", "cross-cultural",
        "mission trip", "global health", "cultural immersion",
        "refugee", "immigrant", "translation", "interpreter",
    ],
}


def _gather_experience_text_v2(
    applicant_exps: pd.DataFrame,
    domain: str,
) -> str:
    """Extract relevant experience text for a v2 domain.

    For Exp_Type-mapped domains, filters by type.
    For keyword-mapped domains, searches Exp_Name + Exp_Desc.
    """
    if applicant_exps.empty:
        return ""

    exp_type_col = "Exp_Type" if "Exp_Type" in applicant_exps.columns else "exp_type"

    if domain in DOMAIN_KEYWORDS_V2:
        # Keyword search
        keywords = DOMAIN_KEYWORDS_V2[domain]
        matches = []
        for _, row in applicant_exps.iterrows():
            text_parts = []
            for col in ["Exp_Name", "Exp_Desc"]:
                val = row.get(col)
                if val is not None and pd.notna(val):
                    text_parts.append(str(val))
            combined = " ".join(text_parts).lower()
            if any(kw in combined for kw in keywords):
                matches.append(dict(row))
        if not matches:
            return ""
        relevant = pd.DataFrame(matches)
    elif domain in DOMAIN_EXP_TYPES_V2:
        # Exp_Type filter
        relevant_types = DOMAIN_EXP_TYPES_V2[domain]
        if exp_type_col not in applicant_exps.columns:
            return ""

        def _type_matches(t: object) -> bool:
            if t is None or (isinstance(t, float) and pd.isna(t)):
                return False
            return any(rt.lower() in str(t).lower() for rt in relevant_types)

        mask = applicant_exps[exp_type_col].apply(_type_matches)
        relevant = applicant_exps[mask]
    else:
        return ""

    if len(relevant) == 0:
        return ""

    # Format each experience as readable text
    entries = []
    for _, row in relevant.iterrows():
        parts = []
        exp_name = row.get("Exp_Name")
        if exp_name is not None and pd.notna(exp_name):
            parts.append(f"Title: {exp_name}")
        exp_type_val = row.get(exp_type_col)
        if exp_type_val is not None and pd.notna(exp_type_val):
            parts.append(f"Type: {exp_type_val}")
        exp_desc = row.get("Exp_Desc")
        if exp_desc is not None and pd.notna(exp_desc):
            parts.append(f"Description: {exp_desc}")

        # Include hours if available
        hour_cols = [c for c in row.index if "hour" in str(c).lower()]
        for hc in hour_cols:
            val = row.get(hc)
            if val is not None and pd.notna(val):
                try:
                    if float(val) > 0:
                        parts.append(f"{hc}: {val}")
                except (ValueError, TypeError):
                    pass

        entries.append("\n".join(parts))

    return "\n---\n".join(entries)




def build_applicant_records(
    years: list[int],
    n: int | None = None,
    amcas_id: int | None = None,
    id_file: Path | None = None,
) -> list[dict[str, Any]]:
    """Load applicant data and build records for v2 scoring.

    Returns list of dicts matching the schema expected by rubric_scorer_v2.score_batch().
    """
    experiences_df = load_experiences(years)
    ps_dict = build_personal_statements_dict(years)
    sec_dict = build_secondary_texts_dict(years)

    # Determine applicant IDs
    all_ids = set(experiences_df[ID_COLUMN].unique())
    all_ids.update(ps_dict.keys())
    all_ids.update(sec_dict.keys())

    if amcas_id:
        if amcas_id not in all_ids:
            logger.error("AMCAS ID %d not found in data", amcas_id)
            sys.exit(1)
        applicant_ids = [amcas_id]
    elif id_file:
        with open(id_file) as f:
            target_ids = set(json.load(f))
        applicant_ids = sorted(aid for aid in all_ids if aid in target_ids)
        missing = target_ids - set(applicant_ids)
        if missing:
            logger.warning("%d IDs from file not found in data: %s", len(missing), list(missing)[:5])
        logger.info("Filtered to %d applicants from ID file", len(applicant_ids))
    else:
        applicant_ids = sorted(all_ids)
        if n:
            applicant_ids = applicant_ids[:n]

    logger.info("Building records for %d applicants", len(applicant_ids))

    records = []
    for aid in applicant_ids:
        # Gather experience text per v2 domain
        applicant_exps = experiences_df[experiences_df[ID_COLUMN] == aid]
        experience_texts: dict[str, str] = {}
        for domain_key in EXPERIENCE_DOMAINS:
            text = _gather_experience_text_v2(applicant_exps, domain_key)
            if text:
                experience_texts[domain_key] = text

        records.append({
            "applicant_id": aid,
            "ps_text": ps_dict.get(aid),
            "secondary_text": sec_dict.get(aid),
            "experience_texts": experience_texts,
        })

    # Report coverage
    has_ps = sum(1 for r in records if r["ps_text"])
    has_exp = sum(1 for r in records if r["experience_texts"])
    has_sec = sum(1 for r in records if r["secondary_text"])
    logger.info(
        "Coverage: %d/%d PS, %d/%d experiences, %d/%d secondary",
        has_ps, len(records), has_exp, len(records), has_sec, len(records),
    )

    return records


def get_llm_call():
    """Get the unified LLM call function.

    Uses pipeline.llm_client (Azure OpenAI with JSON mode and retry).
    """
    from pipeline.llm_client import create_llm_call
    return create_llm_call()


def run_scoring(
    n: int | None,
    dry_run: bool = False,
    years: list[int] | None = None,
    amcas_id: int | None = None,
    resume: bool = False,
    id_file: Path | None = None,
    dims: str = "all",
) -> None:
    """Run v2 atomic rubric scoring."""
    years = years or [2022, 2023, 2024]

    # Resolve dimension filter
    dims_filter: set[str] | None = None
    if dims == "curated":
        dims_filter = set(CURATED_RUBRIC_DIMS)
        logger.info("Scoring curated %d dimensions: %s", len(dims_filter), sorted(dims_filter))
    elif dims != "all":
        logger.error("Unknown --dims value: %s (use 'all' or 'curated')", dims)
        sys.exit(1)

    if dry_run:
        logger.info("=== DRY RUN: printing prompt structure ===")
        print(f"\nDimension mode: {dims}")
        if dims_filter:
            print(f"Scoring {len(dims_filter)} curated dimensions:")
            for d in sorted(dims_filter):
                print(f"  - {d}")
        else:
            print(f"\nSystem prompt ({len(SYSTEM_PROMPT)} chars):")
            print(SYSTEM_PROMPT[:200] + "...")
            print(f"\n{len(PS_DIMENSIONS)} PS dimensions:")
            for name, tmpl in PS_DIMENSIONS:
                print(f"  {name}: {len(tmpl)} chars")
            print(f"\n{len(EXPERIENCE_PROMPTS)} experience domains:")
            for name, tmpl in EXPERIENCE_PROMPTS.items():
                print(f"  {name}: {len(tmpl)} chars")
            print(f"\nTotal dimensions per applicant: {len(PS_DIMENSIONS) + len(EXPERIENCE_PROMPTS)}")
        print(f"\nScale: 1-4 (no neutral midpoint)")
        print("Dry run complete.")
        return

    from pipeline.rubric_scorer_v2 import score_batch, MIN_SCORABLE_TEXT

    # Load applicant data
    applicants = build_applicant_records(years, n=n, amcas_id=amcas_id, id_file=id_file)

    # Log input quality summary
    for rec in applicants:
        aid = rec["applicant_id"]
        ps_len = len(rec["ps_text"]) if rec["ps_text"] else 0
        sec_len = len(rec["secondary_text"]) if rec["secondary_text"] else 0
        exp_count = len(rec["experience_texts"])
        exp_short = sum(1 for t in rec["experience_texts"].values() if len(t) < MIN_SCORABLE_TEXT)
        if exp_short > 0 or ps_len == 0:
            logger.warning(
                "Applicant %d: PS=%d chars, secondary=%d chars, %d exp domains (%d below minimum)",
                aid, ps_len, sec_len, exp_count, exp_short,
            )

    if not applicants:
        logger.error("No applicants to score.")
        sys.exit(1)

    # Resume support: skip already-scored applicants
    if resume:
        out_path = CACHE_DIR / "rubric_scores_v2.json"
        if out_path.exists():
            with open(out_path) as f:
                existing = json.load(f)
            already_scored = {int(k) for k in existing.keys()}
            before = len(applicants)
            applicants = [a for a in applicants if a["applicant_id"] not in already_scored]
            logger.info("Resume mode: skipping %d already-scored, %d remaining", before - len(applicants), len(applicants))
        else:
            logger.info("No existing scores found, starting fresh")

    if not applicants:
        logger.info("No applicants to score.")
        return

    # Get LLM client
    llm_call = get_llm_call()

    # Score
    results = score_batch(applicants, llm_call, dims_filter=dims_filter)

    # Save results
    out_dir = CACHE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "rubric_scores_v2.json"

    # Merge with existing results (for --resume and --id-file workflows)
    output: dict[str, Any] = {}
    if out_path.exists():
        with open(out_path) as f:
            output = json.load(f)

    for result in results:
        aid = str(result["applicant_id"])
        output[aid] = {
            "scores": result["scores"],
            "details": {
                dim: {
                    "evidence_extracted": info.get("evidence_extracted", ""),
                    "reasoning": info.get("reasoning", ""),
                }
                for dim, info in result.get("details", {}).items()
            },
            "metadata": result["metadata"],
        }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    logger.info("Saved %d scored applicants to %s", len(output), out_path)

    # Print summary
    print("\n" + "=" * 70)
    print("V2 SMOKE TEST RESULTS")
    print("=" * 70)

    total_calls = sum(r["metadata"]["total_calls"] for r in results)
    total_failures = sum(r["metadata"]["parse_failures"] for r in results)
    total_time = sum(r["metadata"]["elapsed_seconds"] for r in results)

    print(f"Applicants scored: {len(results)}")
    print(f"Total API calls:   {total_calls}")
    print(f"Parse failures:    {total_failures} ({total_failures/max(total_calls,1)*100:.1f}%)")
    print(f"Total time:        {total_time:.1f}s")
    print(f"Avg per applicant: {total_time/max(len(results),1):.1f}s")

    for result in results:
        aid = result["applicant_id"]
        scores = result["scores"]
        print(f"\n--- Applicant {aid} ---")
        for dim, score in sorted(scores.items()):
            indicator = "  [missing text]" if score == 0 else ""
            print(f"  {dim:45s}  {score}{indicator}")

    # Score distribution
    all_scores = []
    for r in results:
        all_scores.extend(v for v in r["scores"].values() if v > 0)
    if all_scores:
        from collections import Counter
        dist = Counter(all_scores)
        total = len(all_scores)
        print("\n--- Score Distribution ---")
        for level in [1, 2, 3, 4]:
            count = dist.get(level, 0)
            pct = count / total * 100
            bar = "#" * int(pct / 2)
            flag = " WARNING >40%" if pct > 40 else ""
            print(f"  {level}: {count:4d} ({pct:5.1f}%) {bar}{flag}")

    # Parse failure rate
    if total_calls > 0:
        fail_pct = total_failures / total_calls * 100
        status = "PASS" if fail_pct < 5 else "WARN" if fail_pct < 10 else "FAIL"
        print(f"\nParse failure rate: {fail_pct:.1f}% [{status}]")

    print(f"\nFull results: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run v2 atomic rubric scoring (research-grounded, halo-free)"
    )
    parser.add_argument(
        "-n", type=int, default=None, help="Number of applicants to score (default: all)"
    )
    parser.add_argument(
        "--amcas-id", type=int, help="Score a single applicant by ID"
    )
    parser.add_argument(
        "--years", type=int, nargs="+", default=[2022, 2023, 2024],
        help="Years to load data for (default: 2022 2023 2024)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip already-scored applicants and continue where you left off",
    )
    parser.add_argument(
        "--id-file",
        type=Path,
        default=None,
        help="JSON file with list of AMCAS IDs to score (e.g., pilot_batch2_ids.json)",
    )
    parser.add_argument(
        "--dims",
        choices=["all", "curated"],
        default="all",
        help="Dimension set to score: 'all' (21 dims) or 'curated' (7 dims, 67%% cost reduction)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt structure without calling API",
    )
    args = parser.parse_args()

    run_scoring(
        n=args.n,
        dry_run=args.dry_run,
        years=args.years,
        amcas_id=args.amcas_id,
        resume=args.resume,
        id_file=args.id_file,
        dims=args.dims,
    )


if __name__ == "__main__":
    main()
