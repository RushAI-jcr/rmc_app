"""
Atomic rubric scorer for medical school holistic review.

Scores each dimension independently (1 API call per dimension) to eliminate
halo effects that caused r > 0.97 multicollinearity in v1.

Architecture:
  - 7 PS dimensions        × 1 call each = 7 calls per applicant (if PS text exists)
  - 5 Secondary dimensions × 1 call each = 5 calls per applicant (if secondary text exists)
  - 9 EXP dimensions       × 1 call each = 9 calls per applicant (if exp text exists)
  - Total: up to 21 calls per applicant

Scale: 1-4 (no neutral midpoint, forces commitment)

Research basis:
  - LLM-Rubric (ACL 2024): atomic scoring eliminates halo effect
  - AutoSCORE (arxiv:2509.21910): evidence extraction before scoring
  - G-Eval (EMNLP 2023): CoT + form-filling
"""

import json
import logging
import time
from typing import Any, Callable

import pandas as pd

from pipeline.rubric_prompts_v2 import (
    EXPERIENCE_PROMPTS,
    PS_DIMENSIONS,
    SECONDARY_DIMENSIONS,
    SECONDARY_PROMPTS,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

# Below this character count, LLM can't meaningfully evaluate the text.
# A single AMCAS experience with title + type + one-sentence description is ~120-150 chars;
# below 100 means the entry is missing its description entirely.
MIN_SCORABLE_TEXT = 100

# Type for the LLM call function: (system_prompt, user_prompt) -> str
LLMCallFn = Callable[[str, str], str]


def _parse_score_json(raw: str, dimension: str) -> dict[str, Any]:
    """Parse LLM JSON response, handling common failure modes.

    Returns dict with at minimum: {"dimension": ..., "score": ..., "reasoning": ...}
    On parse failure, returns score=0 with error info.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]  # remove first line
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        score = data.get("score")
        if not isinstance(score, (int, float)) or score < 1 or score > 4:
            logger.warning(
                "Score out of range for %s: %s, clipping", dimension, score
            )
            score = max(1, min(4, int(score))) if score else 0
            data["score"] = score
        return data
    except (json.JSONDecodeError, TypeError) as e:
        logger.error("JSON parse failed for %s: %s\nRaw: %s", dimension, e, raw[:200])
        return {
            "dimension": dimension,
            "score": 0,
            "reasoning": f"PARSE_ERROR: {e}",
            "evidence_extracted": "",
            "raw_response": raw[:500],
        }


def score_dimension(
    dimension_name: str,
    prompt_template: str,
    text: str,
    llm_call: LLMCallFn,
) -> dict[str, Any]:
    """Score a single dimension for a single applicant.

    Args:
        dimension_name: e.g. "writing_quality"
        prompt_template: prompt string with {text} placeholder
        text: applicant text to evaluate
        llm_call: function(system_prompt, user_prompt) -> str

    Returns:
        Dict with keys: dimension, score, reasoning, evidence_extracted
    """
    if not text or not text.strip():
        return {
            "dimension": dimension_name,
            "score": 0,
            "reasoning": "NO_TEXT: applicant text was empty",
            "evidence_extracted": "",
        }

    stripped_len = len(text.strip())
    if stripped_len < MIN_SCORABLE_TEXT:
        return {
            "dimension": dimension_name,
            "score": 0,
            "reasoning": f"INSUFFICIENT_TEXT: only {stripped_len} chars (minimum {MIN_SCORABLE_TEXT})",
            "evidence_extracted": "",
        }

    # Use .replace() instead of .format() to avoid colliding with JSON
    # braces in the output template (experience prompts go through two
    # format passes: build_experience_prompt + this substitution).
    user_prompt = prompt_template.replace("{text}", text)
    raw_response = llm_call(SYSTEM_PROMPT, user_prompt)
    return _parse_score_json(raw_response, dimension_name)


def score_personal_statement(
    ps_text: str,
    llm_call: LLMCallFn,
) -> dict[str, dict[str, Any]]:
    """Score all 7 PS dimensions atomically (7 sequential API calls).

    Returns:
        Dict mapping dimension_name -> {score, reasoning, evidence_extracted}
    """
    results = {}
    for dim_name, prompt_template in PS_DIMENSIONS:
        logger.info("  Scoring PS dimension: %s", dim_name)
        result = score_dimension(dim_name, prompt_template, ps_text, llm_call)
        results[dim_name] = result
    return results


def score_experience_domain(
    domain_key: str,
    experience_text: str,
    llm_call: LLMCallFn,
) -> dict[str, Any]:
    """Score a single experience domain.

    Returns:
        Dict with keys: dimension, score, reasoning, evidence_extracted
    """
    prompt_template = EXPERIENCE_PROMPTS[domain_key]
    dim_name = f"{domain_key}_depth_and_quality"
    return score_dimension(dim_name, prompt_template, experience_text, llm_call)


def score_all_experiences(
    experience_texts: dict[str, str],
    llm_call: LLMCallFn,
) -> dict[str, dict[str, Any]]:
    """Score all experience domains atomically.

    Args:
        experience_texts: Dict mapping domain_key -> concatenated experience text
        llm_call: LLM call function

    Returns:
        Dict mapping dimension_name -> {score, reasoning, evidence_extracted}
    """
    results = {}
    for domain_key, text in experience_texts.items():
        if domain_key not in EXPERIENCE_PROMPTS:
            logger.warning("Unknown experience domain: %s, skipping", domain_key)
            continue
        dim_name = f"{domain_key}_depth_and_quality"
        logger.info("  Scoring EXP dimension: %s", dim_name)
        result = score_experience_domain(domain_key, text, llm_call)
        results[dim_name] = result
    return results


def score_secondary_essays(
    secondary_text: str,
    llm_call: LLMCallFn,
) -> dict[str, dict[str, Any]]:
    """Score all 5 secondary essay dimensions atomically (5 sequential API calls).

    Returns:
        Dict mapping dimension_name -> {score, reasoning, evidence_extracted}
    """
    results = {}
    for dim_name in SECONDARY_DIMENSIONS:
        logger.info("  Scoring SECONDARY dimension: %s", dim_name)
        prompt_template = SECONDARY_PROMPTS[dim_name]
        result = score_dimension(dim_name, prompt_template, secondary_text, llm_call)
        results[dim_name] = result
    return results


def score_applicant(
    applicant_id: Any,
    ps_text: str | None,
    secondary_text: str | None,
    experience_texts: dict[str, str],
    llm_call: LLMCallFn,
) -> dict[str, Any]:
    """Score a single applicant across all dimensions.

    Args:
        applicant_id: AMCAS ID or similar identifier
        ps_text: full personal statement text (may be None/empty)
        secondary_text: concatenated secondary essay text (may be None/empty)
        experience_texts: dict of domain_key -> experience text
        llm_call: LLM call function

    Returns:
        Dict with all dimension scores, reasoning, and metadata
    """
    logger.info("Scoring applicant %s", applicant_id)
    start = time.time()
    all_scores = {}
    parse_failures = 0
    total_calls = 0

    # --- Personal Statement (7 calls) ---
    if ps_text and ps_text.strip():
        ps_results = score_personal_statement(ps_text, llm_call)
        for dim_name, result in ps_results.items():
            total_calls += 1
            if result["score"] == 0 and "PARSE_ERROR" in result.get("reasoning", ""):
                parse_failures += 1
            all_scores[dim_name] = result
    else:
        logger.warning("Applicant %s: no personal statement text", applicant_id)
        for dim_name, _ in PS_DIMENSIONS:
            all_scores[dim_name] = {
                "dimension": dim_name,
                "score": 0,
                "reasoning": "NO_TEXT: no personal statement available",
                "evidence_extracted": "",
            }

    # --- Secondary Essays (5 calls) ---
    if secondary_text and secondary_text.strip():
        sec_results = score_secondary_essays(secondary_text, llm_call)
        for dim_name, result in sec_results.items():
            total_calls += 1
            if result["score"] == 0 and "PARSE_ERROR" in result.get("reasoning", ""):
                parse_failures += 1
            all_scores[dim_name] = result
    else:
        logger.warning("Applicant %s: no secondary essay text", applicant_id)
        for dim_name in SECONDARY_DIMENSIONS:
            all_scores[dim_name] = {
                "dimension": dim_name,
                "score": 0,
                "reasoning": "NO_TEXT: no secondary essays available",
                "evidence_extracted": "",
            }

    # --- Experience Domains (up to 9 calls) ---
    if experience_texts:
        exp_results = score_all_experiences(experience_texts, llm_call)
        for dim_name, result in exp_results.items():
            total_calls += 1
            if result["score"] == 0 and "PARSE_ERROR" in result.get("reasoning", ""):
                parse_failures += 1
            all_scores[dim_name] = result

    elapsed = time.time() - start
    logger.info(
        "Applicant %s scored in %.1fs (%d calls, %d parse failures)",
        applicant_id,
        elapsed,
        total_calls,
        parse_failures,
    )

    return {
        "applicant_id": applicant_id,
        "scores": {k: v["score"] for k, v in all_scores.items()},
        "details": all_scores,
        "metadata": {
            "total_calls": total_calls,
            "parse_failures": parse_failures,
            "elapsed_seconds": round(elapsed, 1),
            "scorer_version": "v2_atomic_research_grounded",
        },
    }


def score_batch(
    applicants: list[dict[str, Any]],
    llm_call: LLMCallFn,
) -> list[dict[str, Any]]:
    """Score a batch of applicants sequentially.

    Args:
        applicants: list of dicts with keys:
            - applicant_id
            - ps_text (optional)
            - secondary_text (optional)
            - experience_texts: dict of domain_key -> text (optional)
        llm_call: LLM call function

    Returns:
        List of score result dicts (one per applicant)
    """
    results = []
    total_parse_failures = 0
    total_calls = 0

    for i, app in enumerate(applicants):
        logger.info(
            "--- Applicant %d/%d: %s ---",
            i + 1,
            len(applicants),
            app["applicant_id"],
        )
        result = score_applicant(
            applicant_id=app["applicant_id"],
            ps_text=app.get("ps_text"),
            secondary_text=app.get("secondary_text"),
            experience_texts=app.get("experience_texts", {}),
            llm_call=llm_call,
        )
        results.append(result)
        total_parse_failures += result["metadata"]["parse_failures"]
        total_calls += result["metadata"]["total_calls"]

    # Batch-level parse failure rate check
    if total_calls > 0:
        failure_rate = total_parse_failures / total_calls
        logger.info(
            "Batch complete: %d applicants, %d calls, %.1f%% parse failure rate",
            len(applicants),
            total_calls,
            failure_rate * 100,
        )
        if failure_rate > 0.10:
            logger.error(
                "Parse failure rate %.1f%% exceeds 10%% threshold!", failure_rate * 100
            )

    return results
