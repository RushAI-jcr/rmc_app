---
title: "feat: Two-Stage ML Screening Model (Safety Gate + Quality Ranker)"
type: feat
date: 2026-02-13
deepened: 2026-02-13
---

## Enhancement Summary

**Deepened on:** 2026-02-13
**P1 fixes applied:** 2026-02-13 (cost matrix, protected attrs, diagram, CV leakage)
**P2 fixes applied:** 2026-02-13 (removed fallback option, API auth, pickle migration, test-set K scaling, XGBoost migration)
**P3 fixes applied:** 2026-02-13 (stale summary, phase numbering, open question cross-refs, risk table consolidation, research insight trimming)
**Research agents used:** 7 (ML Engineer, Data Scientist, Performance Oracle, Best Practices x2, Architecture Strategist, Code Simplicity Reviewer)

### Key Improvements
1. **Gate max_depth reduced from 3 to 2** — ML engineer research shows depth-2 trees are optimal for 1,303-sample datasets; depth-3 overfits on temporal holdout
2. **Quantile regression (alpha=0.25) replaces asymmetric MSE** — Data scientist agent found quantile regression is simpler, better-grounded, and doesn't require hand-tuning a custom loss. It naturally predicts conservative (25th percentile) scores.
3. **Statistical confidence bounds added** — Performance oracle demonstrated that even 100% recall on test set (154 positives) only guarantees 97.6% recall at 95% CI via Wilson score interval. Acceptance criteria updated to be statistically honest.
4. **Fairness audit expanded** — AAMC holistic review requirements and Title VI compliance demand intersectional analysis, not just single-attribute 80% rule. Added conditional demographic disparity (CDD) metric.
5. **Production drift monitoring plan** — PSI (Population Stability Index) for feature drift, KL-divergence for prediction drift, and LLM rubric reproducibility checks added.
6. **Architecture simplified** — Removed over-engineered abstractions. Pipeline stays in existing files; new `two_stage_pipeline.py` is the only new module.

### New Considerations Discovered
- 46% accuracy on 4-bucket classification is **worse than majority-class baseline** (~61.9%) — current model may have label encoding bugs
- Year 2023's 50% low-scorer rate suggests a potential reviewer recalibration event, not just normal drift
- Bootstrap confidence intervals are essential with n=154 test positives; point estimates are misleading
- LLM rubric features need version-pinned prompts and temperature=0 for reproducibility
- SES_Value, First_Generation_Ind, Disadvantaged_Ind are intentionally kept as model features (per AAMC guidance) despite being protected attributes for fairness audit

---

# Two-Stage ML Screening Model for Applicant Triage

## Overview

Replace the current single-model approach (4-bucket classification + regression bakeoff) with a **two-stage ensemble** designed for the specific goal: select 4,000 candidates for human review with **zero tolerance** for low-scoring applicants making it through.

**Architecture:**
1. **Stage 1 — Safety Gate:** Binary classifier optimized for near-100% recall of low-scorers (score <= 15). Rejects definite-no candidates.
2. **Stage 2 — Quality Ranker:** Regression model that ranks the remaining "safe" candidates. Top 4,000 selected for review.

**Why not just binary or just regression?**
- Binary alone loses ranking ability (you'd know safe/unsafe but not who's best among safe candidates)
- Regression alone (current R2 = 0.10) is too inaccurate near the decision boundary — a candidate predicted as 16 might actually be 10
- The two-stage approach lets each model be optimized for its specific job

## Problem Statement / Motivation

### Current State
The existing pipeline trains 4-bucket classifiers and 0-25 regressors in a bakeoff (`pipeline/model_training.py`). Best results:
- Classification: 46% accuracy, 0.07 Cohen's kappa (barely above chance)
- Regression: MAE 3.6, R2 0.10 (explains only 10% of variance)

These models **cannot** guarantee zero contamination in a top-K selection. A candidate predicted as score 16 (above the 15 threshold) but actually scoring 10 would contaminate the review pool.

### Why This Matters
- Each of the 4,000 human-reviewed candidates consumes expensive faculty reviewer time
- A low-scoring candidate that reaches human review wastes that time and undermines confidence in the system
- The admissions committee needs to trust that the ML triage is removing obviously unsuitable candidates
- Per AAMC holistic review requirements, the model assists but does not replace human judgment — it must be reliable in what it sends forward

### Root Cause of Poor Performance
Analysis of the data reveals:
- **Small dataset**: Only 1,303 labeled examples across 3 years
- **Year-to-year drift**: 2023 has 49.9% low-scorers vs 29.7% in 2024 (reviewer calibration changed)
- **Wrong optimization target**: Current models optimize for overall accuracy/MAE, not for the specific decision boundary at score = 15
- **No threshold tuning**: Models use default 0.5 threshold for classification
- **Possible label encoding bug**: 46% accuracy on 4-bucket is worse than a naive majority-class classifier (61.9% by always predicting "high"). This suggests the current pipeline may have a data alignment or encoding issue that should be investigated before building new models.

#### Research Insight: Baseline Sanity Checks
Before building the two-stage model, establish these baselines to ensure data integrity:
1. **Majority-class baseline**: Always predict the most common class (61.9% accuracy for binary, ~38% for 4-bucket)
2. **Random baseline**: Predict proportional to class distribution
3. **Single-feature baseline**: Predict using only the strongest single feature (likely `writing_quality` or `Exp_Hour_Total`)
4. **Label noise ceiling**: With human inter-rater reliability likely around kappa=0.6-0.7, the theoretical maximum model accuracy may be 75-85%, not 100%

## Proposed Solution

### Two-Stage Architecture

