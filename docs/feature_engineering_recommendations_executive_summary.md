# Feature Engineering Recommendations - Executive Summary

**Project:** Rush Medical College AMCAS Triage System
**Date:** February 13, 2026
**Priority:** HIGH - Affects production deployment readiness

---

## The Bottom Line

**Current State:**
- 46 features → R² = 0.72 (good), but 95% of signal comes from LLM rubric scores
- Structured features alone → R² = 0.04 (nearly random)
- Missing critical academic metrics (GPA, MCAT)
- High feature redundancy (5-8 features can be dropped)

**Critical Path for Production:**
1. Add GPA/MCAT (2-4 hours) → Expected +0.20 R²
2. Drop redundant features (1 hour) → Cleaner model, no performance loss
3. Implement drift detection (1-2 days) → Prevents catastrophic failures
4. Always run LLM rubric scoring ($943/year) → Non-negotiable for quality predictions

---

## Top 4 Recommendations (Implement Immediately)

### 1. Extract GPA and MCAT Scores ⭐⭐⭐⭐⭐
**Impact:** +0.15-0.25 R² for structured-only model
**Effort:** 2-4 hours
**Why Critical:** GPA and MCAT are THE primary screens for medical schools. Currently missing.

**Implementation:**
```python
# Add to feature_engineering.py
def extract_academic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract GPA and MCAT from Academic Records table."""
    return pd.DataFrame({
        ID_COLUMN: df[ID_COLUMN],
        'Overall_GPA': df['Total_GPA'].fillna(df['Total_GPA'].median()),
        'BCPM_GPA': df['Science_GPA'].fillna(df['Science_GPA'].median()),
        'MCAT_Total': df['MCAT_Total'].fillna(0),  # 0 = not yet taken
        'Has_MCAT': (df['MCAT_Total'] > 0).astype(int),
    })
```

**Data Source:** `5. Academic Records.xlsx` (check column names)

---

### 2. Drop Redundant Linear Combinations ⭐⭐⭐⭐
**Impact:** Faster training, cleaner SHAP, no accuracy loss
**Effort:** 1 hour
**Why Critical:** Perfect linear combinations add no information, dilute feature importance

**Drop These 3 Features:**
```python
# In config.py, remove from ENGINEERED_FEATURES:
- 'Exp_Hour_Total'           # = sum of all hour columns
- 'Total_Volunteer_Hours'    # = Med + Non-Med volunteer
- 'Clinical_Total_Hours'     # = Shadowing + Med Employment
```

**Before:** 46 features
**After:** 43 features
**Performance change:** None (tree models ignore redundant features anyway)

---

### 3. Implement Feature Drift Detection ⭐⭐⭐⭐⭐
**Impact:** Prevents catastrophic production failures
**Effort:** 1-2 days
**Why Critical:** Model trained on 2022-2023 will score 2025+ applicants. Distributions WILL shift.

**Implementation:**
```python
def detect_drift_before_scoring(new_data: pd.DataFrame,
                                training_stats: dict) -> dict:
    """Run Kolmogorov-Smirnov test on all numeric features."""
    from scipy.stats import ks_2samp

    alerts = []
    for col in NUMERIC_FEATURES:
        stat, p_value = ks_2samp(
            training_stats['distributions'][col],
            new_data[col].dropna()
        )
        if p_value < 0.05:
            alerts.append({
                'feature': col,
                'p_value': p_value,
                'mean_shift': (new_data[col].mean() -
                              training_stats['means'][col]) / training_stats['stds'][col]
            })

    if len(alerts) > len(NUMERIC_FEATURES) * 0.2:
        logger.critical(f"DRIFT ALERT: {len(alerts)} features drifted")
        return {'drift_detected': True, 'alerts': alerts}

    return {'drift_detected': False, 'alerts': alerts}
```

**Deploy as:** Pre-scoring validation step in production API

---

