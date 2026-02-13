---
title: "Connect Rubric Scorer to Azure AI Foundry & Refine Prompts"
type: feat
date: 2026-02-13
---

# Connect Rubric Scorer to Azure AI Foundry & Refine Prompts

## Overview

Wire `pipeline/rubric_scorer.py` to a live Azure AI Foundry endpoint (GPT-4.1-mini), run a 10-50 applicant smoke test, audit the data flowing into prompts, and refine the 30-dimension rubric prompts based on the audit findings in `data/rubric_audit.md`.

**Scope:** LLM pipeline connection first; data audit is secondary and informs prompt refinement.

---

## Problem Statement

The rubric scorer (`pipeline/rubric_scorer.py`) defines 30-dimension prompts and a provider-agnostic `llm_call(system, user)` interface — but no LLM provider is connected. The existing `rubric_scores.json` (1,300 applicants) was generated externally with known quality issues:

- **61% zero-rate** on 6 personal quality dimensions (data not reaching LLM, or LLM returning defaults)
- **r > 0.97 multicollinearity** across 8 "personal quality" dims (prompts not differentiating constructs)
- **No `authenticity_and_self_awareness` prompt exists** in `rubric_scorer.py` (line 262-308 only scores 6 PS dimensions, but `config.py:217` lists 7 including `authenticity_and_self_awareness`)
- **Bimodal distributions** suggest 797/1,300 applicants had incomplete text inputs

The pipeline has no Azure AI Foundry SDK, no API keys configured, and `requirements.txt` has no LLM dependencies.

---

## Proposed Solution

### Architecture

```
┌─────────────────┐     ┌───────────────────────┐     ┌──────────────────────┐
│ Raw Excel Files  │────▶│ data_ingestion.py     │────▶│ master_{year}.csv    │
│ (12 files/year)  │     │ (join, normalize)      │     │ (unified dataset)    │
└─────────────────┘     └───────────────────────┘     └──────────┬───────────┘
                                                                  │
                         ┌───────────────────────┐                │
                         │ Text Extraction        │◀───────────────┘
                         │ - Personal Statements  │
                         │ - Secondary Essays     │
                         │ - Experience Records   │
                         └───────────┬───────────┘
                                     │
                         ┌───────────▼───────────┐
                         │ rubric_scorer.py       │
                         │ (30 dimension prompts) │
                         └───────────┬───────────┘
                                     │ llm_call(system, user)
                         ┌───────────▼───────────┐
                    NEW  │ azure_foundry_client.py│
                         │ (ChatCompletionsClient)│
                         │ + JsonSchemaFormat     │
                         └───────────┬───────────┘
                                     │ HTTPS POST
                         ┌───────────▼───────────┐
                         │ Azure AI Foundry       │
                         │ GPT-4.1-mini endpoint  │
                         └───────────┬───────────┘
                                     │
                         ┌───────────▼───────────┐
                         │ data/cache/            │
                         │ rubric_scores_v2.json  │
                         └───────────────────────┘
```

### What Data Hits the Azure Foundry Endpoint

Every API call sends **exactly two strings** to the deployed model:

| Call Type | System Prompt | User Prompt | Data Included | Est. Tokens/Call |
|-----------|--------------|-------------|---------------|-----------------|
| **Experience domain** (x9 per applicant) | `SYSTEM_PROMPT` (198 tokens) | Domain-specific prompt + `{experience_text}` | Exp_Name, Exp_Type, Exp_Desc, hour columns filtered by domain | 300-800 |
| **Personal statement** (x1) | `SYSTEM_PROMPT` (198 tokens) | `PERSONAL_STATEMENT_PROMPT` + full PS text | Full personal statement (~500-2000 words) | 800-3000 |
| **Secondary essays** (x1) | `SYSTEM_PROMPT` (198 tokens) | `SECONDARY_ESSAYS_PROMPT` + concatenated essay text | 6 essay columns concatenated | 600-2500 |

**Per applicant: 11 API calls, ~5,000-25,000 input tokens, ~500-1,000 output tokens.**

**For 50-applicant smoke test: ~550 API calls, ~500K-1.25M input tokens.**

**Sensitive fields that NEVER leave the pipeline (not sent to LLM):**
- `Amcas_ID` (used as dict key, not in prompt text)
- Gender, Age, Race, Citizenship (fairness-only, blocked in config)
- GPA, MCAT scores (structured features, not in rubric prompts)
- Financial data (SES, Pell Grant, Fee Assistance)