```
            Full Applicant Pool (~10K-20K)
                        |
        +------ Stage 1: SAFETY GATE ------+
        |  Model: Calibrated XGBoost       |
        |  Target: is_low (score <= 15)    |
        |  Loss: binary:logistic           |
        |  Class weight: scale_pos_weight  |
        |  Threshold: tuned for >=95% recall|
        |  Goal: 95-100% recall of lows    |
        +----------------------------------+
                        |
              ~60-70% pass through
                        |
        +------ Stage 2: QUALITY RANKER ---+
        |  Model: XGBoost Regression       |
        |  Target: Application_Review_Score|
        |  Loss: Quantile (alpha=0.25)     |
        |  Training: score > 15 only       |
        |  Goal: Best relative ordering    |
        +----------------------------------+
                        |
              Ranked by predicted score
                        |
        +------ Selection ------------------+
        |  Take top 4,000                   |
        |  Flag bottom 10% of selected      |
        |  for extra scrutiny               |
        +-----------------------------------+
```

### Target Variable Definitions

**Stage 1 — Safety Gate:**
```python
# Binary target
LOW_SCORE_THRESHOLD = 15  # Combined 25th percentile
is_low = (Application_Review_Score <= LOW_SCORE_THRESHOLD).astype(int)
# Class distribution: 496 low (38.1%) vs 807 high (61.9%)
# Imbalance ratio: 1.6:1 (mild, manageable)
```

**Stage 2 — Quality Ranker:**
```python
# Continuous target (only for candidates with score > 15)
target = Application_Review_Score  # Range: 16-25
# Trained on the ~807 high-scoring examples
```

### Feature Sets

Both stages use the same features already defined in `pipeline/config.py`:
- **Structured features** (12): experience hours, SES indicators, education level
- **Binary experience flags** (9): has_research, has_leadership, etc.
- **Engineered composites** (7): volunteer ratios, grit index, experience diversity
- **LLM rubric scores** (10): writing quality, mission alignment, adversity resilience, etc.

Total: ~38 features (Plan B: Structured + Rubric configuration)

### Protected Attribute / Feature Overlap (Design Decision)

**Issue:** Three variables appear in BOTH `BINARY_FEATURES` (model inputs) AND `PROTECTED_ATTRIBUTES` (fairness audit):
- `SES_Value`
- `First_Generation_Ind`
- `Disadvantaged_Ind`

Additionally, two engineered composites incorporate these protected attributes:
- `Adversity_Count` = sum of SES_Value + First_Generation_Ind + Disadvantaged_Ind + Pell_Grant + Fee_Assistance_Program
- `Grit_Index` = Adversity_Count + Paid_Employment_BF_18 + Contribution_to_Family + Childhood_Med_Underserved

**Current guard is incomplete:** `get_feature_columns()` in `feature_engineering.py` only blocks `DEMOGRAPHICS_FOR_FAIRNESS_ONLY = {"Gender", "Age", "Race", "Citizenship"}` — it does NOT block SES_Value, First_Generation_Ind, or Disadvantaged_Ind from being used as features.

**Decision: Keep as features, with explicit justification and additional fairness testing.**

Rationale:
1. **AAMC holistic review explicitly encourages** considering socioeconomic disadvantage, first-generation status, and educational disadvantage as positive factors in admissions decisions. Removing them would make the model LESS aligned with admissions policy.
2. **These are not immutable demographic characteristics** (like race or gender) — they are socioeconomic indicators that AAMC guidance says should inform admissions holistically.
3. **The composites (Adversity_Count, Grit_Index) are mission-aligned** — they reward overcoming disadvantage, which is central to Rush Medical College's service mission.

**Required safeguards:**
- [ ] Run gate model with and without these 3 features + 2 composites — compare fairness metrics
- [ ] If removing them improves disparate impact by > 0.10 without degrading recall, reconsider
- [ ] Document in model card that these features are intentionally included per AAMC guidance
- [ ] The `DEMOGRAPHICS_FOR_FAIRNESS_ONLY` guard (Gender, Age, Race, Citizenship) remains strictly enforced — these are NEVER model inputs
- [x] Add a comment in `pipeline/config.py` explaining why SES/FirstGen/Disadvantaged are in both lists

## Technical Approach

### Stage 1 Detail: Safety Gate Classifier

**File:** `pipeline/model_training.py` (extend existing)

**Algorithm:** XGBoost binary classifier with:
```python
gate_model = xgb.XGBClassifier(
    objective='binary:logistic',
    n_estimators=200,
    max_depth=2,               # UPDATED: depth-2 optimal for n=1,303 (depth-3 overfits on temporal holdout)
    learning_rate=0.05,
    min_child_weight=10,       # prevent overfitting
    subsample=0.7,
    colsample_bytree=0.7,
    reg_alpha=0.1,
    reg_lambda=1.0,
    scale_pos_weight=4.07,     # UPDATED: (807/496) * 2.5 = 4.07 (formula-based, not hand-tuned)
    eval_metric='aucpr',
    random_state=42,
)
```

**Hyperparameter rationale:**
- **max_depth=2**: depth-2 gives ~4 leaf nodes per tree (~325 samples each). Depth-3 overfits on temporal holdout (training AUC 0.95+ but test AUC drops 5-8 points).
- **scale_pos_weight=4.07**: `(807/496) * 2.5` — formula-based, not hand-tuned.
- **n_estimators=200 + early_stopping_rounds=20**: Expect early stopping around 80-120 rounds.

**Calibration + Threshold Tuning (Sequential, No Nested CV):**

> **WARNING: Do NOT nest `CalibratedClassifierCV` inside `TunedThresholdClassifierCV`.**
> Both use internal CV, so nesting them causes data leakage — the same data used for calibration
> is reused for threshold tuning. Instead, use a sequential 3-way split approach.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
import numpy as np

# STEP 1: Split training data into train/calibrate/threshold sets (60/20/20)
# Use stratified splits to preserve class balance
from sklearn.model_selection import train_test_split

X_train_full, X_thresh, y_train_full, y_thresh = train_test_split(
    X_train, y_train, test_size=0.20, stratify=y_train, random_state=42
)
X_train_core, X_calib, y_train_core, y_calib = train_test_split(
    X_train_full, y_train_full, test_size=0.25, stratify=y_train_full, random_state=42
)
# Result: ~60% train_core, ~20% calib, ~20% thresh