### 4. Save Training Statistics with Model ⭐⭐⭐⭐
**Impact:** Enables normalization, imputation, and drift detection
**Effort:** 2 hours
**Why Critical:** Score-only deployment needs frozen statistics for consistency

**Implementation:**
```python
# In model_training.py, add to model artifact:
model_artifact = {
    'gate': gate_model,
    'ranker': ranker_model,
    'scaler': StandardScaler(fitted=True),
    'threshold': 0.125,
    'feature_columns': feature_names,
    'training_stats': {  # NEW
        'means': X_train.mean(axis=0).tolist(),
        'stds': X_train.std(axis=0).tolist(),
        'medians': np.median(X_train, axis=0).tolist(),
        'distributions': {col: X_train[:, i].tolist()
                         for i, col in enumerate(feature_names)},
        'train_years': [2022, 2023],
        'n_train': len(X_train),
    },
    'metadata': {...}
}
```

---

## Rubric Integration Decision (High Priority)

### The Economics
**Cost to score 17,000 applicants with GPT-4 Turbo:**
- $0.0555 per applicant × 17,000 = **$943.50 per year**
- Time: ~70 minutes (20 concurrent API calls)

**Performance Impact:**
- Without rubric (Plan A): R² = 0.04 ⭐ (Very Poor - nearly random)
- With rubric (Plan B):    R² = 0.72 ⭐⭐⭐⭐ (Good)

### Recommendation: ALWAYS RUN RUBRIC SCORING

**Rationale:**
- $943/year is negligible vs. $4M+ reviewer time saved
- Plan A model is too weak to trust (R² = 0.04 = coin flip)
- 70 minutes scoring time fits overnight batch window

**Implementation:**
```python
def score_applicants_production(amcas_data: pd.DataFrame) -> pd.DataFrame:
    """Production pipeline with mandatory rubric."""
    # 1. Extract structured features (43 features after cleanup)
    structured = extract_structured_features(amcas_data)

    # 2. Extract NEW academic features (4 features)
    academic = extract_academic_features(amcas_data)

    # 3. Score with LLM rubric (10 features, ~70 min for 17K)
    rubric = batch_score_rubric(amcas_data[['personal_statement', 'secondary_essays']])

    # 4. Combine and predict
    X = combine_feature_sets([structured, academic, rubric])
    return two_stage_model.predict(X)
```

**DO NOT deploy without rubric scoring** unless acceptable to get random predictions.

---

## Medium-Priority Enhancements (Implement This Month)

### 5. Build NLP Features for Personal Statements ⭐⭐⭐
**Impact:** +0.05-0.10 R² as rubric fallback
**Effort:** 1 day
**Why Useful:** Cheap approximation of writing quality if API fails

**Features to extract:**
```python
def extract_ps_nlp_features(text: str) -> dict:
    """Lightweight NLP features (8 total)."""
    return {
        'ps_word_count': len(text.split()),
        'ps_sentence_count': len(sent_tokenize(text)),
        'ps_avg_sentence_length': word_count / sentence_count,
        'ps_lexical_diversity': len(set(tokens)) / len(tokens),
        'ps_sentiment_polarity': TextBlob(text).sentiment.polarity,
        'ps_flesch_readability': textstat.flesch_reading_ease(text),
        'ps_medical_keyword_density': count_keywords(text, MEDICAL_VOCAB) / word_count,
        'ps_service_keyword_density': count_keywords(text, SERVICE_VOCAB) / word_count,
    }
```

**Use case:** Fallback scoring if LLM API is down

---

### 6. Investigate Binary Flag Redundancy ⭐⭐⭐
**Impact:** Drop 4-6 features if redundant
**Effort:** 2 hours
**Why Useful:** Cleaner model, easier SHAP interpretation

