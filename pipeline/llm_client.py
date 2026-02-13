"""Unified Azure OpenAI client for rubric scoring.

Provides the `llm_call(system, user) -> str` callable that rubric scorers expect.
Uses Azure OpenAI with JSON mode, exponential backoff retry, and thread-safe instantiation.

All configuration is loaded from .env file at the project root:
    AZURE_OPENAI_API_KEY      - Your Azure OpenAI subscription key
    AZURE_OPENAI_ENDPOINT     - Azure endpoint URL
    AZURE_OPENAI_DEPLOYMENT   - Model deployment name (default: gpt-4.1)
    AZURE_OPENAI_API_VERSION  - API version (default: 2025-01-01-preview)

Usage:
    from pipeline.llm_client import create_llm_call

    llm_call = create_llm_call()
    response = llm_call("You are a reviewer.", "Score this applicant...")
"""

import json
import logging
import os
from pathlib import Path

import tenacity
from dotenv import load_dotenv
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def create_llm_call(
    api_key: str | None = None,
    endpoint: str | None = None,
    deployment: str | None = None,
    api_version: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 800,
):
    """Create a provider-agnostic LLM callable for rubric scoring.

    Returns a function with signature: (system: str, user: str) -> str

    All parameters fall back to .env / environment variables if not provided.
    Includes exponential backoff retry with 5 attempts for transient errors.
    Forces JSON mode for structured output.
    """
    resolved_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
    resolved_endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
    resolved_deployment = deployment or os.environ.get(
        "AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"
    )
    resolved_api_version = api_version or os.environ.get(
        "AZURE_OPENAI_API_VERSION", "2025-01-01-preview"
    )

    if not resolved_key:
        raise ValueError(
            "Azure OpenAI API key required. Set AZURE_OPENAI_API_KEY in .env "
            "or pass api_key parameter."
        )
    if not resolved_endpoint:
        raise ValueError(
            "Azure OpenAI endpoint required. Set AZURE_OPENAI_ENDPOINT in .env "
            "or pass endpoint parameter."
        )

    client = AzureOpenAI(
        api_version=resolved_api_version,
        azure_endpoint=resolved_endpoint,
        api_key=resolved_key,
    )
    model = resolved_deployment

    logger.info(
        "Azure OpenAI client: endpoint=%s deployment=%s api_version=%s",
        resolved_endpoint, model, resolved_api_version,
    )

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=60),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type(Exception),
        before_sleep=lambda rs: logger.warning(
            "Retry %d/5 after %s", rs.attempt_number, rs.outcome.exception()
        ),
    )
    def llm_call(system: str, user: str) -> str:
        """Call Azure OpenAI and return the JSON text response.

        Enforces JSON mode and validates response is parseable.
        Retries with exponential backoff on transient errors.
        """
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            response_format={"type": "json_object"},
            seed=42,  # Deterministic for reproducibility
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Empty response from API")

        # Validate JSON before returning
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON from API: %s\nContent: %s", e, content[:500])
            raise

        return content

    return llm_call
