# Medical School Applicant Rubric Scores - Statistical Audit Report

**Dataset:** `/Users/JCR/Desktop/rmc_every/data/cache/rubric_scores.json`
**Analysis Date:** 2026-02-13
**Total Applicants:** 1,300

---

## Executive Summary

This dataset contains LLM-derived rubric scores for 1,300 medical school applicants across 30 scoring dimensions. The scoring system uses a mixed approach with:

- 9 binary presence indicators (0/1)
- 21 continuous scales (0-5) with varying distributions

Key findings reveal extensive multicollinearity between personal quality dimensions (r > 0.97), suggesting potential scoring redundancy. Additionally, 10 dimensions show bimodal distributions with >60% zero values, indicating potential missing data patterns where 0 may represent "not applicable" rather than "poor performance."

---

## 1. Dataset Overview

### Total Applicants Scored
**N = 1,300 applicants**

### Missing Values
**NONE - 100% complete data across all 30 dimensions**

This is unusual for real-world data and may indicate:
- Zero values used to represent missing/not applicable data
- Automated scoring with default values
- Pre-cleaned dataset

---

## 2. Scoring Dimensions (All 30 Dimensions)

### Personal Quality Dimensions (7)
1. `writing_quality`
2. `authenticity_and_self_awareness`
3. `mission_alignment_service_orientation`
4. `adversity_resilience`
5. `motivation_depth`
6. `intellectual_curiosity`
7. `maturity_and_reflection`

### Binary Presence Indicators (9)
8. `has_direct_patient_care`
9. `has_volunteering`
10. `has_community_service`
11. `has_shadowing`
12. `has_clinical_experience`
13. `has_leadership`
14. `has_research`
15. `has_military_service`
16. `has_honors`

### Experience Depth Ratings (8)
17. `direct_patient_care_depth`
18. `volunteering_depth`
19. `community_service_depth`
20. `shadowing_depth`
21. `clinical_experience_depth`
22. `leadership_depth_and_progression`
23. `research_depth_and_output`
24. `honors_significance`

### Holistic Assessment Dimensions (6)
25. `meaningful_vs_checkbox`
26. `personal_attributes_insight`
27. `adversity_response_quality`
28. `reflection_depth`
29. `healthcare_experience_quality`
30. `research_depth`

---

## 3. Score Ranges and Distributions

### Binary Indicators (9 dimensions)
All use **0/1 scale** where 1 = present, 0 = absent

| Dimension | % Present (=1) | % Absent (=0) |
|-----------|----------------|---------------|
| has_clinical_experience | 94.8% | 5.2% |
| has_community_service | 94.6% | 5.4% |
| has_direct_patient_care | 93.8% | 6.2% |
| has_volunteering | 94.2% | 5.8% |
| has_leadership | 92.1% | 7.9% |
| has_research | 91.1% | 8.9% |
| has_shadowing | 85.9% | 14.1% |
| has_honors | 60.3% | 39.7% |
| **has_military_service** | **0.9%** | **99.1%** |

### Continuous Scales (0-5)

#### High-Functioning Dimensions (mean > 3.5)
| Dimension | Min | Max | Mean | Std | Primary Values |
|-----------|-----|-----|------|-----|----------------|
| community_service_depth | 0 | 5 | 3.95 | 1.11 | 60% scored 4 |
| clinical_experience_depth | 0 | 5 | 3.95 | 1.05 | 67% scored 4 |
| mission_alignment_service_orientation | 0 | 5 | 3.89 | 1.33 | 43% scored 5 |
| direct_patient_care_depth | 0 | 5 | 3.77 | 1.08 | 74% scored 4 |
| leadership_depth_and_progression | 0 | 5 | 3.77 | 1.28 | 46% scored 4 |
| writing_quality | 0 | 5 | 3.66 | 1.04 | 57% scored 4 |
| research_depth_and_output | 0 | 5 | 3.51 | 1.35 | 40% scored 4 |
| volunteering_depth | 0 | 5 | 3.46 | 1.06 | 53% scored 4 |
| adversity_resilience | 0 | 5 | 3.37 | 1.14 | 38% scored 4 |
| adversity_response_quality | 0 | 5 | 3.34 | 0.98 | 43% scored 3 |