**Check these correlations:**
```python
# Expected redundancy (investigate):
has_research           ↔ Exp_Hour_Research > 0        (expected r > 0.95)
has_volunteering       ↔ Exp_Hour_Volunteer_Med > 0   (expected r > 0.95)
has_shadowing          ↔ Exp_Hour_Shadowing > 0       (expected r > 0.95)
has_clinical_experience ↔ Exp_Hour_Employ_Med > 0     (expected r > 0.95)

# Likely unique (keep):
has_honors             ← keyword-extracted, no hour equivalent
has_leadership         ← may have leadership without logged hours
```

**If r > 0.95:** Drop binary flag, keep hours

---

### 7. Re-Evaluate GPA Trend Feature ⭐⭐
**Impact:** +0.02-0.05 R² if missingness is fixable
**Effort:** 4 hours
**Why Useful:** "Upward trend" is strong resilience signal

**Currently:** Dropped due to >70% missing (see `config.py` line 148)

**Investigation needed:**
1. Check raw data quality in "12. GPA Trend.xlsx"
2. If missingness is consistent (e.g., only pre-2023), impute with mode
3. If truly 70% missing, keep dropped

---

## Low-Priority Nice-to-Haves (Backlog)

### 8. Secondary Essay Metrics ⭐
**Impact:** +0.02-0.05 R²
**Effort:** 2 hours
**Features:** Response rate (% of 6 essays submitted), avg length, keyword density

### 9. Experience Description Text Mining ⭐
**Impact:** +0.01-0.03 R²
**Effort:** 1 day
**Features:** Leadership keywords, publication keywords, avg description length

### 10. Rubric Approximation Experiment 🔬
**Impact:** Potential 100x cost reduction ($943 → $10/year) if R² > 0.6
**Effort:** 2-3 days (research project)
**Risk:** High - may not work (rubric R² approximation might be <0.5)

**Feasibility study required before implementation.**

---

## Production Deployment Checklist

**Before deploying score-only pipeline:**

- [ ] GPA and MCAT extracted and validated
- [ ] Redundant features dropped from config
- [ ] Drift detection implemented and tested
- [ ] Training statistics saved with model artifact
- [ ] LLM rubric scoring integrated (mandatory)
- [ ] API endpoint built with confidence scoring
- [ ] Dashboard monitoring (mean score, tier distribution, drift alerts)
- [ ] Fallback plan if API down (NLP features or manual review queue)
- [ ] Stakeholder sign-off on tier thresholds (currently [6.25, 12.5, 18.75])

**Estimated total effort:** 1-2 weeks for critical path (items 1-4)

---

## Key Metrics to Monitor in Production

**Pre-Scoring (Drift Detection):**
- % features with K-S test p < 0.05 (alert if >20%)
- Mean shift per feature (alert if >2σ from training)

**Post-Scoring (Quality Assurance):**
- Mean predicted score (expected: 15.5 ± 2.0)
- % applicants in tier 3 (expected: 18-25%)
- Gate rejection rate (expected: 85-95%)
- Mean rubric score (expected: 3.8 ± 0.4)

**Annual Retraining Triggers:**
- Any metric outside ±2σ for 2+ consecutive years
- Major AAMC policy changes
- LLM rubric prompt updates
- Stakeholder feedback on prediction quality

---

## Questions for Stakeholders

1. **GPA/MCAT Extraction:** Can we access "5. Academic Records.xlsx"? What are the exact column names for GPA and MCAT?

2. **Rubric Scoring Budget:** Is $943/year acceptable for LLM rubric scoring? (Alternative: $85/year with GPT-3.5, but quality loss unknown.)

3. **Tier Thresholds:** Current thresholds [6.25, 12.5, 18.75] are from research prototype. Should we recalibrate after GPA/MCAT features added?

4. **Drift Monitoring:** Who should receive drift alerts? What's the escalation process if >20% features drift?

5. **Coverage Target:** Current two-stage model has 2.1% coverage (only 2% of high-scorers selected). Is this acceptable, or should we relax gate threshold to 10-15%?

---

## Contact

**For technical questions:** Data Science Team
**For deployment timeline:** Project Lead
**For stakeholder decisions:** Admissions Committee

**Report prepared:** February 13, 2026
