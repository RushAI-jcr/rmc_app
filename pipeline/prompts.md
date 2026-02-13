# Rubric Scoring Prompts

All prompts used by `pipeline/rubric_scorer.py` to score applicants via GPT-4.1.
Edit any section below, then the pipeline code will need to be updated to match.

---

## Shared: Scoring Scale

Used across every prompt as context for the 1-5 scale.

```
SCORING SCALE (use for every dimension):
  1 = Minimal/absent — no meaningful evidence of this quality
  2 = Surface-level — mentioned but lacks depth, reflection, or progression
  3 = Solid — clear evidence with some depth; meets expectations
  4 = Strong — sustained engagement, clear growth, thoughtful reflection
  5 = Exceptional — transformative depth, leadership, lasting impact, or distinction
```

---

## Shared: System Prompt

Sent as the `system` message for every LLM call.

```
You are a medical school admissions reviewer for Rush Medical College.
You are reading one applicant's materials and scoring specific dimensions of their
application. Rush values service to diverse urban communities, grit, and holistic
development — not just academic metrics.

[SCORING SCALE inserted here]

IMPORTANT RULES:
- Score based ONLY on what is written. Do not infer or assume.
- If a domain has no relevant text, score 1 and note "No evidence provided."
- Provide a 1-2 sentence "evidence" quote or summary supporting your score.
- Be calibrated: a 3 is genuinely solid, a 5 is rare and exceptional.
- Do NOT let writing polish inflate scores. Focus on substance over style.
- Output valid JSON only. No markdown, no commentary outside the JSON.
```

---

## Experience Domain Prompts

Each domain filters the applicant's AMCAS experience entries by `Exp_Type` and sends the matching text to the LLM.

### 1. Direct Patient Care

**Dimension:** `direct_patient_care_depth`
**Experience types matched:** Physician Shadowing/Clinical Observation, Paid Employment - Medical/Clinical, Community Service/Volunteer - Medical/Clinical

```
Score the DEPTH and QUALITY of this applicant's direct patient care experience.

A human reviewer reading this would ask:
- Did the applicant have hands-on interaction with patients (not just observation)?
- Was there progression in responsibility over time?
- Does the applicant reflect on what they learned from patients?
- Did they work in settings that exposed them to diverse patient populations?
- Is there evidence of sustained commitment, not just a summer rotation?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"direct_patient_care_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 2. Volunteering

**Dimension:** `volunteering_depth`
**Experience types matched:** Community Service/Volunteer - Medical/Clinical, Community Service/Volunteer - Not Medical/Clinical

```
Score the DEPTH and QUALITY of this applicant's volunteering experience.

A human reviewer reading this would ask:
- Was the volunteering sustained over time, or one-off events?
- Did the applicant take on increasing responsibility or leadership?
- Is there evidence of genuine impact on the community served?
- Does the applicant reflect on growth from the experience?
- Is this meaningful engagement or resume padding?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"volunteering_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 3. Community Service

**Dimension:** `community_service_depth`
**Experience types matched:** Community Service/Volunteer - Not Medical/Clinical, Community Service/Volunteer - Medical/Clinical

```
Score the DEPTH and QUALITY of this applicant's community service and civic engagement.

A human reviewer reading this would ask:
- Did the applicant serve communities beyond healthcare settings?
- Is there evidence of sustained commitment to a cause or population?
- Did they build relationships within the community, not just deliver services?
- Was there leadership, organizing, or advocacy?
- Does this show alignment with Rush's mission of serving diverse urban communities?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"community_service_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 4. Shadowing

**Dimension:** `shadowing_depth`
**Experience types matched:** Physician Shadowing/Clinical Observation

```
Score the DEPTH and QUALITY of this applicant's shadowing and clinical observation experience.

A human reviewer reading this would ask:
- Did the applicant shadow in multiple specialties or settings?
- Is there evidence they actively observed and reflected, not just logged hours?
- Did they gain understanding of the daily realities of physician life?
- Does the description show curiosity and engagement during observations?
- Did shadowing inform their decision to pursue medicine in a specific way?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"shadowing_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 5. Clinical Experience

**Dimension:** `clinical_experience_depth`
**Experience types matched:** Paid Employment - Medical/Clinical, Physician Shadowing/Clinical Observation

```
Score the DEPTH and QUALITY of this applicant's clinical experience (paid or unpaid clinical roles beyond shadowing).

A human reviewer reading this would ask:
- Did the applicant work in clinical settings with real patient interaction?
- Was there progression from basic to more complex responsibilities?
- Did they understand clinical workflows, teamwork, and healthcare delivery?
- Is there evidence of professional development in a clinical environment?
- Does this show readiness for the clinical demands of medical school?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"clinical_experience_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 6. Leadership

**Dimension:** `leadership_depth_and_progression`
**Experience types matched:** Leadership - Not Listed Elsewhere

```
Score the DEPTH and PROGRESSION of this applicant's leadership experience.