#### Low-Functioning Dimensions (mean < 2.0)
| Dimension | Min | Max | Mean | Std | Primary Values |
|-----------|-----|-----|------|-----|----------------|
| honors_significance | 0 | 5 | 1.90 | 1.68 | 39% scored 0 |
| meaningful_vs_checkbox | 0 | 5 | 1.91 | 2.41 | **61% scored 0** |
| authenticity_and_self_awareness | 0 | 5 | 1.74 | 2.22 | **61% scored 0** |
| maturity_and_reflection | 0 | 5 | 1.74 | 2.22 | **61% scored 0** |
| motivation_depth | 0 | 5 | 1.73 | 2.20 | **61% scored 0** |
| reflection_depth | 0 | 5 | 1.58 | 2.02 | **61% scored 0** |
| personal_attributes_insight | 0 | 5 | 1.56 | 1.99 | **61% scored 0** |
| intellectual_curiosity | 0 | 5 | 1.47 | 1.89 | **61% scored 0** |
| healthcare_experience_quality | 0 | 5 | 1.41 | 1.84 | **61% scored 0** |
| research_depth | 0 | 5 | 1.13 | 1.40 | 55% scored 0 |

---

## 4. Scale Type Classification

### Binary (0/1) - 9 dimensions
All "has_" prefix dimensions represent presence/absence of activity type.

### Modified 0-5 Scale - 21 dimensions
These appear to be 1-5 ordinal scales where **0 = missing/not applicable**:

- Most show gaps at value 1 (appears rarely)
- Strong bimodal pattern: either 0 or 3-5
- The "0" values likely represent "not scored" rather than "poor quality"

**Evidence:**
- `writing_quality`: No 1s, only {0, 2, 3, 4, 5}
- `authenticity_and_self_awareness`: No 1s or 2s, only {0, 3, 4, 5}
- `motivation_depth`: No 1s or 2s, only {0, 3, 4, 5}

This suggests the actual scoring rubric is **1-5** with 0 added as a placeholder for unanswered/not applicable items.

---

## 5. Binary vs Continuous Dimension Analysis

### Binary Dimensions (0/1)
All 9 "has_" dimensions are true binary indicators:

```
has_direct_patient_care          94% have it
has_volunteering                 94% have it
has_community_service            95% have it
has_shadowing                    86% have it
has_clinical_experience          95% have it
has_leadership                   92% have it
has_research                     91% have it
has_military_service              1% have it (rare)
has_honors                       60% have it
```

### Pseudo-Binary Dimensions (Bimodal 0 vs High)
6 dimensions show bimodal distributions suggesting they function more like binary indicators than continuous scales:

| Dimension | % Zeros | % High (4-5) | % Middle (1-3) |
|-----------|---------|--------------|----------------|
| meaningful_vs_checkbox | 61.3% | 38.7% | 0.0% |
| authenticity_and_self_awareness | 61.3% | 38.6% | 0.1% |
| motivation_depth | 61.3% | 38.5% | 0.2% |
| maturity_and_reflection | 61.3% | 38.6% | 0.1% |
| personal_attributes_insight | 61.4% | 36.5% | 2.1% |
| reflection_depth | 61.4% | 36.6% | 2.0% |

**Interpretation:** These dimensions appear to indicate whether certain essay prompts/sections were completed. The exact 61% with zeros suggests a subset of applicants (797 out of 1,300) did not complete certain application components.

---

## 6. Missing Values Analysis

### No Explicit Missing Values
All 30 dimensions have complete data (0% missing) for all 1,300 applicants.

### Implicit Missing Values (Zeros as Placeholders)
10 dimensions have >50% zero values:

| Dimension | % Zeros | Interpretation |
|-----------|---------|----------------|
| has_military_service | 99.1% | Legitimately rare |
| authenticity_and_self_awareness | 61.3% | Likely missing/not applicable |
| motivation_depth | 61.3% | Likely missing/not applicable |
| intellectual_curiosity | 61.3% | Likely missing/not applicable |
| maturity_and_reflection | 61.3% | Likely missing/not applicable |
| meaningful_vs_checkbox | 61.3% | Likely missing/not applicable |
| personal_attributes_insight | 61.4% | Likely missing/not applicable |
| reflection_depth | 61.4% | Likely missing/not applicable |
| healthcare_experience_quality | 61.4% | Likely missing/not applicable |
| research_depth | 54.6% | Legitimately low research activity |

