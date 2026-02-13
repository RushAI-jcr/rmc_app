---
date: 2026-02-13
topic: reviewer-experience-and-feedback-loop
---

# Reviewer Experience & Annual Feedback Loop

## What We're Building

A triage interface designed for non-data-scientist medical school review committee members. Reviewers see an AI-generated score (0-25) with a structured rubric scorecard that mirrors how they already evaluate applicants — not SHAP charts or model internals. The system filters ~17K AMCAS applications down to ~4-5K for human review (Tier 2 + Tier 3 only). When the AI gets it wrong, reviewers flag the error with a reason. Flags accumulate all cycle and feed into an annual retrain to improve the model year over year.

## Why This Approach

**Rubric scorecard over SHAP:** Reviewers think in dimensions (Volunteering: 4/5, Clinical: 3/5, Grit: 5/5). SHAP values like "+1.3 from Exp_Hour_Volunteer_Med" mean nothing to them. The rubric scorecard uses the same LLM-scored dimensions already in the system, presented as a familiar grid.

**Flag-as-incorrect over tier overrides:** Tier overrides create a second scoring system that's hard to reconcile with model predictions. Flags are simpler — "this is wrong because X" — and the reasons surface systematic blind spots (e.g., "30% of flags say volunteer work is undervalued" → adjust feature engineering).

**Annual retrain over mid-cycle:** Keeps the workflow simple and predictable. One retrain before each cycle. No model drift mid-cycle that could confuse reviewers.

## Key Decisions

- **Explainability = Rubric Scorecard**: Structured grid of LLM-scored dimensions (1-5 scale), grouped by reviewer priority: Volunteering & Community, Clinical Experience, Grit/Resilience, Mission Alignment, Research. No SHAP, no model jargon.
- **Review queue = Tier 2 + Tier 3 only**: Human reviewers never see Tier 0 ("Will Not Likely Interview") or Tier 1 ("Committee Review" — borderline, held for escalation). Target: 4-5K applicants from 17K pool.
- **Feedback = "Flag as Incorrect" + reason**: Reviewers click a flag button and select from:
  - Undervalued volunteer/community work
  - Undervalued clinical experience
  - Missed grit/adversity indicators
  - Overvalued — application weaker than score suggests
  - Other (free text)
- **Model improvement = Annual retrain**: At end of each cycle, merge flags + interview outcomes as new training data. Retrain, run fairness audit, compare old vs new, deploy.
- **No SHAP in reviewer UI**: SHAP remains available in admin/data-science view but is hidden from the reviewer-facing scorecard.

## Rubric Scorecard Dimensions (Reviewer-Facing)

Grouped by reviewer priority:

**Volunteering & Community Engagement**
- Volunteering Depth (1-5)
- Community Service Depth (1-5)

**Clinical Experience**
- Direct Patient Care Depth (1-5)
- Clinical Experience Depth (1-5)

**Grit / Resilience**
- Adversity & Resilience (1-5)
- First-Gen / Disadvantaged indicators (Yes/No badges)

**Mission Alignment**
- Mission Alignment & Service Orientation (1-5)
- Writing Quality (1-5)

**Research & Leadership**
- Research Depth & Output (1-5)
- Leadership Depth & Progression (1-5)

**Summary**
- Personal Attributes Insight (1-5, from secondary essays)
- Overall AI Score: X/25 — Tier badge (color)

## Feedback Loop: Annual Retrain Pipeline

```
End of Cycle
    │
    ▼
Export reviewer flags ──→ flags_2026.json
    │                     {amcas_id, flag_reason, reviewer_id, timestamp}
    │
    ▼
Merge with outcomes ───→ outcomes_2026.csv
    │                     {amcas_id, interviewed: bool, admitted: bool}
    │
    ▼
Combine with historical ─→ training_data_2022_2026.csv
    │                       (all years, all decisions, all flags)
    │
    ▼
Retrain pipeline ────────→ new models (Plan A + Plan B)
    │
    ▼
Compare old vs new ──────→ bakeoff + fairness audit
    │
    ▼
Deploy if improved ──────→ production for next cycle
```

**Flag analysis** (pre-retrain):
- Aggregate flag reasons by category
- If >20% of flags cite the same reason → investigate feature engineering gap
- Example: "Undervalued volunteer work" at 35% → check Community_Engaged_Ratio weighting, consider adding LLM re-scoring prompt adjustments

## What Changes in Current System

| Component | Current State | Target State |
|---|---|---|
| Scorecard page | SHAP horizontal bars + rubric JSON dump | Clean rubric grid grouped by reviewer priorities |
| Review queue | Shows all tiers, all applicants | Only Tier 2 + Tier 3, sorted by confidence |
| Decision buttons | Interview / Hold / Flag | **Flag as Incorrect** (+ reason picker) or **Confirm Score** |
| Data storage | In-memory JSON dict | Per-cycle flag files (JSON), exportable for retrain |
| Pipeline CLI | `run_pipeline` (one-shot) | Add `--retrain-with-feedback` flag for annual retrain |
| Dashboard stats | Tier distribution only | + Flag summary (reasons breakdown, count, % of reviewed) |

## Open Questions

- Should Tier 1 ("Committee Review") be visible to senior reviewers or a separate escalation queue?
- What's the minimum number of flags needed before a retrain is meaningful? (Likely 50+ to affect model behavior)
- Should the flag reason list be configurable per cycle, or fixed?
- Interview outcomes — does the committee record these in a separate system we'd need to import, or can the tool capture them directly?

## Next Steps

→ Implement the rubric scorecard UI (replace SHAP view for reviewers)
→ Build the flag-as-incorrect flow (button + reason picker + persistence)
→ Add `--retrain-with-feedback` to pipeline CLI
→ Update review queue to filter Tier 0 and Tier 1