**Fields that DO flow into prompts:**
- Experience descriptions (Exp_Name, Exp_Desc, Exp_Type, hours)
- Personal statement full text
- Secondary essay full text (6 essays)

---

## Implementation Plan

### Phase 1: Azure AI Foundry Client (the `llm_call` implementation)

**New file: `pipeline/azure_foundry_client.py`**

```python
"""Azure AI Foundry client: implements the llm_call interface for rubric_scorer."""

import json
import os
import logging
from typing import Any

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    JsonSchemaFormat,
)
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)


def create_foundry_client() -> ChatCompletionsClient:
    """Create Azure AI Foundry chat completions client.

    Requires two environment variables:
      AZURE_FOUNDRY_ENDPOINT  - e.g. https://<resource>.services.ai.azure.com/models
      AZURE_FOUNDRY_KEY       - API key from Azure AI Foundry portal
    """
    endpoint = os.environ["AZURE_FOUNDRY_ENDPOINT"]
    key = os.environ["AZURE_FOUNDRY_KEY"]
    return ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def make_llm_call(client: ChatCompletionsClient) -> callable:
    """Return a llm_call(system, user) -> str function for rubric_scorer."""

    def llm_call(system_prompt: str, user_prompt: str) -> str:
        response = client.complete(
            messages=[
                SystemMessage(content=system_prompt),
                UserMessage(content=user_prompt),
            ],
            temperature=0,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    return llm_call
```

**Tasks:**

- [ ] `pipeline/azure_foundry_client.py` — Create Foundry client with `create_foundry_client()` and `make_llm_call()`
- [ ] Add `AZURE_FOUNDRY_ENDPOINT` and `AZURE_FOUNDRY_KEY` to `infra/.env.example`
- [ ] Add `azure-ai-inference>=1.0.0b9` and `azure-core` to `requirements.txt`
- [ ] Store actual keys in Azure Key Vault (`rmc-triage-kv`) as `AZURE-FOUNDRY-ENDPOINT` and `AZURE-FOUNDRY-KEY`
- [ ] Test: single applicant, single domain call → verify JSON response parses

### Phase 2: Structured Outputs (Schema Enforcement)

Replace raw JSON parsing with Azure AI Foundry's `JsonSchemaFormat` for guaranteed schema compliance.

**Example for experience domains:**

```python
from pydantic import BaseModel, Field

class ExperienceScore(BaseModel, extra="forbid"):
    """Schema for a single experience domain score."""
    score: int = Field(ge=1, le=5, description="Quality/depth score")
    evidence: str = Field(description="1-2 sentence supporting quote")

# In make_llm_call, add response_format parameter:
response = client.complete(
    messages=[...],
    temperature=0,
    max_tokens=1000,
    response_format=JsonSchemaFormat(
        name="experience_score",
        schema=ExperienceScore.model_json_schema(),
        strict=True,
    ),
)
```

**Tasks:**

- [ ] `pipeline/schemas.py` — Define Pydantic models for each prompt output type:
  - `ExperienceScore` (9 experience domains)
  - `PersonalStatementScore` (6 dimensions + evidence)
  - `SecondaryEssayScore` (5 dimensions + evidence)
  - `ResearchScore` (3 fields: depth, publication_quality, num_publications + evidence)
- [ ] Update `make_llm_call()` to accept an optional `response_schema` parameter
- [ ] Update `rubric_scorer.py` scoring functions to pass schemas
- [ ] Test: verify 100% schema compliance on 10 applicants

### Phase 3: Smoke Test Script (10-50 Applicants)

**New file: `pipeline/run_smoke_test.py`**

