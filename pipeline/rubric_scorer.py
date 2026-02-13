"""LLM rubric scorer: domain-specific prompts that mirror human reviewer process.

Each experience domain gets a structured prompt that reads the applicant's actual
text (experience descriptions, personal statement, secondary essays) and scores
depth/quality on a 1-5 scale with supporting evidence.

This replaces binary flags (has_research = 0/1) with rich quality scores
(research_depth_and_output = 4, research_publication_quality = 3, etc.)

Design principles:
  - Mirror how a human reviewer reads applications, not how an ML model sees data
  - Score depth and quality, not just presence/absence
  - Extract evidence quotes so committee members can verify
  - Acknowledge that human reviewers have heterogeneity — run multiple passes
  - Structured JSON output for direct use as model features
"""

import json
import logging
from typing import Any

import pandas as pd

from pipeline.config import ID_COLUMN

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring scale (shared across all domains)
# ---------------------------------------------------------------------------

SCALE_DESCRIPTION = """
SCORING SCALE (use for every dimension):
  1 = Minimal/absent — no meaningful evidence of this quality
  2 = Surface-level — mentioned but lacks depth, reflection, or progression
  3 = Solid — clear evidence with some depth; meets expectations
  4 = Strong — sustained engagement, clear growth, thoughtful reflection
  5 = Exceptional — transformative depth, leadership, lasting impact, or distinction
"""

# ---------------------------------------------------------------------------
# System prompt (shared context for all domain scorers)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a medical school admissions reviewer for Rush Medical College.
You are reading one applicant's materials and scoring specific dimensions of their
application. Rush values service to diverse urban communities, grit, and holistic
development — not just academic metrics.

{SCALE_DESCRIPTION}

IMPORTANT RULES:
- Score based ONLY on what is written. Do not infer or assume.
- If a domain has no relevant text, score 1 and note "No evidence provided."
- Provide a 1-2 sentence "evidence" quote or summary supporting your score.
- Be calibrated: a 3 is genuinely solid, a 5 is rare and exceptional.
- Do NOT let writing polish inflate scores. Focus on substance over style.
- Output valid JSON only. No markdown, no commentary outside the JSON.
"""

# ---------------------------------------------------------------------------
# Domain-specific prompts
# ---------------------------------------------------------------------------

DOMAIN_PROMPTS: dict[str, dict[str, str]] = {
    "direct_patient_care": {
        "dimension": "direct_patient_care_depth",
        "display_name": "Direct Patient Care",
        "prompt": """Score the DEPTH and QUALITY of this applicant's direct patient care experience.