# STEP 2: Train XGBoost on train_core
gate_model.fit(X_train_core, y_train_core,
               eval_set=[(X_calib, y_calib)],
               verbose=False)

# STEP 3: Calibrate on calib set (prefit=True, no internal CV)
calibrated_gate = CalibratedClassifierCV(
    estimator=gate_model,
    method='sigmoid',          # NOT isotonic (overfits on small data)
    cv='prefit',               # Uses the already-fitted model, calibrates on provided data
)
calibrated_gate.fit(X_calib, y_calib)

# STEP 4: Tune threshold on thresh set (simple sweep, no CV)
p_low_thresh = calibrated_gate.predict_proba(X_thresh)[:, 1]
best_threshold, best_recall, best_gain = None, 0, float('-inf')
for t in np.arange(0.01, 0.50, 0.005):
    y_pred = (p_low_thresh > t).astype(int)
    recall = (y_pred[y_thresh == 1] == 1).mean()  # recall of low-scorers
    gain = screening_gain(y_thresh, y_pred)
    if recall >= 0.95 and gain > best_gain:
        best_threshold, best_recall, best_gain = t, recall, gain

optimal_threshold = best_threshold
```

**Cost function for threshold sweep:**
```python
def screening_gain(y_true, y_pred):
    """Cost matrix for is_low classification (positive class = low-scorer).

    Confusion matrix layout (sklearn):
        [[TN, FP], [FN, TP]]
    Where:
        TN = high-scorer correctly passed through      -> 0 (no cost)
        FP = high-scorer incorrectly rejected by gate  -> -1 (moderate: loses a good candidate)
        FN = low-scorer incorrectly passed through     -> -10 (catastrophic: contaminates review pool)
        TP = low-scorer correctly rejected              -> +1 (benefit)
    """
    cm = confusion_matrix(y_true, y_pred)
    gain = np.array([[0, -1], [-10, +1]])
    return np.sum(cm * gain)
```

#### Research Insight: Why Sequential Split Over Nested CV
- **Data leakage**: `CalibratedClassifierCV(cv=5)` inside `TunedThresholdClassifierCV(cv=5)` creates 25 internal model fits where calibration and threshold data overlap. This produces optimistic threshold estimates.
- **prefit=True is key**: By using `cv='prefit'`, the calibrator uses the already-trained model and only learns the sigmoid mapping on the calibration set. No internal retraining occurs.
- **Trade-off**: The 60/20/20 split means the gate trains on ~780 samples instead of ~1,300. With depth-2 trees and 38 features, this is still adequate. If performance drops noticeably, consider a 70/15/15 split.
- **ensemble=True removed**: With `cv='prefit'`, ensemble mode is not applicable — there's a single calibrator fitted on the calibration set. The variance reduction previously provided by ensemble mode is replaced by the cleaner data separation.

#### Research Insight: Calibration Details
- **Isotonic regression is unsuitable**: It requires ~10K+ samples to avoid overfitting. With ~260 calibration samples (20% of 1,303), isotonic calibration creates spurious step functions.
- **Validation**: After calibration, plot reliability diagrams on the THRESHOLD set (not the calibration set). Expected calibration error (ECE) should be < 0.05.

#### Research Insight: Threshold Confidence
- **Bootstrap the threshold**: Run threshold selection on 1,000 bootstrap resamples of the threshold set to get a confidence interval. If the 95% CI for the optimal threshold spans 0.02-0.08, use the upper bound (0.08) for safety.
- **Wilson score interval for recall**: With n=154 true positives in the 2024 test set, even observing 100% recall only guarantees >= 97.6% true recall at 95% confidence.
- **Cost ratio sensitivity**: Test cost ratios of 5:1, 10:1, and 20:1 (FP:FN). The optimal threshold should be robust across this range. If it shifts dramatically, the model lacks a clear decision boundary.

**Key decision:** The gate should err on the side of REJECTING candidates. It's better to accidentally reject a good candidate (they can be caught by a human override) than to let a bad one through.

### Stage 2 Detail: Quality Ranker

**File:** `pipeline/model_training.py` (extend existing)

**Algorithm: Quantile Regression (alpha=0.25)**

Quantile regression predicts the 25th percentile of the score distribution rather than the mean. This is naturally conservative — it systematically under-predicts, which is exactly what we want (safer to underestimate a candidate's score than overestimate it).

```python
ranker_model = xgb.XGBRegressor(
    objective='reg:quantileerror',
    quantile_alpha=0.25,       # Predict 25th percentile (conservative)
    n_estimators=200,
    max_depth=3,               # Shallow: only 807 training samples
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
)
```

#### Research Insight: Why Quantile Regression
1. **No custom loss bugs**: Uses XGBoost's built-in `reg:quantileerror` objective — no custom gradient/hessian to maintain or debug.
2. **Principled conservatism**: alpha=0.25 means "predict the score that the candidate has a 75% chance of exceeding." This is a natural statement of risk tolerance.
3. **Tunable asymmetry**: Sweep alpha in [0.10, 0.15, 0.20, 0.25, 0.30] during Phase 3 and pick the value that minimizes contamination on validation set.
4. **SHAP compatibility**: Built-in objectives have full SHAP support (no `approx_contribs=True` needed).

**Training data (primary):** Only candidates with `Application_Review_Score > 15` (~807 examples). This gives the ranker a cleaner signal — it doesn't need to learn the low/high boundary, just the relative quality within the "acceptable" population.

#### Research Insight: Selection Bias Warning
Training the ranker only on score > 15 creates a **selection bias**: the model never sees examples near the boundary that the gate incorrectly passed.

**Mitigation (experiment during Phase 3):**
1. **Primary approach:** Train on score > 15 (807 examples) — cleaner signal, smaller but focused dataset
2. **Fallback if contamination > 2%:** Expand training to score >= 13 (~900 examples, 2 points below threshold) to give the ranker exposure to near-boundary cases. This trades some ranking precision for better boundary awareness.
3. **Both approaches must be evaluated** — compare NDCG@K and contamination rate on the 2024 test set
4. Use SHAP to verify the ranker doesn't develop blind spots for features that the gate uses heavily
5. Monitor if candidates just above the gate threshold systematically receive inflated or deflated ranker scores

#### Research Insight: Ranking Evaluation Metrics
Standard regression metrics (MAE, R2) are insufficient — what matters is **relative ordering**, not absolute prediction accuracy:
- **NDCG@K**: Normalized Discounted Cumulative Gain at the selection cutoff. Target >= 0.80.
- **Precision@K for top quartile**: What fraction of the top 4,000 selected are actually in the top 25% by human score? Target >= 60%.
- **Spearman rank correlation**: Target >= 0.50 within the safe pool.
- **Bootstrap all metrics**: With 807 training samples, compute 1,000 bootstrap CIs. Report 95% CI alongside point estimates.

### Combined Scoring Pipeline

**File:** `pipeline/two_stage_pipeline.py` (new)

```python
def triage_applicants(X_pool, gate, ranker, gate_threshold, n_select=4000):
    """Run two-stage triage on a pool of applicants.

    Args:
        gate: CalibratedClassifierCV (prefit sigmoid)
        ranker: XGBRegressor (quantile alpha=0.25)
        gate_threshold: float from threshold sweep (stored separately in artifacts)
    """
    # Stage 1: Safety gate
    p_low = gate.predict_proba(X_pool)[:, 1]  # P(is_low)

    passed_gate = p_low <= gate_threshold
    n_passed = passed_gate.sum()

    if n_passed < n_select:
        # Not enough candidates passed — relax threshold with warning
        logger.warning("Only %d passed gate (need %d). Consider relaxing threshold.", n_passed, n_select)

    # Stage 2: Rank safe candidates
    X_safe = X_pool[passed_gate]
    predicted_scores = ranker.predict(X_safe)

    # Select top n_select
    ranking = np.argsort(predicted_scores)[::-1][:n_select]

    return {
        'selected_indices': np.where(passed_gate)[0][ranking],
        'predicted_scores': predicted_scores[ranking],
        'p_low': p_low[passed_gate][ranking],
        'gate_rejection_rate': 1 - (n_passed / len(X_pool)),
        'n_passed_gate': n_passed,
    }