```python
"""Smoke test: score 10-50 applicants via Azure AI Foundry and compare to v1 cache."""

import json
import logging
import sys
from pathlib import Path

from pipeline.config import CACHE_DIR, PROCESSED_DIR, TRAIN_YEARS, TEST_YEAR
from pipeline.data_ingestion import (
    load_applicants, load_experiences,
    load_personal_statements, load_secondary_applications,
)
from pipeline.rubric_scorer import score_batch
from pipeline.azure_foundry_client import create_foundry_client, make_llm_call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_smoke_test(n_applicants: int = 10):
    # Load data
    applicants = load_applicants(years=[TEST_YEAR])
    experiences = load_experiences(years=[TEST_YEAR])
    ps_df = load_personal_statements(years=[TEST_YEAR])
    sec_df = load_secondary_applications(years=[TEST_YEAR])

    # Sample applicants
    sample_ids = applicants["Amcas_ID"].dropna().unique()[:n_applicants].tolist()
    logger.info("Scoring %d applicants: %s", len(sample_ids), sample_ids)

    # Build text lookups
    ps_dict = {}
    for _, row in ps_df.iterrows():
        aid = row.get("Amcas_ID")
        text = row.get("personal_statement", "")
        if aid and text:
            ps_dict[int(aid)] = str(text)

    sec_dict = {}  # TODO: concatenate secondary essay columns per applicant

    # Connect to Foundry
    client = create_foundry_client()
    llm_call = make_llm_call(client)

    # Score
    results_df = score_batch(
        applicant_ids=sample_ids,
        experiences_df=experiences,
        personal_statements=ps_dict,
        secondary_texts=sec_dict,
        llm_call=llm_call,
        n_passes=1,
    )

    # Save results
    out_path = CACHE_DIR / "rubric_scores_v2_smoke.json"
    results_dict = {}
    for _, row in results_df.iterrows():
        aid = str(int(row["Amcas_ID"]))
        results_dict[aid] = {k: v for k, v in row.items() if k != "Amcas_ID"}
    with open(out_path, "w") as f:
        json.dump(results_dict, f, indent=2, default=str)

    logger.info("Saved %d scored applicants to %s", len(results_dict), out_path)

    # Compare to v1 if available
    v1_path = CACHE_DIR / "rubric_scores.json"
    if v1_path.exists():
        compare_v1_v2(v1_path, out_path, sample_ids)


def compare_v1_v2(v1_path, v2_path, sample_ids):
    """Print side-by-side comparison of v1 vs v2 scores."""
    with open(v1_path) as f:
        v1 = json.load(f)
    with open(v2_path) as f:
        v2 = json.load(f)

    for aid in sample_ids:
        aid_str = str(aid)
        if aid_str in v1 and aid_str in v2:
            print(f"\n=== Applicant {aid_str} ===")
            for dim in sorted(v1[aid_str].keys()):
                s1 = v1[aid_str].get(dim, "N/A")
                s2 = v2[aid_str].get(dim, "N/A")
                marker = " **" if s1 != s2 else ""
                print(f"  {dim:45s}  v1={s1}  v2={s2}{marker}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_smoke_test(n)
```

**Tasks:**

- [ ] `pipeline/run_smoke_test.py` — Script to score N applicants and compare to v1 cache
- [ ] Build `sec_dict` from secondary application columns (concatenate 6 essay columns per applicant)
- [ ] Run: `python -m pipeline.run_smoke_test 10`
- [ ] Verify: JSON responses parse, scores are 1-5 (not 0), evidence strings present
- [ ] Compare v1 vs v2: identify scoring drift, zero-rate differences

### Phase 4: Prompt Refinement

Based on the rubric audit findings (`data/rubric_audit.md`), these are the specific prompt issues to fix:

#### Issue 1: Missing `authenticity_and_self_awareness` Dimension

**Current state:** `rubric_scorer.py:262-308` defines `PERSONAL_STATEMENT_PROMPT` scoring 6 dimensions, but `config.py:217-225` lists 7 PS dims including `authenticity_and_self_awareness`. The existing cache has scores for it, meaning it was scored by a different system.

**Fix:** Add `authenticity_and_self_awareness` to the personal statement prompt.

**Refined prompt addition (insert after `writing_quality` in PERSONAL_STATEMENT_PROMPT):**

```
2. authenticity_and_self_awareness (1-5): Does the applicant show genuine
   self-knowledge — not a polished performance? Look for: honest acknowledgment
   of mistakes or limitations, awareness of their own biases or blind spots,
   evidence they've reflected on WHY they think the way they do (not just WHAT
   they think). Distinguish between self-serving "vulnerability" and genuine
   introspection. A score of 5 requires the reader to believe this person truly
   knows themselves.
```

#### Issue 2: Multicollinearity in Personal Quality Dims (r > 0.97)

**Root cause:** The prompts for `authenticity_and_self_awareness`, `maturity_and_reflection`, `motivation_depth`, and `intellectual_curiosity` are too vague — they all converge on "is this a thoughtful person."

**Fix: Sharpen discriminant cues in each prompt.** Make each dimension ask for **specific, mutually exclusive evidence:**

