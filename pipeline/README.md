# RMC Admissions Triage Pipeline — v2 Architecture

**Production scorer**: Research-grounded atomic prompts (1 dimension per API call)
**Scale**: 1-4 (no neutral midpoint)
**Status**: v2 atomic scoring pipeline

---

## Quick Start

### 1. Score Applicants with LLM Rubric

```bash
# Score all applicants (all years: 2022, 2023, 2024)
python -m pipeline.run_rubric_scoring_v2

# Score specific years
python -m pipeline.run_rubric_scoring_v2 --years 2024

# Score first 10 applicants (for testing)
python -m pipeline.run_rubric_scoring_v2 -n 10

# Score a single applicant by ID
python -m pipeline.run_rubric_scoring_v2 --amcas-id 13149516 -n 1

# Resume from where you left off (skip already-scored)
python -m pipeline.run_rubric_scoring_v2 --resume

# Print prompt structure without calling API
python -m pipeline.run_rubric_scoring_v2 --dry-run
```

**Output**: `data/cache/rubric_scores_v2.json`

---

### 2. Validate Scores

```bash
python -m pipeline.validate_scores data/cache/rubric_scores_v2.json
```

**Checks**:
- Score distribution (no single level > 40%)
- Inter-dimension correlation (target: r < 0.60 for PS dimensions)
- Zero-rate analysis (should be < 10% if text available)
- Parse failure rate (should be < 10%)

---

### 3. Train Model with v2 Scores

```python
from pipeline.data_preparation import prepare_dataset
from pipeline.feature_engineering import FeaturePipeline
from pipeline.config import CACHE_DIR

# Load data
df = prepare_dataset(years=[2022, 2023, 2024])

# Build features (includes v2 rubric scores)
feature_pipe = FeaturePipeline(
    include_rubric=True,
    rubric_path=CACHE_DIR / "rubric_scores_v2.json"
)
features_df = feature_pipe.fit_transform(df)

# Save fitted pipeline
feature_pipe.save(MODELS_DIR / "feature_pipeline_v2.joblib")

# Train your XGBoost model using features_df
# ...
```

---

## Architecture

### Scoring Pipeline (v2)

```
run_rubric_scoring_v2.py
  ├─→ data_ingestion.py (load PS, secondary, experiences)
  ├─→ rubric_scorer_v2.py (atomic scoring orchestrator)
  │    ├─→ score_personal_statement() → 7 API calls
  │    ├─→ score_secondary_essays() → 5 API calls
  │    └─→ score_all_experiences() → up to 9 API calls
  ├─→ rubric_prompts_v2.py (research-grounded prompts)
  │    ├─→ PS_DIMENSIONS (7 atomic prompts)
  │    ├─→ SECONDARY_DIMENSIONS (5 atomic prompts)
  │    └─→ EXPERIENCE_PROMPTS (9 atomic prompts)
  └─→ llm_client.py (Azure OpenAI with JSON mode + retry)
```

**Total**: Up to 21 API calls per applicant
**Duration**: ~8-12 seconds per applicant (with retry)

---

### Feature Engineering (v2)

```
FeaturePipeline (sklearn-style fit/transform)
  ├─→ fit(train_df) — learns imputation medians from training data only
  ├─→ transform(test_df) — applies fitted transformations consistently
  ├─→ save() / load() — persist fitted pipeline for scoring new cycles
  └─→ Handles v2 rubric JSON format automatically
```

**Features extracted**:
- 11 numeric features (hours, languages, parent education, etc.)
- 10 binary features (first-gen, disadvantaged, SES, Pell, etc.)
- 7 engineered composites (volunteer hours, adversity count, grit index, etc.)
- 21 LLM rubric dimensions (7 PS + 5 secondary + 9 experience)
- 1 binary flag (rubric_scored_flag)

**Total**: ~50 features per applicant

---

## v2 Rubric Dimensions (21 total)

### Personal Statement (7 dimensions)
- `writing_quality` — Form, not content (clarity, organization, grammar)
- `authenticity_and_self_awareness` — Genuine self-knowledge, not performed vulnerability
- `mission_alignment_service_orientation` — Concrete commitment to serving diverse communities
- `adversity_resilience` — Specific obstacle + specific action (quiet resilience counts)
- `motivation_depth` — Tested and evolved commitment (not static calling)
- `intellectual_curiosity` — Self-directed learning beyond requirements
- `maturity_and_reflection` — Evidence that thinking changed

### Secondary Essays (5 dimensions)
- `personal_attributes_insight` — Self-awareness about strengths/weaknesses
- `adversity_response_quality` — What they DID in challenging situation
- `reflection_depth` — Quality of changed thinking
- `healthcare_experience_quality` — Nuanced view of clinical realities
- `research_depth` — Scholarly engagement evident in responses

### Experiences (9 dimensions)
- `direct_patient_care_depth_and_quality` — Hands-on patient interaction
- `research_depth_and_quality` — Scientific inquiry and methodology
- `community_service_depth_and_quality` — Sustained civic engagement
- `leadership_depth_and_quality` — Initiative, impact, developing others
- `teaching_mentoring_depth_and_quality` — Pedagogical experience
- `clinical_exposure_depth_and_quality` — Shadowing and observation
- `clinical_employment_depth_and_quality` — Paid clinical work
- `advocacy_policy_depth_and_quality` — Systems-level change work
- `global_crosscultural_depth_and_quality` — Cross-cultural competency