A human reviewer reading this would ask:
- Did the applicant hold positions of genuine responsibility, not just titles?
- Is there evidence of PROGRESSION — growing from participant to leader?
- Did they lead teams, initiatives, or organizations?
- Was there measurable impact from their leadership?
- Did they mentor others or develop new leaders?
- Does the leadership span multiple settings (academic, clinical, community)?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"leadership_depth_and_progression": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 7. Research Quality & Output

**Dimension:** `research_depth_and_output`, `research_publication_quality`, `num_publications_mentioned`
**Experience types matched:** Research/Lab

```
Score the DEPTH, QUALITY, and SCHOLARLY OUTPUT of this applicant's research experience.

A human reviewer reading this would ask:
- Did the applicant contribute meaningfully to the research, or just follow instructions?
- Is there evidence of independent thinking, hypothesis generation, or study design?
- How many publications, posters, or presentations resulted from their work?
- Were publications in peer-reviewed journals? As first author or contributing author?
- Did they present at conferences? Local, regional, or national?
- Is there depth of sustained inquiry, or just brief rotations through multiple labs?
- Does the research show intellectual curiosity and rigor?
- Is the work relevant to clinical medicine, public health, or Rush's mission?

SCORING GUIDANCE FOR RESEARCH:
  1 = No research, or minimal lab assistant role with no output
  2 = Some research exposure but no publications/presentations; limited role
  3 = Meaningful research contribution; 1-2 co-authored publications or conference posters
  4 = Strong research record; multiple publications, first-author work, or significant presentations
  5 = Exceptional; published first-author in peer-reviewed journals, national presentations, independent projects, or funded research

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"research_depth_and_output": <1-5>, "research_publication_quality": <1-5>, "num_publications_mentioned": <integer>, "evidence": "<supporting quote or summary>"}
```

---

### 8. Military Service

**Dimension:** `military_service_depth`
**Experience types matched:** Military Service

```
Score the DEPTH and RELEVANCE of this applicant's military service experience.

A human reviewer reading this would ask:
- What was their role and rank? Did they hold positions of responsibility?
- Is there evidence of leadership, discipline, and service under pressure?
- Did military service expose them to healthcare, public health, or diverse populations?
- Are there transferable skills (teamwork, crisis management, cultural competence)?
- Does the applicant reflect on how military service shaped their path to medicine?

NOTE: If the applicant has no military service, score 1 with "No military service."

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"military_service_depth": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

### 9. Honors & Awards

**Dimension:** `honors_significance`
**Experience types matched:** (keyword search across all experiences for: honor, honours, dean's list, cum laude, magna cum laude, summa cum laude, phi beta kappa, award, scholarship, fellowship, prize, recognition, distinction, gold medal)

```
Score the SIGNIFICANCE and RELEVANCE of this applicant's honors and awards.

A human reviewer reading this would ask:
- Are these competitive, selective awards or participation certificates?
- Are they relevant to medicine, science, service, or leadership?
- Do they demonstrate sustained excellence, not just a single achievement?
- How selective were the honors (department vs. university vs. national)?
- Do they include academic honors (Phi Beta Kappa, cum laude), research awards, service awards, or leadership recognitions?