| Dimension | Current Cue (Vague) | Refined Cue (Discriminant) |
|-----------|--------------------|-----------------------------|
| `writing_quality` | "Clarity, organization, coherence" | Keep as-is (already distinct — about form, not content) |
| `authenticity_and_self_awareness` | (missing) | "Honest self-knowledge. Did they admit a real limitation? Do they know their blind spots?" |
| `mission_alignment` | "Alignment with Rush's mission" | "SPECIFIC to Rush. Name a community, population, or program. Generic 'I want to help people' = 2." |
| `adversity_resilience` | "Perseverance through challenges" | "What OBSTACLE did they face? What ACTION did they take? No obstacle = 1, not 3." |
| `motivation_depth` | "Why medicine, is it genuine" | "Can they name the MOMENT their decision was tested and they chose to persist? Vague 'calling' = 2." |
| `intellectual_curiosity` | "Love of learning beyond requirements" | "Did they pursue knowledge NO ONE ASKED THEM TO? Self-directed projects, readings, questions — not coursework." |
| `maturity_and_reflection` | "Emotional intelligence, self-awareness" | "Did their THINKING CHANGE? Point to a belief they held, then revised. Static worldview = 2 max." |

**Exact refined `PERSONAL_STATEMENT_PROMPT` (replace lines 262-308):**

```python
PERSONAL_STATEMENT_PROMPT = """Score the following dimensions from this applicant's personal statement.

Read as a human reviewer: looking for substance over polish. A plainly written
statement with genuine content scores higher than an eloquent statement that
says nothing specific.

DIMENSIONS TO SCORE (each asks for DIFFERENT evidence — do not let one
dimension's score influence another):

1. writing_quality (1-5): FORM ONLY. Clarity, organization, paragraph transitions,
   grammar. Ignore content quality — this dimension measures communication skill.
   A 5 reads effortlessly. A 2 has unclear antecedents or disorganized structure.

2. authenticity_and_self_awareness (1-5): Does the applicant show genuine
   self-knowledge? Look for: honest acknowledgment of a real limitation or mistake,
   awareness of their own biases or blind spots, evidence they reflected on WHY they
   think the way they do. Self-serving "vulnerability" (a weakness that's really a
   strength) = 2. Genuine introspection = 4-5.

3. mission_alignment_service_orientation (1-5): SPECIFIC alignment with Rush's
   mission of serving diverse urban communities. Must name a community, population,
   neighborhood, or structural barrier. Generic "I want to help underserved patients"
   without specifics = 2. Demonstrated sustained work in a specific community = 4-5.

4. adversity_resilience (1-5): Evidence of perseverance through a SPECIFIC obstacle.
   Must identify: (a) what the obstacle was, (b) what action they took. No obstacle
   described = 1. Obstacle described but no action = 2. Quiet resilience counts — do
   NOT require trauma.

5. motivation_depth (1-5): Can they name a SPECIFIC MOMENT their decision to pursue
   medicine was tested — and they chose to persist? "I've always wanted to be a doctor"
   = 2. A pivotal experience that changed or deepened their commitment = 4-5.

6. intellectual_curiosity (1-5): Evidence of SELF-DIRECTED learning beyond what was
   required. Independent reading, questions pursued outside coursework, cross-disciplinary
   exploration. Listing courses taken = 1. Describing a question that kept them up at
   night = 4-5.

7. maturity_and_reflection (1-5): Did their THINKING CHANGE? Point to a belief they
   held, then revised based on experience. Static worldview with no evolution = 2 max.
   Evidence of growth from a specific experience = 4-5.

PERSONAL STATEMENT:
{personal_statement}

Respond with JSON:
{{
  "writing_quality": <1-5>,
  "authenticity_and_self_awareness": <1-5>,
  "mission_alignment_service_orientation": <1-5>,
  "adversity_resilience": <1-5>,
  "motivation_depth": <1-5>,
  "intellectual_curiosity": <1-5>,
  "maturity_and_reflection": <1-5>,
  "evidence": "<1-2 sentence summary of the strongest signal in this statement>"
}}"""
```

#### Issue 3: `meaningful_vs_checkbox` Has No Prompt

**Current state:** The dimension appears in `rubric_scores.json` but has no prompt in `rubric_scorer.py`. It's a meta-assessment that correlates r>0.98 with 7 other dims.