**Pattern:** Exactly 797 applicants (61.3%) have zeros across 6 dimensions simultaneously, suggesting these applicants may have used a different application format or skipped optional essay sections.

---

## 7. Correlation Structure

### Extreme Multicollinearity (r > 0.95)

The following dimensions are nearly **perfectly correlated** (r > 0.99), indicating they measure essentially the same construct:

| Dimension Pair | Correlation |
|----------------|-------------|
| authenticity_and_self_awareness ↔ maturity_and_reflection | **0.998** |
| personal_attributes_insight ↔ reflection_depth | **0.993** |
| authenticity_and_self_awareness ↔ motivation_depth | **0.993** |
| motivation_depth ↔ maturity_and_reflection | **0.992** |
| meaningful_vs_checkbox ↔ personal_attributes_insight | **0.990** |

### Correlation Clusters

#### Cluster 1: Personal Quality Supercluster (r = 0.95-0.99)
All of these dimensions are interchangeable:
- authenticity_and_self_awareness
- maturity_and_reflection
- motivation_depth
- meaningful_vs_checkbox
- personal_attributes_insight
- reflection_depth
- intellectual_curiosity
- healthcare_experience_quality

**Statistical implication:** These 8 dimensions provide NO unique information beyond each other. They appear to be different labels for the same underlying "application quality" factor.

#### Cluster 2: Clinical Experience Bundle (r = 0.80-0.96)
Binary indicators and depth ratings are tightly coupled:
- has_volunteering ↔ has_community_service (r = 0.96)
- has_community_service ↔ has_clinical_experience (r = 0.95)
- has_direct_patient_care ↔ has_clinical_experience (r = 0.90)

**Interpretation:** Applicants with one type of clinical experience typically have all types.

#### Cluster 3: Presence → Depth Correlations (r = 0.80-0.92)
Binary presence strongly predicts depth rating (as expected):

| Presence Indicator | Depth Rating | Correlation |
|--------------------|--------------|-------------|
| has_honors | honors_significance | 0.917 |
| has_direct_patient_care | direct_patient_care_depth | 0.900 |
| has_clinical_experience | clinical_experience_depth | 0.875 |
| has_shadowing | shadowing_depth | 0.849 |
| has_community_service | community_service_depth | 0.852 |
| has_leadership | leadership_depth_and_progression | 0.826 |
| has_research | research_depth_and_output | 0.813 |
| has_volunteering | volunteering_depth | 0.806 |

**Note:** The correlation is not perfect (0.80-0.92 rather than 1.0) because some applicants have the activity but receive low depth scores, and vice versa (depth can be >0 when presence = 0, likely a data inconsistency).

#### Cluster 4: Writing Quality as Proxy for Clinical Experience (r = 0.72-0.81)
Surprisingly, writing quality correlates strongly with clinical activities:
- writing_quality ↔ adversity_response_quality (r = 0.81)
- writing_quality ↔ has_clinical_experience (r = 0.80)
- writing_quality ↔ has_community_service (r = 0.79)

**Interpretation:** Either (1) better writers describe experiences more compellingly, inflating perceived quality, or (2) more experienced applicants develop better writing skills.

### Correlations Near Zero (Independent Dimensions)

Very few dimension pairs show r < 0.3:

| Dimension Pair | Correlation |
|----------------|-------------|
| has_military_service ↔ [most dimensions] | < 0.10 |
| research_depth ↔ has_research | 0.24 |
| shadowing_depth ↔ research_depth | 0.08 |

---

## 8. Scoring Schema Determination

### Binary Indicators (9 dimensions)
**Schema: {0, 1}**
- 0 = activity not present
- 1 = activity present

### Continuous Ratings (21 dimensions)
**Schema: {0, 1, 2, 3, 4, 5}**

However, the **actual distribution** suggests:
- **0 = Not applicable / Not scored** (appears in 5-61% of cases)
- **1-5 = Quality rating** where:
  - 1 = Very poor (extremely rare, <1%)
  - 2 = Poor (5-10%)
  - 3 = Average (20-40%)
  - 4 = Good (40-60%)
  - 5 = Excellent (10-30%)

### Evidence for "0 = Not Applicable"