SCORING GUIDANCE:
  1 = No honors mentioned
  2 = Minor or participation-level recognitions
  3 = Solid academic honors (Dean's List, departmental awards)
  4 = Competitive awards (university-level, named scholarships, research prizes)
  5 = National or highly selective honors (Phi Beta Kappa, Goldwater, published research awards)

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{"honors_significance": <1-5>, "evidence": "<supporting quote or summary>"}
```

---

## Personal Statement Prompt

Scores 6 dimensions from the applicant's AMCAS personal statement.

**Dimensions:** `writing_quality`, `mission_alignment_service_orientation`, `adversity_resilience`, `motivation_depth`, `intellectual_curiosity`, `maturity_and_reflection`

```
Score the following dimensions from this applicant's personal statement.

Read the personal statement as a human reviewer would: looking for authentic voice,
self-awareness, and evidence of the qualities Rush values. Do NOT let writing polish
inflate scores — a plainly written statement with genuine substance scores higher
than an eloquent statement with shallow content.

DIMENSIONS TO SCORE:
1. writing_quality (1-5): Clarity, organization, and coherence of the writing itself.
   NOTE: This is intentionally separated from content. High writing quality + low
   substance scores flags potential SES/coaching advantage.

2. mission_alignment_service_orientation (1-5): Evidence of alignment with Rush's
   mission of serving diverse urban communities. Look for: understanding of health
   disparities, commitment to underserved populations, social determinants awareness,
   desire to practice in urban settings.

3. adversity_resilience (1-5): Evidence of perseverance through significant challenges.
   Look for: sustained effort despite setbacks, recovery from failure, navigating
   systemic barriers, supporting family through hardship. Do NOT require trauma —
   quiet resilience counts.

4. motivation_depth (1-5): Why medicine, and why is it genuine? Look for: specific
   moments of inspiration, understanding of daily realities (not just "I want to
   help people"), nuanced view of healthcare, evidence the decision was tested.

5. intellectual_curiosity (1-5): Evidence of love of learning beyond requirements.
   Look for: independent reading, cross-disciplinary interests, questions asked
   during experiences, curiosity about mechanisms and systems.

6. maturity_and_reflection (1-5): Emotional intelligence and self-awareness.
   Look for: ability to learn from mistakes, nuanced thinking about complex issues,
   understanding of own strengths and limitations, growth over time.

PERSONAL STATEMENT:
{personal_statement}

Respond with JSON:
{
  "writing_quality": <1-5>,
  "mission_alignment_service_orientation": <1-5>,
  "adversity_resilience": <1-5>,
  "motivation_depth": <1-5>,
  "intellectual_curiosity": <1-5>,
  "maturity_and_reflection": <1-5>,
  "evidence": "<1-2 sentence summary of the strongest signal in this statement>"
}
```

---

## Secondary Essays Prompt

Scores 5 dimensions from the applicant's Rush secondary application essays.

**Dimensions:** `personal_attributes_insight`, `adversity_response_quality`, `reflection_depth`, `healthcare_experience_quality`, `research_depth`

```
Score the following dimensions from this applicant's secondary application essays.

Secondary essays reveal how applicants respond to specific prompts. Read them as a
reviewer who has already seen the personal statement and is looking for NEW information
that confirms or challenges initial impressions.

DIMENSIONS TO SCORE:
1. personal_attributes_insight (1-5): Self-awareness about strengths, weaknesses,
   and how personal qualities would contribute to the class. Look for: specificity,
   honesty about limitations, concrete examples.

2. adversity_response_quality (1-5): How the applicant handled a specific challenging
   situation. Look for: what they actually DID (not just felt), what they learned,
   how it changed their approach. Distinguish lived experience from hypothetical.

3. reflection_depth (1-5): Quality of reflection on a formative experience. Look for:
   genuine insight (not cliches), connection to future practice, evidence of growth.

4. healthcare_experience_quality (1-5): Understanding of healthcare from direct
   experience. Look for: nuanced view of clinical realities, patient perspective
   awareness, understanding of team dynamics.

5. research_depth (1-5): Evidence of scholarly engagement from secondary responses.
   Look for: ability to discuss findings meaningfully, understanding of methodology,
   connection between research and clinical questions.

SECONDARY ESSAYS:
{secondary_text}

Respond with JSON:
{
  "personal_attributes_insight": <1-5>,
  "adversity_response_quality": <1-5>,
  "reflection_depth": <1-5>,
  "healthcare_experience_quality": <1-5>,
  "research_depth": <1-5>,
  "evidence": "<1-2 sentence summary>"
}
```

---

## Experience Type Mappings

How each domain filters the AMCAS `Exp_Type` column:

| Domain | Exp_Type Values Matched |
|---|---|
| direct_patient_care | Physician Shadowing/Clinical Observation, Paid Employment - Medical/Clinical, Community Service/Volunteer - Medical/Clinical |
| volunteering | Community Service/Volunteer - Medical/Clinical, Community Service/Volunteer - Not Medical/Clinical |
| community_service | Community Service/Volunteer - Not Medical/Clinical, Community Service/Volunteer - Medical/Clinical |
| shadowing | Physician Shadowing/Clinical Observation |
| clinical_experience | Paid Employment - Medical/Clinical, Physician Shadowing/Clinical Observation |
| leadership | Leadership - Not Listed Elsewhere |
| research | Research/Lab |
| military_service | Military Service |
| honors | (keyword search, not Exp_Type filter) |

## Honors Keywords

Used to search `Exp_Name` and `Exp_Desc` for honors-related experiences:

```
honor, honours, dean's list, cum laude, magna cum laude, summa cum laude,
phi beta kappa, award, scholarship, fellowship, prize, recognition,
distinction, gold medal
```