**Fix:** Do NOT add a separate prompt. Instead, fold it into the experience domain prompts as a **sub-criterion**. Add to each experience domain prompt:

```
CHECKBOX TEST: If this reads like a list of activities with no reflection,
depth, or personal connection — the applicant checked a box. Score ≤ 2
regardless of hours logged.
```

This makes each experience domain score implicitly penalize checkbox behavior rather than having a redundant 31st dimension.

#### Issue 4: 61% Zero-Rate on Personal Quality Dims

**Root cause:** 797/1,300 applicants have zeros across `authenticity_and_self_awareness`, `motivation_depth`, `intellectual_curiosity`, `maturity_and_reflection`, `meaningful_vs_checkbox`, `personal_attributes_insight`, `reflection_depth`, `healthcare_experience_quality` simultaneously.

**Hypothesis:** These applicants had no personal statement or secondary essay text available when the v1 scores were generated.

**Validation step (smoke test):**

```python
# In run_smoke_test.py — check which applicants have empty text
for aid in sample_ids:
    ps = ps_dict.get(aid, "")
    sec = sec_dict.get(aid, "")
    print(f"{aid}: PS={len(ps)} chars, SEC={len(sec)} chars")
```

**Fix if confirmed:** The `score_personal_statement()` and `score_secondary_essays()` functions already return 0 for empty text (lines 526-534, 565-570). The fix is upstream — ensure `build_unified_dataset()` actually joins PS/secondary text for all applicants.

#### Issue 5: Experience Domain Prompts Could Be Sharper

**Current prompts are good** but share a weakness: they list reviewer questions without anchoring specific score levels. The research domain prompt (lines 182-207) is the best — it includes `SCORING GUIDANCE` with explicit 1-5 anchors.

**Fix: Add explicit score anchors to ALL experience domain prompts.** Example for `direct_patient_care`:

```
SCORING GUIDANCE:
  1 = No direct patient interaction, or only administrative/front desk role
  2 = Brief or shallow patient contact (e.g., one summer, limited reflection)
  3 = Regular patient interaction in one setting with some reflection
  4 = Sustained patient care across settings, clear growth, diverse populations
  5 = Deep, prolonged patient care with progressive responsibility and transformative reflection
```

**Tasks:**

- [ ] Add `authenticity_and_self_awareness` to `PERSONAL_STATEMENT_PROMPT`
- [ ] Replace vague cues with discriminant cues in all 7 PS dimensions (see table above)
- [ ] Add `SCORING GUIDANCE` anchors to all 9 experience domain prompts (match research domain format)
- [ ] Add `CHECKBOX TEST` sub-criterion to experience domain prompts
- [ ] Remove `meaningful_vs_checkbox` from `RUBRIC_FEATURES_FINAL` in config.py (redundant)
- [ ] Validate: run smoke test before/after prompt changes, compare multicollinearity

### Phase 5: Data Audit (Pipeline Integrity Check)

Audit the flow from raw Excel to the text that hits the Azure endpoint.

**Tasks:**

- [ ] Verify PS text join: count applicants with non-empty personal statements per year
- [ ] Verify secondary essay join: count applicants with non-empty essay text per year
- [ ] Verify experience text extraction: for 10 applicants, manually compare `gather_experience_text()` output against raw Excel
- [ ] Check for text truncation: are any PS/essay texts cut off by Excel column limits?
- [ ] Validate `DOMAIN_EXP_TYPES` mapping: are any experience types falling through unmapped?
- [ ] Count applicants with zero experience records (should score 1 on all domains, not 0)

---

## Acceptance Criteria

### Functional Requirements

- [ ] `python -m pipeline.run_smoke_test 10` runs end-to-end, producing `rubric_scores_v2_smoke.json`
- [ ] All 30 rubric dimensions have scores 1-5 (never 0) for applicants with available text
- [ ] JSON responses from Azure Foundry match Pydantic schemas 100% of the time
- [ ] Prompt changes reduce PS dimension pairwise correlation from r>0.97 to r<0.85
- [ ] Zero-rate on personal quality dims drops from 61% to match the actual rate of missing PS text

### Non-Functional Requirements

- [ ] API keys stored in environment variables, never in code
- [ ] Single applicant scores in <30 seconds (11 sequential API calls)
- [ ] Smoke test for 50 applicants completes in <30 minutes
- [ ] All API calls logged with applicant ID, dimension, token count, latency

---

## Dependencies & Prerequisites