A human reviewer reading this would ask:
- Did the applicant have hands-on interaction with patients (not just observation)?
- Was there progression in responsibility over time?
- Does the applicant reflect on what they learned from patients?
- Did they work in settings that exposed them to diverse patient populations?
- Is there evidence of sustained commitment, not just a summer rotation?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{{"direct_patient_care_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "volunteering": {
        "dimension": "volunteering_depth",
        "display_name": "Volunteering",
        "prompt": """Score the DEPTH and QUALITY of this applicant's volunteering experience.

A human reviewer reading this would ask:
- Was the volunteering sustained over time, or one-off events?
- Did the applicant take on increasing responsibility or leadership?
- Is there evidence of genuine impact on the community served?
- Does the applicant reflect on growth from the experience?
- Is this meaningful engagement or resume padding?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{{"volunteering_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "community_service": {
        "dimension": "community_service_depth",
        "display_name": "Community Service",
        "prompt": """Score the DEPTH and QUALITY of this applicant's community service and civic engagement.

A human reviewer reading this would ask:
- Did the applicant serve communities beyond healthcare settings?
- Is there evidence of sustained commitment to a cause or population?
- Did they build relationships within the community, not just deliver services?
- Was there leadership, organizing, or advocacy?
- Does this show alignment with Rush's mission of serving diverse urban communities?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{{"community_service_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "shadowing": {
        "dimension": "shadowing_depth",
        "display_name": "Shadowing",
        "prompt": """Score the DEPTH and QUALITY of this applicant's shadowing and clinical observation experience.

A human reviewer reading this would ask:
- Did the applicant shadow in multiple specialties or settings?
- Is there evidence they actively observed and reflected, not just logged hours?
- Did they gain understanding of the daily realities of physician life?
- Does the description show curiosity and engagement during observations?
- Did shadowing inform their decision to pursue medicine in a specific way?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{{"shadowing_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "clinical_experience": {
        "dimension": "clinical_experience_depth",
        "display_name": "Clinical Experience",
        "prompt": """Score the DEPTH and QUALITY of this applicant's clinical experience (paid or unpaid clinical roles beyond shadowing).

A human reviewer reading this would ask:
- Did the applicant work in clinical settings with real patient interaction?
- Was there progression from basic to more complex responsibilities?
- Did they understand clinical workflows, teamwork, and healthcare delivery?
- Is there evidence of professional development in a clinical environment?
- Does this show readiness for the clinical demands of medical school?

CONTEXT TO READ:
{experience_text}

Respond with JSON:
{{"clinical_experience_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "leadership": {
        "dimension": "leadership_depth_and_progression",
        "display_name": "Leadership",
        "prompt": """Score the DEPTH and PROGRESSION of this applicant's leadership experience.

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
{{"leadership_depth_and_progression": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "research": {
        "dimension": "research_depth_and_output",
        "display_name": "Research Quality & Output",
        "prompt": """Score the DEPTH, QUALITY, and SCHOLARLY OUTPUT of this applicant's research experience.

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
{{"research_depth_and_output": <1-5>, "research_publication_quality": <1-5>, "num_publications_mentioned": <integer>, "evidence": "<supporting quote or summary>"}}""",
    },

    "military_service": {
        "dimension": "military_service_depth",
        "display_name": "Military Service",
        "prompt": """Score the DEPTH and RELEVANCE of this applicant's military service experience.

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
{{"military_service_depth": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },

    "honors": {
        "dimension": "honors_significance",
        "display_name": "Honors & Awards",
        "prompt": """Score the SIGNIFICANCE and RELEVANCE of this applicant's honors and awards.

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
{{"honors_significance": <1-5>, "evidence": "<supporting quote or summary>"}}""",
    },
}

# ---------------------------------------------------------------------------
# Personal statement & secondary essay prompts
# ---------------------------------------------------------------------------

PERSONAL_STATEMENT_PROMPT = """Score the following dimensions from this applicant's personal statement.

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
{{
  "writing_quality": <1-5>,
  "mission_alignment_service_orientation": <1-5>,
  "adversity_resilience": <1-5>,
  "motivation_depth": <1-5>,
  "intellectual_curiosity": <1-5>,
  "maturity_and_reflection": <1-5>,
  "evidence": "<1-2 sentence summary of the strongest signal in this statement>"
}}"""

SECONDARY_ESSAYS_PROMPT = """Score the following dimensions from this applicant's secondary application essays.

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
{{
  "personal_attributes_insight": <1-5>,
  "adversity_response_quality": <1-5>,
  "reflection_depth": <1-5>,
  "healthcare_experience_quality": <1-5>,
  "research_depth": <1-5>,
  "evidence": "<1-2 sentence summary>"
}}"""


# ---------------------------------------------------------------------------
# Helper: gather experience text per domain
# ---------------------------------------------------------------------------

# Map each domain to the experience types (from Exp_Type column) that are relevant
DOMAIN_EXP_TYPES: dict[str, list[str]] = {
    "direct_patient_care": [
        "Physician Shadowing/Clinical Observation",
        "Paid Employment - Medical/Clinical",
        "Community Service/Volunteer - Medical/Clinical",
    ],
    "volunteering": [
        "Community Service/Volunteer - Medical/Clinical",
        "Community Service/Volunteer - Not Medical/Clinical",
    ],
    "community_service": [
        "Community Service/Volunteer - Not Medical/Clinical",
        "Community Service/Volunteer - Medical/Clinical",
    ],
    "shadowing": [
        "Physician Shadowing/Clinical Observation",
    ],
    "clinical_experience": [
        "Paid Employment - Medical/Clinical",
        "Physician Shadowing/Clinical Observation",
    ],
    "leadership": [
        "Leadership - Not Listed Elsewhere",
    ],
    "research": [
        "Research/Lab",
    ],
    "military_service": [
        "Military Service",
    ],
    "honors": [],  # Honors are detected from text, not Exp_Type
}

# Keywords for honors detection (searched in Exp_Name + Exp_Desc)
HONORS_KEYWORDS = [
    "honor", "honours", "dean's list", "cum laude", "magna cum laude",
    "summa cum laude", "phi beta kappa", "award", "scholarship", "fellowship",
    "prize", "recognition", "distinction", "gold medal",
]


def gather_experience_text(
    experiences_df: pd.DataFrame,
    amcas_id: int,
    domain: str,
) -> str:
    """Extract relevant experience text for a specific domain and applicant.

    For most domains, filters by Exp_Type. For honors, searches text content.
    Returns a formatted string of all matching experiences.
    """
    if experiences_df.empty:
        return "No experience records available."

    applicant_exps = experiences_df[experiences_df[ID_COLUMN] == amcas_id]
    if applicant_exps.empty:
        return "No experience records for this applicant."

    exp_type_col = "Exp_Type" if "Exp_Type" in applicant_exps.columns else "exp_type"
    if exp_type_col not in applicant_exps.columns:
        return "Experience type column not found."

    if domain == "honors":
        # Search all experiences for honors keywords
        matches: list[dict[str, object]] = []
        for _, row in applicant_exps.iterrows():
            text_parts = []
            for col in ["Exp_Name", "Exp_Desc"]:
                val = row.get(col)
                if val is not None and pd.notna(val):
                    text_parts.append(str(val))
            combined = " ".join(text_parts).lower()
            if any(kw in combined for kw in HONORS_KEYWORDS):
                matches.append(dict(row))
        if not matches:
            return "No honors or awards found in experience records."
        relevant = pd.DataFrame(matches)
    else:
        # Filter by experience type
        relevant_types = DOMAIN_EXP_TYPES.get(domain, [])
        if not relevant_types:
            return f"No experience type mapping for domain '{domain}'."

        def _type_matches(t: object) -> bool:
            if t is None or (isinstance(t, float) and pd.isna(t)):
                return False
            return any(rt.lower() in str(t).lower() for rt in relevant_types)

        mask = applicant_exps[exp_type_col].apply(_type_matches)
        relevant = applicant_exps[mask]

    if len(relevant) == 0:
        return f"No {domain.replace('_', ' ')} experiences found."

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
            if val is not None and pd.notna(val) and float(val) > 0:
                parts.append(f"{hc}: {val}")

        entries.append("\n".join(parts))

    return "\n---\n".join(entries)


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------


def score_experiences_for_applicant(
    amcas_id: int,
    experiences_df: pd.DataFrame,
    llm_call: Any,  # callable(system: str, user: str) -> str
) -> dict[str, Any]:
    """Score all 9 experience domains for a single applicant.

    Args:
        amcas_id: The applicant's AMCAS ID.
        experiences_df: Full experiences DataFrame (all applicants).
        llm_call: A callable that takes (system_prompt, user_prompt) and returns
                  the LLM's text response. Provider-agnostic.

    Returns:
        Dict with all dimension scores and evidence strings.
    """
    results: dict[str, Any] = {ID_COLUMN: amcas_id}

    for domain, config in DOMAIN_PROMPTS.items():
        experience_text = gather_experience_text(experiences_df, amcas_id, domain)
        user_prompt = config["prompt"].format(experience_text=experience_text)

        try:
            response = llm_call(SYSTEM_PROMPT, user_prompt)
            parsed = json.loads(response)
            for key, value in parsed.items():
                results[key] = value
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(
                "Failed to score %s for applicant %d: %s", domain, amcas_id, e
            )
            results[config["dimension"]] = 0  # 0 = scoring failed, treat as missing
            results[f"{config['dimension']}_evidence"] = f"Scoring error: {e}"

    return results


def score_personal_statement(
    amcas_id: int,
    personal_statement: str,
    llm_call: Any,
) -> dict[str, Any]:
    """Score personal statement dimensions for a single applicant."""
    results: dict[str, Any] = {ID_COLUMN: amcas_id}

    if not personal_statement or personal_statement.strip() == "":
        # No personal statement available
        for dim in [
            "writing_quality", "mission_alignment_service_orientation",
            "adversity_resilience", "motivation_depth",
            "intellectual_curiosity", "maturity_and_reflection",
        ]:
            results[dim] = 0
        results["ps_evidence"] = "No personal statement provided."
        return results

    user_prompt = PERSONAL_STATEMENT_PROMPT.format(
        personal_statement=personal_statement
    )

    try:
        response = llm_call(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(response)
        for key, value in parsed.items():
            results[key] = value
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Failed to score PS for applicant %d: %s", amcas_id, e)
        for dim in [
            "writing_quality", "mission_alignment_service_orientation",
            "adversity_resilience", "motivation_depth",
            "intellectual_curiosity", "maturity_and_reflection",
        ]:
            results[dim] = 0

    return results


def score_secondary_essays(
    amcas_id: int,
    secondary_text: str,
    llm_call: Any,
) -> dict[str, Any]:
    """Score secondary application essay dimensions for a single applicant."""
    results: dict[str, Any] = {ID_COLUMN: amcas_id}

    if not secondary_text or secondary_text.strip() == "":
        for dim in [
            "personal_attributes_insight", "adversity_response_quality",
            "reflection_depth", "healthcare_experience_quality", "research_depth",
        ]:
            results[dim] = 0
        results["secondary_evidence"] = "No secondary essays provided."
        return results

    user_prompt = SECONDARY_ESSAYS_PROMPT.format(secondary_text=secondary_text)

    try:
        response = llm_call(SYSTEM_PROMPT, user_prompt)
        parsed = json.loads(response)
        for key, value in parsed.items():
            results[key] = value
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(
            "Failed to score secondaries for applicant %d: %s", amcas_id, e
        )
        for dim in [
            "personal_attributes_insight", "adversity_response_quality",
            "reflection_depth", "healthcare_experience_quality", "research_depth",
        ]:
            results[dim] = 0

    return results


def score_applicant_full(
    amcas_id: int,
    experiences_df: pd.DataFrame,
    personal_statement: str,
    secondary_text: str,
    llm_call: Any,
) -> dict[str, Any]:
    """Score ALL rubric dimensions for a single applicant.

    Combines experience domain scores, personal statement scores, and
    secondary essay scores into a single dict.
    """
    exp_scores = score_experiences_for_applicant(
        amcas_id, experiences_df, llm_call
    )
    ps_scores = score_personal_statement(amcas_id, personal_statement, llm_call)
    sec_scores = score_secondary_essays(amcas_id, secondary_text, llm_call)

    # Merge all scores (ID_COLUMN appears in each, keep once)
    combined = {**exp_scores}
    for d in [ps_scores, sec_scores]:
        for k, v in d.items():
            if k != ID_COLUMN:
                combined[k] = v

    return combined


def score_batch(
    applicant_ids: list[int],
    experiences_df: pd.DataFrame,
    personal_statements: dict[int, str],
    secondary_texts: dict[int, str],
    llm_call: Any,
    n_passes: int = 1,
) -> pd.DataFrame:
    """Score a batch of applicants across all rubric dimensions.

    Args:
        applicant_ids: List of AMCAS IDs to score.
        experiences_df: Full experiences DataFrame.
        personal_statements: Dict mapping AMCAS ID -> personal statement text.
        secondary_texts: Dict mapping AMCAS ID -> concatenated secondary essay text.
        llm_call: Provider-agnostic LLM callable.
        n_passes: Number of independent scoring passes (default 1).
                  If >1, scores are averaged and spread is reported.

    Returns:
        DataFrame with one row per applicant, all rubric dimension scores.
    """
    all_results = []

    for amcas_id in applicant_ids:
        ps = personal_statements.get(amcas_id, "")
        sec = secondary_texts.get(amcas_id, "")

        if n_passes == 1:
            result = score_applicant_full(
                amcas_id, experiences_df, ps, sec, llm_call
            )
            all_results.append(result)
        else:
            # Multiple passes: average numeric scores, report spread
            pass_results = []
            for _ in range(n_passes):
                result = score_applicant_full(
                    amcas_id, experiences_df, ps, sec, llm_call
                )
                pass_results.append(result)

            # Average numeric fields, keep last evidence
            averaged = {ID_COLUMN: amcas_id}
            numeric_keys = [
                k for k in pass_results[0]
                if k != ID_COLUMN
                and isinstance(pass_results[0][k], (int, float))
                and not k.startswith("num_")
            ]

            for key in numeric_keys:
                values = [r.get(key, 0) for r in pass_results]
                averaged[key] = round(sum(values) / len(values), 1)
                averaged[f"{key}_spread"] = max(values) - min(values)

            # Keep non-numeric fields from last pass
            for key in pass_results[-1]:
                if key not in averaged:
                    averaged[key] = pass_results[-1][key]

            all_results.append(averaged)

        logger.info("Scored applicant %d (%d/%d)", amcas_id, len(all_results), len(applicant_ids))

    return pd.DataFrame(all_results)
