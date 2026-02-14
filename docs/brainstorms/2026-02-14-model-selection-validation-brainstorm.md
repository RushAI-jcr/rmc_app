# Brainstorm: Model Selection & Validation for Rubric Scoring Pipeline

**Date:** 2026-02-14
**Status:** Draft

---

## What We're Building

A validation framework to confirm GPT-4.1 is the right model for the rubric scoring pipeline before scaling to the full applicant cohort. The pipeline scores 21 atomic dimensions (1-4 scale) per applicant. We have human reviewer ground truth with two separate measures to validate against.

## Why This Approach

### Decision: Stay with GPT-4.1 + Add Validation Layer

**Rejected alternatives:**
- **Reasoning models (o1/o3/DeepSeek R1):** No temperature control (fixed internally at 1.0). Research confirms these are too variable for consistent scoring tasks. DeepSeek-R1 is documented as "sensitive to prompts" and few-shot examples degrade its performance.
- **GPT-4o with Structured Outputs:** Better JSON schema enforcement (100% compliance), but requires migration effort. GPT-4.1's JSON mode + parsing is working. Worth revisiting only if parse failures become an issue.
- **Multi-model ensemble (GPT-4.1 + Claude):** Best reliability but 2x cost for 21 calls/applicant. Overkill before we've measured current performance.

**Why GPT-4.1 is a reasonable default:**
- Temperature 0.0 + seed 42 = maximum reproducibility
- Already deployed on Azure with enterprise compliance
- 21 atomic prompts based on peer-reviewed research (LLM-Rubric ACL 2024, AutoSCORE, G-Eval)
- No evidence of problems yet; validate before optimizing

## Key Decisions

1. **Model:** GPT-4.1 on Azure (current setup, no change)
2. **Validation target:** Both human scores — Application_Review_Score (0-25 holistic) AND Service_Rating (1-4 service-specific)
3. **Score=0 is real:** Include all 0-scored applicants in the validation set (not missing data)
4. **Scale mapping needed:** 21 LLM dimensions (1-4 each, sum range 21-84) must be mapped to the 0-25 Application_Review_Score scale

## Human Ground Truth Data

Two separate human reviewer measures (n ~ 600 applicants):

| Measure | Scale | What It Captures |
|---------|-------|------------------|
| Application_Review_Score | 0-25 | Overall holistic assessment |
| Service_Rating | Lacking (1) / Adequate (2) / Significant (3) / Exceptional (4) | Service-specific dimension |

**Distribution of Service_Rating:**
- Lacking/Does Not Meet (1): ~120 applicants
- Adequate (2): ~130 applicants
- Significant (3): ~230 applicants
- Exceptional (4): ~100 applicants

**Notable pattern:** Score boundaries overlap across categories (e.g., Application_Review_Score=12 can be Lacking, Adequate, or Significant). This reflects natural human judgment variance and is expected.

## Resolved Questions

1. **Scale mapping strategy:** Use **Spearman rank-order correlation** — don't try to match exact scores. Verify the LLM ranks applicants in the same order as humans. Avoids the need for arbitrary scale transformations.

2. **Success criteria:** Target **ICC > 0.8** (strong agreement). LLM and humans should largely agree, suitable for screening use. If below 0.8, investigate specific disagreement patterns before switching models.

## Open Questions

1. **Which LLM dimensions map to Service_Rating?** Need to determine which of the 21 dimensions correspond to the "service" construct the human raters evaluated. Likely candidates: `community_service_depth_and_quality`, `direct_patient_care_depth_and_quality`, `mission_alignment_service_orientation`.

2. **Validation sample size:** Score all ~600 applicants with the LLM, or validate on a subset first?

## Research Supporting This Approach

- **Temperature 0.0** is the single most impactful setting for scoring consistency
- **1-4 scales** (no midpoint) outperform 0-10 for LLM-human agreement (arXiv:2601.03444)
- **Evidence extraction before scoring** improves reliability (already implemented in v2 pipeline)
- **Chain-of-thought + rubrics** enhances accuracy vs. CoT alone (ScienceDirect 2024)
- **Fine-tuned models** can achieve ICC=0.972 (Wiley BJET), but base models with good prompts are often sufficient
- **Ensemble voting** (3-5 runs, majority vote) reduces max error ~3 percentage points — useful as a fallback if initial validation shows variance

## Next Steps

1. Resolve open questions above
2. Create a validation plan (run LLM scoring → compare to human scores)
3. Analyze results: ICC, Spearman correlation, confusion matrix for Service_Rating
4. Decide: ship as-is, add ensemble voting, or switch models