---

## Scoring Rubric (All Dimensions)

**Scale**: 1-4 (no neutral midpoint forces commitment)

- **4 = Exceptional** — Deep, sustained, progressive; transformative reflection
- **3 = Substantive** — Clear evidence with depth; meets strong applicant bar
- **2 = Checkbox** — Listed without reflection; hours logged but no genuine engagement
- **1 = Absent** — No meaningful evidence in text (NOT "this person is deficient")

**Key principle**: Score 1 means "no evidence in this text," not "deficiency in the applicant."

---

## Research Grounding

v2 prompts are based on:

1. **LLM-Rubric** (Hashemi et al., ACL 2024)
   - Atomic scoring (1 dimension per call) eliminates halo effects
   - v1 had r > 0.97 correlation between dimensions → model couldn't distinguish them
   - 1-4 scale with no neutral midpoint → forces evaluator to commit

2. **AutoSCORE** (arxiv:2509.21910)
   - Evidence extraction BEFORE scoring
   - Prompts explicitly ask for `evidence_extracted` field
   - Reduces hallucination and provides audit trail

3. **G-Eval** (Liu et al., EMNLP 2023)
   - Chain-of-Thought + form-filling paradigm
   - Prompts include evaluation steps and rubric anchors
   - Structured JSON output for direct use as model features

4. **Rulers** (arxiv:2601.08654)
   - Executable rubrics > prompt engineering alone
   - Prompts include checkbox tests ("Is there evidence of X?") and signal detection

---

## File Structure

```
pipeline/
├── config.py                      # Dimension lists, paths, constants
├── llm_client.py                  # Unified Azure OpenAI client (JSON mode + retry)
├── rubric_prompts_v2.py           # 21 atomic prompts (research-grounded)
├── rubric_scorer_v2.py            # Scoring orchestrator
├── run_rubric_scoring_v2.py       # Production CLI runner
├── validate_scores.py             # Score quality validation
├── data_ingestion.py              # Load xlsx files, build text dicts
├── data_preparation.py            # Clean and normalize data
├── feature_engineering.py         # FeaturePipeline class (fit/transform)
└── score_pipeline.py              # Score-only pipeline for new cycles
```

---

## Configuration (.env)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

---

## Output Format

### rubric_scores_v2.json Structure

```json
{
  "13149516": {
    "scores": {
      "writing_quality": 3,
      "authenticity_and_self_awareness": 4,
      "mission_alignment_service_orientation": 3,
      "direct_patient_care_depth_and_quality": 4,
      "research_depth_and_quality": 2,
      ...
    },
    "details": {
      "writing_quality": {
        "evidence_extracted": "Clear thesis with logical progression...",
        "reasoning": "Well-organized statement with minor issues..."
      },
      ...
    },
    "metadata": {
      "total_calls": 21,
      "parse_failures": 0,
      "elapsed_seconds": 9.2,
      "scorer_version": "v2_atomic_research_grounded"
    }
  },
  ...
}
```

---

---

## Performance

Based on smoke tests (N=10):

- **Avg time per applicant**: 8-12 seconds (21 API calls with retry)
- **Parse failure rate**: < 5% (JSON mode + validation)
- **Score distribution**: Balanced (no level > 40%)
- **PS dimension correlations**: r < 0.60 (eliminates v1's r > 0.97 halo effect)

---

## Troubleshooting

### "No rubric scores found"

Check that scoring has run:
```bash
ls -lh data/cache/rubric_scores_v2.json
```

If missing, run scoring:
```bash
python -m pipeline.run_rubric_scoring_v2 -n 10
```

### "Parse failure rate > 10%"

Check LLM client configuration:
```python
from pipeline.llm_client import create_llm_call
llm_call = create_llm_call()
response = llm_call("You are a test.", "Respond with JSON: {\"test\": 1}")
print(response)  # Should be valid JSON
```

### "Feature columns mismatch"

Check fitted pipeline feature list:
```python
from pipeline.feature_engineering import FeaturePipeline
from pipeline.config import MODELS_DIR

pipe = FeaturePipeline.load(MODELS_DIR / "feature_pipeline_v2.joblib")
print("Features:", len(pipe.feature_columns_))
print("First 10:", pipe.feature_columns_[:10])
```

---

## Next Steps

1. **Score your full dataset**: `python -m pipeline.run_rubric_scoring_v2`
2. **Validate output**: `python -m pipeline.validate_scores data/cache/rubric_scores_v2.json`
3. **Train model**: Use `FeaturePipeline` to extract features, train XGBoost
4. **Deploy**: Use `score_pipeline.py` for production scoring

---

## Research Citations

- Hashemi et al. (2024). LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation of Natural Language Texts. *ACL 2024*.
- Liu et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. *EMNLP 2023*.
- arxiv:2509.21910. AutoSCORE: Automated Evidence Extraction for Evaluation.
- arxiv:2601.08654. Rulers: Making Executable Rubrics for Language Model Evaluation.