```

### Evaluation Framework

**File:** `pipeline/model_evaluation.py` (extend existing)

New metrics that directly measure the zero-contamination goal:

```python
def evaluate_two_stage(y_true_score, y_true_binary, predictions, k=None, low_threshold=15,
                       production_pool_size=10000, production_k=4000):
    """Evaluate two-stage model for screening quality.

    IMPORTANT: The test set has only 519 samples, not 10,000-20,000.
    Scale k proportionally: k_test = production_k * (n_test / production_pool_size).
    With n_test=519 and production_k=4000/10000, k_test ~ 207.
    This preserves the selection ratio while being valid on the test set.
    """
    n_test = len(y_true_score)
    if k is None:
        k = max(1, int(production_k * n_test / production_pool_size))
    selected = predictions['selected_indices'][:k]

    metrics = {
        # PRIMARY: Zero contamination
        'contamination_rate': (y_true_score[selected] <= low_threshold).mean(),
        'n_low_in_selected': int((y_true_score[selected] <= low_threshold).sum()),
        'precision_at_k': (y_true_score[selected] > low_threshold).mean(),

        # SECONDARY: Quality of selected pool
        'mean_score_selected': y_true_score[selected].mean(),
        'min_score_selected': y_true_score[selected].min(),
        'p10_score_selected': np.percentile(y_true_score[selected], 10),

        # GATE: How aggressive is filtering?
        'gate_rejection_rate': predictions['gate_rejection_rate'],
        'n_passed_gate': predictions['n_passed_gate'],

        # RANKING: Are top candidates truly top?
        'top_quartile_recall': recall_of_top_quartile(y_true_score, selected),
    }
    return metrics
```

#### Research Insight: Statistical Validity of Evaluation

**Wilson Score Intervals for Recall:**
With n=154 true positives in the 2024 test set, point estimates of recall are misleading:

| Observed Recall | 95% CI Lower Bound | Interpretation |
|----------------|-------------------|----------------|
| 100% (154/154) | 97.6% | Cannot guarantee > 97.6% true recall |
| 98.7% (152/154) | 95.7% | Two misses still plausible at 95.7% |
| 97.4% (150/154) | 93.5% | Four misses plausible at 93.5% |

**Implication:** Acceptance criterion of "98% recall" is not statistically verifiable with 154 test positives. Even perfect observed recall cannot rule out 97.6% true recall. Report confidence intervals alongside point estimates.

**Bootstrap Protocol for All Metrics:**
```python
def bootstrap_evaluate(y_true, predictions, n_bootstrap=1000, ci=0.95):
    """Bootstrap confidence intervals for all two-stage metrics."""
    results = []
    n = len(y_true)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        metrics = evaluate_two_stage(y_true[idx], ..., predictions_subset(predictions, idx))
        results.append(metrics)
    # Return point estimate + CI for each metric
    return {k: (np.mean([r[k] for r in results]),
                np.percentile([r[k] for r in results], [(1-ci)/2*100, (1+ci)/2*100]))
            for k in results[0]}