| Dependency | Status | Action Needed |
|-----------|--------|---------------|
| Azure AI Foundry endpoint | Deployed | Get endpoint URL and API key from portal |
| GPT-4.1-mini model | Deployed | Confirm model name in deployment |
| `azure-ai-inference` SDK | Not installed | `pip install azure-ai-inference` |
| `pydantic` | Not installed | `pip install pydantic` (for structured outputs) |
| Raw Excel data (2024) | Available | In `data/raw/2024/` |
| `rubric_scores.json` (v1) | Available | In `data/cache/` — 1,300 applicants for comparison |

---

## Cost Estimate (Smoke Test)

| Parameter | Value |
|-----------|-------|
| Model | GPT-4.1-mini |
| Applicants | 50 |
| API calls | 550 (11 per applicant) |
| Input tokens | ~750K |
| Output tokens | ~30K |
| Price (input) | ~$0.30 (at $0.40/1M tokens) |
| Price (output) | ~$0.05 (at $1.60/1M tokens) |
| **Total smoke test** | **~$0.35** |

Full 17K production run (Batch API, 50% discount): ~$20

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Azure endpoint quota limits | Medium | Blocks smoke test | Request quota increase; start with 10 applicants |
| Prompt changes degrade score quality | Low | Bad model features | Compare v2 scores against human reviewer labels |
| 61% zeros are real (not missing data) | Low | Prompt changes won't fix it | Smoke test will reveal actual text availability |
| Structured outputs reject valid scores | Low | Scoring failures | Test schemas against v1 response formats first |

---

## Files Changed

| File | Action | Description |
|------|--------|-------------|
| `pipeline/azure_foundry_client.py` | **Create** | Foundry client + `llm_call` factory |
| `pipeline/schemas.py` | **Create** | Pydantic models for structured outputs |
| `pipeline/run_smoke_test.py` | **Create** | Smoke test script with v1/v2 comparison |
| `pipeline/rubric_scorer.py` | **Edit** | Refine all prompts (PS, experience domains) |
| `pipeline/config.py` | **Edit** | Remove `meaningful_vs_checkbox` from `RUBRIC_FEATURES_FINAL` |
| `requirements.txt` | **Edit** | Add `azure-ai-inference`, `pydantic` |
| `infra/.env.example` | **Edit** | Add `AZURE_FOUNDRY_ENDPOINT`, `AZURE_FOUNDRY_KEY` |

---

## Exact Prompts — Before vs After

### Personal Statement: Before (current rubric_scorer.py:262-308)

Scores 6 dimensions. Missing `authenticity_and_self_awareness`. Vague cues lead to r>0.97 correlation between dimensions.

### Personal Statement: After (refined)

Scores 7 dimensions. Each dimension asks for **mutually exclusive evidence**:
- `writing_quality` → FORM only (grammar, structure)
- `authenticity_and_self_awareness` → Admits real limitation? Knows blind spots?
- `mission_alignment` → Names SPECIFIC community/population/program
- `adversity_resilience` → Names SPECIFIC obstacle + ACTION taken
- `motivation_depth` → Names SPECIFIC moment decision was TESTED
- `intellectual_curiosity` → SELF-DIRECTED learning (not coursework)
- `maturity_and_reflection` → Belief they CHANGED (not static worldview)

### Experience Domains: Before

9 domain prompts with reviewer questions but no score anchors (except research).

### Experience Domains: After

Same 9 domains + explicit `SCORING GUIDANCE` (1-5 anchors) + `CHECKBOX TEST` sub-criterion.

### Secondary Essays: No Changes

The secondary essay prompt is already well-structured with 5 discriminant dimensions.

---

## References

### Internal
- [rubric_scorer.py](pipeline/rubric_scorer.py) — Current prompts and scoring functions
- [config.py](pipeline/config.py) — Feature lists, dimension enums
- [data/rubric_audit.md](data/rubric_audit.md) — Statistical audit of v1 rubric scores
- [data/cache/rubric_scores.json](data/cache/rubric_scores.json) — v1 scored data (1,300 applicants)
- [infra/.env.example](infra/.env.example) — Environment variable template

### External
- [Azure AI Inference SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-inference-readme) — ChatCompletionsClient docs
- [Structured Outputs on Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/model-inference/how-to/use-structured-outputs) — JsonSchemaFormat usage
- [Azure AI Foundry Batch API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/batch) — For future 17K production runs (uses OpenAI SDK)