1. **Missing value 1:** Many dimensions skip 1 entirely (e.g., authenticity_and_self_awareness has only {0, 3, 4, 5})

2. **Bimodal distributions:** 6 dimensions show 61% zeros and 39% high values (4-5) with virtually nothing in between

3. **Synchronized zeros:** Exactly 797 applicants (61.3%) have zeros across multiple related dimensions simultaneously

4. **Logical consistency:** It makes no sense that 61% of medical school applicants would receive "very poor" scores on writing quality, authenticity, motivation, etc.

### Recommended Interpretation

Treat 0 as **missing data** rather than "poor performance":

```python
# Convert 0 to NaN for analysis
df_clean = df.replace(0, np.nan)
```

Alternatively, create binary indicators for "was scored" vs "not scored":

```python
df['was_scored_personal_quality'] = (df['authenticity_and_self_awareness'] > 0).astype(int)
```

---

## 9. Data Quality Concerns

### Issue 1: Extreme Redundancy
**Problem:** 8 personal quality dimensions have r > 0.95, meaning they're measuring the exact same thing.

**Impact on analysis:**
- Multicollinearity will destabilize regression models
- Inflates type I error in significance testing
- Wastes degrees of freedom

**Recommendation:**
- Perform Principal Component Analysis (PCA) to create a single "Personal Quality Score"
- Or use only 1-2 representative dimensions (e.g., `meaningful_vs_checkbox`)

### Issue 2: Bimodal "Quality" Scales
**Problem:** 6 dimensions function as binary indicators (0 vs high) rather than continuous scales.

**Impact on analysis:**
- Violates normality assumptions for parametric tests
- Misleading means/standard deviations
- Cannot differentiate quality levels within the scored group

**Recommendation:**
- Convert to binary: `scored_personal_quality = (value > 0)`
- Or analyze only the non-zero subset: `df[df['motivation_depth'] > 0]`

### Issue 3: Presence/Depth Inconsistencies
**Problem:** Some applicants have depth scores >0 when presence indicator = 0, and vice versa.

**Example:**
- 81 applicants have `has_direct_patient_care = 0` but 75 of them have `direct_patient_care_depth = 0` (expected)
- This leaves 6 applicants with depth scores despite no presence indicator

**Recommendation:**
- Enforce logical consistency: `depth = 0 if presence = 0`
- Or investigate whether depth can be inferred without explicit presence

### Issue 4: Zero-Inflation Bias
**Problem:** Using 0 for "not applicable" artificially lowers means and inflates variance.

**Impact on analysis:**
- Misleading summary statistics
- Biased correlation estimates
- Incorrect model predictions

**Recommendation:**
- Recode 0 → NA before calculating statistics
- Or use zero-inflated models (e.g., zero-inflated Poisson regression)

---

## 10. Recommended Analysis Approaches

### Option A: Dimensionality Reduction
```python
from sklearn.decomposition import PCA

# Create composite scores
personal_quality_dims = [
    'authenticity_and_self_awareness',
    'motivation_depth',
    'intellectual_curiosity',
    'maturity_and_reflection',
    'meaningful_vs_checkbox',
    'personal_attributes_insight',
    'reflection_depth',
    'healthcare_experience_quality'
]

# PCA on non-zero values only
subset = df[personal_quality_dims].replace(0, np.nan).dropna()
pca = PCA(n_components=1)
df['personal_quality_score'] = pca.fit_transform(subset)
```

### Option B: Separate "Scored" Group Analysis
```python
# Identify applicants who completed optional sections
df['completed_personal_essays'] = (df['authenticity_and_self_awareness'] > 0).astype(int)

# Analyze scored group separately
scored_subset = df[df['completed_personal_essays'] == 1]
```

### Option C: Factor Analysis
```python
from sklearn.decomposition import FactorAnalysis

# Identify latent factors
fa = FactorAnalysis(n_components=3)
factors = fa.fit_transform(df[dimensions])

# Suggested factors:
# Factor 1: Personal Quality (8 dimensions)
# Factor 2: Clinical Experience (13 dimensions)
# Factor 3: Research/Honors (4 dimensions)
```

---

## 11. Summary Statistics Table