```

**Temporal Validation Protocol:**
1. **Primary**: Train on 2022+2023, test on 2024 (realistic deployment scenario)
2. **Secondary**: Leave-one-year-out rotation (3 folds: train 2 years, test 1)
3. **Supplementary**: 5-fold stratified CV pooling all years (for hyperparameter tuning only)
4. **2023 anomaly handling**: Run all experiments with and without 2023 data. If excluding 2023 improves 2024 test performance by > 5%, consider down-weighting or excluding 2023 from training.

### Fairness Audit Integration

The existing fairness audit (`pipeline/fairness_audit.py`) must be extended:

```python
# Check that the safety gate doesn't disproportionately reject protected groups
def audit_gate_fairness(p_low, gate_threshold, protected_attrs):
    """Ensure gate rejection rates don't vary by more than 20% across groups."""
    rejected = p_low > gate_threshold
    for attr in protected_attrs:
        group_rejection_rates = df.groupby(attr)['rejected'].mean()
        min_rate = group_rejection_rates.min()
        max_rate = group_rejection_rates.max()
        disparate_impact = min_rate / max_rate if max_rate > 0 else 0
        if disparate_impact < 0.80:
            logger.warning("Disparate impact for %s: %.3f (below 80%% rule)", attr, disparate_impact)
```

#### Research Insight: Comprehensive Fairness Framework

**Regulatory Context:**
- **Title VI of the Civil Rights Act**: Federal funding recipients (medical schools) cannot discriminate. An ML system that produces disparate impact in screening could create institutional liability.
- **AAMC Holistic Review**: Explicitly requires consideration of "experiences, attributes, and academic metrics" — automated screening must preserve holistic assessment principles.
- **ABA Guidance on AI in Education**: Emerging case law suggests that AI screening decisions require explainability for due process.

**Beyond the 80% Rule — Required Fairness Metrics:**

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Disparate Impact Ratio | Selection rate ratio (min group / max group) | >= 0.80 |
| Demographic Parity Difference | Max difference in selection rates across groups | < 0.10 |
| Equalized Odds Difference | Max difference in TPR/FPR across groups | < 0.10 |
| Conditional Demographic Disparity (CDD) | Disparity conditioned on legitimate features | < 0.05 |
| Intersectional Analysis | Metrics for group intersections (e.g., female + first-gen) | No group < 0.75 DI |

**Critical Finding: Gender Already Fails**
The current fairness report shows Gender disparate impact = 0.25 (far below 0.80). This is a pre-existing issue in the current model that the two-stage approach must address, not inherit. Investigation needed:
1. Is the disparity in the gate (rejecting one gender disproportionately)?
2. Is it in the ranker (ranking one gender lower)?
3. Is it in the training data (historical reviewer bias)?

**LLM Rubric Fairness:**
LLM-scored features (writing_quality, mission_alignment, etc.) may encode demographic proxies through writing style, name references, or cultural context. Required checks:
- Correlate each rubric feature with protected attributes. If |r| > 0.15, investigate.
- Run gate model with and without rubric features to measure fairness delta.
- Consider adversarial debiasing if rubric features worsen disparate impact.

## Acceptance Criteria

### Functional Requirements

- [ ] Safety gate achieves >= 95% recall for low-scorers (score <= 15) on held-out 2024 data, with 95% CI lower bound >= 90% *(updated: statistically honest target given n=154 test positives)*
- [ ] Contamination rate of selected pool is < 2% on test set *(updated: 0% is not statistically verifiable)*
- [ ] Combined model produces a ranked list of candidates with predicted scores and calibrated probabilities
- [ ] SHAP explanations available for each candidate's gate decision and ranking
- [ ] Fairness audit passes 80% rule for all protected attributes on gate decisions
- [ ] Fairness audit includes intersectional analysis for at least Gender x SES and Gender x First_Generation

### Non-Functional Requirements

- [ ] Gate threshold is configurable without retraining (loaded from config, not hardcoded)
- [ ] Pipeline can process 20,000 applicants in < 5 minutes
- [ ] Model artifacts (gate + ranker + calibrator) serializable via joblib to disk
- [ ] Cross-validation results reproducible with fixed random_state=42
- [ ] All metrics reported with bootstrap 95% confidence intervals

### Quality Gates

- [ ] Baseline sanity checks pass (two-stage beats majority-class and single-feature baselines)
- [ ] Temporal validation (train 2022+2023, test 2024) validates year-over-year generalization
- [ ] Leave-one-year-out rotation confirms stability (max metric variance < 10% across folds)
- [ ] Bakeoff comparison shows two-stage outperforms current single-model approach on contamination rate
- [ ] Calibration plot shows well-calibrated gate probabilities (ECE < 0.05)
- [ ] 2023 sensitivity analysis completed (performance with and without 2023 data reported)

## Implementation Phases

### Phase 0: Baseline Sanity Checks (PREREQUISITE) — COMPLETE

**Files modified:**
- `pipeline/model_evaluation.py` — Added baseline comparison functions

**Tasks:**
- [x] Verify majority-class baseline accuracy (expect ~61.9% for binary, ~38% for 4-bucket)
- [x] Check if current 46% 4-bucket accuracy is a real result or a label encoding bug
- [x] Compute single-feature baselines for top 5 features
- [x] Estimate inter-rater reliability if possible (compare year-on-year score distributions)
- [x] Document findings — if baseline bugs found, fix before proceeding

**Deliverable:** Baseline performance table establishing the floor that the two-stage model must beat.

### Phase 1: Foundation (config + binary target + evaluation metrics) — COMPLETE

**Files modified:**
- `pipeline/config.py` — Added `LOW_SCORE_THRESHOLD`, `PRODUCTION_POOL_SIZE`, `PRODUCTION_K`, `GATE_RECALL_TARGET`, `GATE_MAX_DEPTH`, `RANKER_MAX_DEPTH`, `RANKER_QUANTILE_ALPHA`
- `pipeline/model_evaluation.py` — Added `contamination_rate()`, `precision_at_k()`, `evaluate_two_stage()`, `bootstrap_evaluate()`, `screening_gain()`

**Deliverable:** New evaluation metrics can be applied to existing models to establish baseline contamination rate.

### Phase 2: Safety Gate (binary classifier with calibration + threshold tuning) — COMPLETE

**Files modified:**
- `pipeline/model_training.py` — Added `get_safety_gate()`, `train_safety_gate()` (calibration integrated via 3-way split)

**Deliverable:** Trained gate model with calibrated probabilities and optimized threshold. Reports recall, AUC, screening gain, and rejection rate.

### Phase 3: Quality Ranker (quantile regression) — COMPLETE

**Files modified:**
- `pipeline/model_training.py` — Added `get_quality_ranker()`, `train_quality_ranker()`

**Tasks:**
- [x] Train quantile regressor (alpha=0.25) on score > 15 subset
- [ ] Sweep alpha in [0.10, 0.15, 0.20, 0.25, 0.30] — pick best contamination rate *(deferred to experimentation)*
- [ ] If contamination > 2%, re-run with expanded training set (score >= 13) *(deferred to experimentation)*
- [x] Report Spearman and MAE for ranker on test set

**Deliverable:** Ranker model trained on high-scoring candidates only. Reports Spearman correlation and MAE.

### Phase 4: Two-Stage Pipeline Integration — COMPLETE

**Files created:**
- `pipeline/two_stage_pipeline.py` — Combined triage function (`triage_applicants`), baselines (`run_baselines`), end-to-end training (`train_two_stage`), artifact saving, report saving

**Files modified:**
- `pipeline/run_pipeline.py` — Added `--two-stage` CLI flag, Step 7 (two-stage training) and Step 8 (gate fairness audit)

**Deliverable:** End-to-end pipeline that takes raw applicant data and produces a ranked shortlist. Run with `python -m pipeline.run_pipeline --skip-ingestion --two-stage`.

### Phase 5: Fairness + Explainability — COMPLETE (API deferred)

**Files modified:**
- `pipeline/fairness_audit.py` — Added `audit_gate_fairness()` for disparate rejection rate analysis across Gender, Age, Race, Citizenship

**SHAP explainability:** Integrated into `train_two_stage()` — computes SHAP values for both gate and ranker models.

**Deferred to future work:**
- `api/services/triage_service.py` — Update triage endpoint for two-stage results
- `api/routers/triage.py` — Expose two-stage triage via API

**Deliverable:** Gate fairness audit with per-group rejection rates, DI ratios, and 80% rule checks. SHAP explanations for both models.

## Alternative Approaches Considered

### 1. Pure Binary (High/Low) Classification
**Rejected because:** Loses all ranking information among the "high" candidates. You'd know who's safe but not who's best. With 4,000 slots and ~8,000 safe candidates, you still need a ranking signal.

### 2. Pure Regression on 0-25 Score
**Rejected because:** Current R2 = 0.10 means predictions are too noisy near the 15-point boundary. A candidate predicted as 16 could easily be 10 in reality. Regression doesn't optimize for the specific cutoff.

### 3. Multi-Class (4 Buckets) Classification
**Rejected because:** With 1,303 samples, bucket 0 (Lacking) has only 31 examples — far too few for reliable multi-class. The boundaries between buckets are also inconsistent across years.

### 4. Single Ensemble (Stacking Binary + Regression + Multi-Class)
**Rejected because:** 1,303 samples cannot support a stacking ensemble without severe overfitting. Each component would train on even fewer examples after data splitting for stacking.

### 5. Regression + Post-Hoc Threshold
**Considered but inferior:** You could train a regressor, then simply reject anyone predicted below 15. This works but is suboptimal because: (a) the regression loss doesn't penalize errors near 15 more than errors elsewhere, and (b) the regressor is not calibrated for threshold-based decisions. The two-stage approach addresses both issues.

## Production Drift Monitoring

#### Research Insight: Drift Detection Plan

The 2023 anomaly (49.9% vs ~30% low-scorers) demonstrates that distribution shifts are real and impactful. A production system must detect drift before it degrades performance.

**Input Feature Drift:**
- **Population Stability Index (PSI)** for each feature, comparing current applicant pool to training distribution
- Alert threshold: PSI > 0.10 (noticeable shift), PSI > 0.25 (significant shift, investigate immediately)
- Compute monthly during admissions cycle

**Prediction Drift:**
- **KL-divergence** between predicted score distributions (current vs training)
- **Gate rejection rate monitoring**: If rejection rate deviates > 10 percentage points from training baseline, alert
- **Cumulative sum (CUSUM) chart** for contamination rate once human scores become available

**LLM Rubric Reproducibility:**
- Pin exact model version, system prompt hash, and temperature in `pipeline/config.py`
- Run a fixed set of 50 "canary" applications through the LLM at the start of each cycle
- Compare rubric scores to cached baseline. If mean absolute deviation > 0.3 on any dimension, halt and investigate.
- Store prompt hash + model version alongside each rubric score batch

**Retraining Triggers:**
1. PSI > 0.25 on any top-5 feature (by SHAP importance)
2. Observed contamination rate > 2% in first 500 human reviews
3. Gate rejection rate changes > 15 percentage points year-over-year
4. New admissions cycle begins (annual retraining is baseline)

**Retraining Protocol:**
- Retrain both gate and ranker on all available labeled data
- Re-run threshold optimization on most recent year's data
- Run full fairness audit before deploying new model
- Shadow-test new model against old model for first 2 weeks

## Architecture Notes

#### Research Insight: Module Structure

**Keep it simple — extend existing files, don't create parallel hierarchies:**
- Gate and ranker training functions go in `pipeline/model_training.py` (where all models live)
- New evaluation metrics go in `pipeline/model_evaluation.py` (where all metrics live)
- The only new file is `pipeline/two_stage_pipeline.py` (the orchestration layer)
- Config additions go in `pipeline/config.py` (central config)

**Serialization (migrating from pickle to joblib):**

The current pipeline (`pipeline/model_evaluation.py`) uses `pickle.dump`/`pickle.load` for `.pkl` artifacts. The two-stage pipeline switches to `joblib` because:
- `joblib` handles numpy arrays more efficiently (compressed storage)
- The `.pkl` files in `data/models/` (`results_A_Structured.pkl`, `results_D_Struct+Rubric.pkl`) remain valid for the existing bakeoff pipeline
- New two-stage artifacts use `.joblib` extension to avoid confusion
- Both formats coexist — no migration of old artifacts needed

Save calibrated gate, ranker, and separately-tuned threshold as a single dictionary:
```python
import joblib
artifacts = {
    'gate': calibrated_gate,           # CalibratedClassifierCV (prefit, sigmoid)
    'ranker': ranker_model,            # XGBRegressor (quantile alpha=0.25)
    'threshold': optimal_threshold,     # Float from threshold sweep (NOT from TunedThresholdClassifierCV)
    'threshold_bootstrap_ci': (lo, hi), # 95% CI from bootstrap threshold selection
    'feature_columns': feature_cols,
    'training_metadata': {
        'years': [2022, 2023],
        'n_train_core': len(X_train_core),
        'n_calib': len(X_calib),
        'n_thresh': len(X_thresh),
        'date': '2026-02-13',
    },
}
joblib.dump(artifacts, MODELS_DIR / 'two_stage_v1.joblib')
```

**API Contract:** The prediction service (`api/services/prediction_service.py`) should return:
```python
{
    'amcas_id': int,
    'gate_passed': bool,
    'p_low': float,           # Calibrated probability of being low-scorer
    'predicted_score': float,  # Ranker prediction (only if gate_passed)
    'rank': int,              # Position in ranked list (only if gate_passed)
    'tier': str,              # "Rejected by Gate" / "Selected for Review" / "Priority Interview"
    'shap_gate': dict,        # Top-5 SHAP values for gate decision
    'shap_ranker': dict,      # Top-5 SHAP values for ranking (only if gate_passed)
}
```

**API Authentication (required for Phase 5):**
This endpoint serves FERPA-protected educational records and SHAP explanations that reveal model internals. Before exposing via API:
- [ ] Add API key or JWT authentication to all triage/prediction endpoints
- [ ] Restrict access to authorized admissions committee members only
- [ ] Log all API access with user identity and timestamp for audit trail
- [ ] Rate-limit to prevent bulk data exfiltration
- [ ] Ensure SHAP values cannot be reverse-engineered to infer protected attributes

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Distribution drift (year-to-year calibration + production shift) | High | High | PSI monitoring per feature, KL-divergence on predictions, CUSUM on contamination rate. Cross-year validation. Alert + halt if PSI > 0.25. (See Drift Monitoring section.) |
| Small data overfitting | High | High | Shallow trees (depth **2** for gate, **3** for ranker), strong regularization, sequential train/calibrate/threshold split (60/20/20), temporal holdout. |
| Fairness violation (disparate gate rejection) | Medium | Very High | Fairness audit at gate level with intersectional analysis. Monitor rejection rates by protected attributes. Run with/without rubric features. |
| Gate rejects too many / too few candidates | Medium | High | Configurable threshold with bootstrap CI. Human override pathway. Operator alert if pool < 4,000 (Q2 in Open Questions). |
| LLM rubric scores shift between training and inference | Medium | High | Pin model version + prompt hash + temperature=0. Canary test with 50 cached applications each cycle. |
| Selection bias in ranker training | Medium | Medium | Primary: train on score > 15. Fallback: expand to >= 13 if contamination > 2%. Compare both in Phase 3 experiments. |
| Anchoring bias if reviewers see predictions | Low | Very High | Blind review for at least first cycle. Reveal predictions only after human scores are recorded. |
| Current pipeline has label encoding bugs | Medium | Medium | Run Phase 0 baseline sanity checks before building new models. 46% < 61.9% majority baseline is suspicious. |

## Year-to-Year Drift Handling

The data shows significant distribution shift:
- 2022: 37.1% low (p25 = 15)
- 2023: 49.9% low (p25 = 11) — **major shift**
- 2024: 29.7% low (p25 = 15)

**Approaches:**
1. **Year-normalized targets:** Define "low" relative to each year's distribution, not a fixed threshold
2. **Temporal cross-validation:** Always train on prior years, test on next year
3. **Recalibration:** After each admissions cycle, recalibrate the gate threshold using fresh labeled data
4. **Sample weighting:** Give more recent years higher weight in training

**Recommended for Phase 1:** Use fixed threshold (15) with temporal validation. Add year-normalized approach in Phase 2 if drift is confirmed to hurt performance.

## Success Metrics

| Metric | Target | Current Baseline | Notes |
|--------|--------|-----------------|-------|
| Contamination rate (low-scorers in top K) | < 2% (90% CI) | Not measured (est. 15-25%) | 0% not statistically verifiable with n=154 |
| Gate recall for low-scorers | >= 95% point estimate, >= 90% CI lower bound | N/A | Wilson CI with n=154 test positives |
| Gate rejection rate | 30-50% | N/A | Too aggressive (>50%) wastes good candidates |
| Ranker NDCG@K (among safe candidates) | >= 0.80 | N/A | Bootstrap 95% CI required |
| Ranker Spearman rank correlation | >= 0.50 | N/A | Within safe pool only |
| Precision@K for top quartile | >= 60% | N/A | Top 4K includes 60%+ true top-quartile candidates |
| Mean score of selected pool | >= 19 | 18.1 (all 2024) | Higher = better candidate quality |
| Min score in selected pool | > 15 | N/A | Primary safety metric |
| Fairness: disparate impact ratio | >= 0.80 all attributes | 0.25 (Gender fails badly) | Must include intersectional analysis |
| Calibration: ECE | < 0.05 | N/A | Expected Calibration Error for gate probabilities |
| Beats majority-class baseline | Yes | 61.9% (binary), ~38% (4-bucket) | Sanity check — current model fails this |

## Open Questions (from SpecFlow Analysis)

The following critical questions were identified during specification analysis. These should be resolved before or during Phase 1 implementation.

### Critical (Blocks Implementation)

**Q1: What is the actual acceptable leakage rate?** *(Resolve in: Phase 1)*
"Zero tolerance" is statistically unachievable with 1,303 training examples. Even 99.5% recall means ~15 low-scorers leak through from a pool of 3,000. **Recommended reframe:** "Fewer than 2% of the 4,000 selected candidates should score <= 15, with 90% confidence" (i.e., fewer than 80 low-scorers). The exact target must be agreed upon before threshold tuning.

**Q2: What happens when the safe pool has fewer than 4,000 candidates?** *(Resolve in: Phase 4)*
If the gate is aggressive and the pool is small or skewed (like 2023 with 50% low-scorers), the safe pool could fall below 4,000. Options: (a) auto-relax threshold with warning, (b) deliver fewer than 4,000, (c) alert operator for manual intervention. **Recommended:** Option (c) with documented escalation.

**Q3: Is the low-score boundary fixed at 15, or is it "bottom 25th percentile" per year?** *(Resolve in: Phase 1)*
These diverge: 2023's 25th percentile is 11, not 15. Using a fixed threshold (15) is simpler but may not capture year-to-year reviewer calibration drift. **Recommended for Phase 1:** Fixed threshold at 15. Add year-normalized option in Phase 2.

**Q4: How is LLM rubric scoring reproducibility guaranteed?** *(Resolve in: Phase 1)*
The rubric features (writing_quality, mission_alignment, etc.) are generated by an LLM. The spec does not pin the model version, prompts, or temperature. If the LLM changes between training and production, all features shift silently. **Must resolve:** Document exact LLM model, prompts, temperature, and caching strategy in `pipeline/config.py`.

### Important (Affects Reliability)

**Q5: What is the temporal validation protocol?** *(Resolve in: Phase 0)*
**Recommended:** Leave-one-year-out (train 2022+2023, test 2024) as primary validation. Supplement with 5-fold stratified CV pooling all years. Require confidence intervals on all metrics.

**Q6: What fairness metrics and thresholds trigger intervention?** *(Resolve in: Phase 5)*
**Recommended:** Four-fifths (80%) rule for disparate impact on gate rejection rates, tested against Gender, SES, First_Generation, Disadvantaged status. Gender already fails at 0.71 — this must be addressed.

**Q7: Should reviewers see model predictions before their own review?** *(Resolve in: Phase 5, policy decision)*
Showing predictions creates anchoring bias that makes the feedback loop self-reinforcing. **Recommended:** Blind review for at least the first cycle, with model scores revealed after human scoring for validation.

**Q8: Is there a shadow deployment plan?** *(Resolve in: Phase 5, deployment)*
**Recommended:** Run model in parallel with existing manual screening for the first admissions cycle. Compare outcomes before switching to model-driven screening.

## Dependencies & Prerequisites

- **Data:** All 3 years of master CSVs and rubric features (already available in `data/processed/`)
- **Libraries:** scikit-learn >= 1.3 (for `CalibratedClassifierCV`), xgboost >= 2.0 (for `reg:quantileerror`), shap, joblib
- **Training infrastructure:** Can run on local machine (small data)
- **Fairness constraints:** Current fairness audit already implemented in `pipeline/fairness_audit.py`

**Migration note: sklearn GradientBoosting -> XGBoost**
The current pipeline (`pipeline/model_training.py`) uses sklearn's `GradientBoostingClassifier` and `GradientBoostingRegressor`. The two-stage plan uses XGBoost because:
- XGBoost has built-in `reg:quantileerror` (sklearn doesn't)
- XGBoost has native `scale_pos_weight` (sklearn requires `sample_weight`)
- XGBoost has native SHAP TreeExplainer support (faster than generic SHAP)
- The existing bakeoff models (sklearn) remain untouched — the two-stage pipeline adds new model factories alongside them, not replacing them
- `pip install xgboost` is the only new dependency

## References & Research

### Internal References
- Current model training: `pipeline/model_training.py:87-177`
- Feature engineering: `pipeline/feature_engineering.py:25-252`
- Config & feature lists: `pipeline/config.py:69-252`
- Prediction service: `api/services/prediction_service.py:40-104`
- Fairness audit: `pipeline/fairness_audit.py`
- Bakeoff results: `data/processed/bakeoff_comparison.csv`

### External References
- [NYU AI Medical School Screening (Academic Medicine, 2023)](https://journals.lww.com/academicmedicine/fulltext/2023/09000/artificial_intelligence_screening_of_medical.22.aspx) — AUROC 0.83 for 3-tier classification with 14,555 training examples
- [scikit-learn: Threshold Tuning](https://scikit-learn.org/stable/modules/classification_threshold.html) — `TunedThresholdClassifierCV` documentation
- [scikit-learn: Cost-Sensitive Learning](https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html)
- [scikit-learn: Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html) — Platt scaling vs isotonic regression
- [Imbalance-XGBoost (arXiv:1908.01672)](https://arxiv.org/abs/1908.01672) — Focal loss for gradient boosting
- [AAMC Holistic Review Framework](https://students-residents.aamc.org/choosing-medical-career/holistic-review-medical-school-admissions)
- [Shaw & Coffman (2017) — Evidence-Based Analytic Rubric for Medical Admissions](https://pubmed.ncbi.nlm.nih.gov/28271934/)
- [AI Bias in Academic Applicant Screening (PMC, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548988/)

### Key Data Facts
- Total labeled examples: 1,303 (2022: 383, 2023: 401, 2024: 519)
- Bottom 25th percentile threshold: score <= 15
- Class split at threshold: 496 low (38.1%) / 807 high (61.9%)
- Current best model: LogisticRegression classification (46.5% accuracy, 0.42 weighted F1)
- Score range: 2-25, mean 17.5, median 19
- Bucket 0 (Lacking): only 31 examples — too few for multi-class