| Dimension Type | Count | Mean Score | Score Range | Notes |
|----------------|-------|------------|-------------|-------|
| Binary Indicators | 9 | 0.78 | 0-1 | 78% average presence rate |
| High-Quality Ratings | 10 | 3.66 | 0-5 | Mean >3.3, mostly scored 3-5 |
| Low-Quality Ratings | 10 | 1.64 | 0-5 | Mean <2.0, 60% zeros |
| Honors Significance | 1 | 1.90 | 0-5 | 40% have no honors |

---

## 12. Key Takeaways

1. **1,300 applicants scored** across 30 dimensions with zero explicit missing values

2. **Two application cohorts exist:**
   - 503 applicants (39%) with full scoring across all dimensions
   - 797 applicants (61%) missing personal quality dimensions (zeros)

3. **Scoring uses 0-5 scale** but 0 represents "not applicable" rather than poor quality:
   - Binary indicators: true 0/1
   - Continuous scales: 0 = NA, 1-5 = quality rating

4. **Extreme redundancy** in personal quality dimensions (r = 0.95-0.99):
   - 8 dimensions measure the same underlying construct
   - Can be reduced to 1-2 representative scores

5. **Clinical experience dimensions** form a tight cluster (r = 0.70-0.96):
   - Applicants typically have all or none
   - Presence strongly predicts depth

6. **Writing quality** surprisingly correlates with clinical experience (r = 0.72-0.81):
   - May reflect better communication by experienced applicants
   - Or halo effect from reviewers

7. **Bimodal distributions** in 6 dimensions indicate binary yes/no completion rather than continuous quality

8. **No true missing values** but 10 dimensions have >50% zeros suggesting implicit missing data

---

## 13. Recommendations for Analysis

### Immediate Actions
1. **Recode zeros to NA** for dimensions with >50% zeros
2. **Create composite scores** using PCA/Factor Analysis for redundant dimensions
3. **Separate cohorts** for applicants with vs without personal quality scores
4. **Validate presence/depth consistency** and resolve conflicts

### Statistical Modeling
- Use **zero-inflated models** if keeping zeros in the data
- Apply **multiple imputation** if treating zeros as missing
- Check for **multicollinearity** (VIF) before regression
- Use **robust standard errors** to account for clustering

### Reporting
- Report statistics separately for:
  - Full cohort (N=1,300)
  - Scored cohort (N=503)
  - Clinical experience dimensions (always scored)
  - Personal quality dimensions (61% missing)

---

## Appendix: Correlation Matrix

Full correlation matrix saved to: `/Users/JCR/Desktop/rmc_every/data/cache/correlation_matrix.csv`

Top 20 correlations (all r > 0.85):

1. authenticity_and_self_awareness ↔ maturity_and_reflection (0.998)
2. personal_attributes_insight ↔ reflection_depth (0.993)
3. authenticity_and_self_awareness ↔ motivation_depth (0.993)
4. motivation_depth ↔ maturity_and_reflection (0.992)
5. meaningful_vs_checkbox ↔ personal_attributes_insight (0.990)
6. motivation_depth ↔ meaningful_vs_checkbox (0.990)
7. authenticity_and_self_awareness ↔ meaningful_vs_checkbox (0.989)
8. maturity_and_reflection ↔ meaningful_vs_checkbox (0.989)
9. meaningful_vs_checkbox ↔ reflection_depth (0.988)
10. maturity_and_reflection ↔ personal_attributes_insight (0.986)
11. authenticity_and_self_awareness ↔ personal_attributes_insight (0.986)
12. maturity_and_reflection ↔ reflection_depth (0.985)
13. motivation_depth ↔ personal_attributes_insight (0.984)
14. authenticity_and_self_awareness ↔ reflection_depth (0.984)
15. motivation_depth ↔ reflection_depth (0.984)
16. motivation_depth ↔ intellectual_curiosity (0.978)
17. intellectual_curiosity ↔ meaningful_vs_checkbox (0.978)
18. intellectual_curiosity ↔ maturity_and_reflection (0.974)
19. authenticity_and_self_awareness ↔ intellectual_curiosity (0.973)
20. intellectual_curiosity ↔ personal_attributes_insight (0.971)

---

**Analysis completed:** 2026-02-13
**Tools used:** Python 3, pandas, numpy, scipy
**Analyst:** Claude Opus 4.6 (Data Scientist Specialization)
