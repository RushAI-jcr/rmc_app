"""Configuration and consistency tests from audit findings P3-016, P3-022."""

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# P3-016: score_to_tier must exist in one location
# ---------------------------------------------------------------------------

class TestScoreToTier:
    """score_to_tier function correctness and single-source-of-truth."""

    def test_boundary_values(self) -> None:
        from pipeline.config import score_to_tier, SCORE_BUCKET_THRESHOLDS

        # Below first threshold -> tier 0
        assert score_to_tier(0.0) == 0
        assert score_to_tier(SCORE_BUCKET_THRESHOLDS[0] - 0.01) == 0

        # At first threshold -> tier 1
        assert score_to_tier(SCORE_BUCKET_THRESHOLDS[0]) == 1

        # At second threshold -> tier 2
        assert score_to_tier(SCORE_BUCKET_THRESHOLDS[1]) == 2

        # At third threshold -> tier 3
        assert score_to_tier(SCORE_BUCKET_THRESHOLDS[2]) == 3

        # Maximum score -> tier 3
        assert score_to_tier(25.0) == 3

    def test_monotonically_increasing(self) -> None:
        """Higher scores should never produce lower tiers."""
        from pipeline.config import score_to_tier

        prev_tier = 0
        for score in [float(x) / 10 for x in range(0, 251)]:
            tier = score_to_tier(score)
            assert tier >= prev_tier, f"Tier decreased at score {score}: {prev_tier} -> {tier}"
            prev_tier = tier


# ---------------------------------------------------------------------------
# P3-022: Feature display names must cover all features
# ---------------------------------------------------------------------------

class TestFeatureDisplayNames:
    """FEATURE_DISPLAY_NAMES should cover all model features."""

    def test_all_structured_features_have_display_names(self) -> None:
        from pipeline.config import STRUCTURED_FEATURES, FEATURE_DISPLAY_NAMES

        missing = [f for f in STRUCTURED_FEATURES if f not in FEATURE_DISPLAY_NAMES]
        assert not missing, f"Structured features without display names: {missing}"

    def test_all_engineered_features_have_display_names(self) -> None:
        from pipeline.config import ENGINEERED_FEATURES, FEATURE_DISPLAY_NAMES

        missing = [f for f in ENGINEERED_FEATURES if f not in FEATURE_DISPLAY_NAMES]
        assert not missing, f"Engineered features without display names: {missing}"

    def test_all_rubric_dims_have_display_names(self) -> None:
        from pipeline.config import ALL_RUBRIC_DIMS, FEATURE_DISPLAY_NAMES

        missing = [d for d in ALL_RUBRIC_DIMS if d not in FEATURE_DISPLAY_NAMES]
        assert not missing, f"Rubric dims without display names: {missing}"

    def test_prettify_fallback(self) -> None:
        from pipeline.config import prettify

        # Known name
        assert prettify("writing_quality") == "Writing Quality"
        # Unknown name falls back to title-case
        assert prettify("some_unknown_feature") == "Some Unknown Feature"


# ---------------------------------------------------------------------------
# Dimension consistency: config dims match prompt definitions
# ---------------------------------------------------------------------------

class TestDimensionConsistency:
    """Config dimensions should match rubric prompt keys."""

    def test_ps_dims_not_empty(self) -> None:
        from pipeline.config import PS_DIMS
        assert len(PS_DIMS) == 7

    def test_experience_quality_dims_not_empty(self) -> None:
        from pipeline.config import EXPERIENCE_QUALITY_DIMS
        assert len(EXPERIENCE_QUALITY_DIMS) == 9

    def test_secondary_dims_not_empty(self) -> None:
        from pipeline.config import SECONDARY_DIMS
        assert len(SECONDARY_DIMS) == 5

    def test_all_rubric_dims_is_union(self) -> None:
        from pipeline.config import ALL_RUBRIC_DIMS, PS_DIMS, EXPERIENCE_QUALITY_DIMS, SECONDARY_DIMS
        assert ALL_RUBRIC_DIMS == PS_DIMS + EXPERIENCE_QUALITY_DIMS + SECONDARY_DIMS

    def test_no_duplicate_dims(self) -> None:
        from pipeline.config import ALL_RUBRIC_DIMS
        assert len(ALL_RUBRIC_DIMS) == len(set(ALL_RUBRIC_DIMS)), "Duplicate rubric dimensions"

    def test_rubric_prompts_match_config(self) -> None:
        """If rubric_prompts_v2 exists, its keys must match config dims."""
        try:
            import pipeline.rubric_prompts_v2 as rp
        except ImportError:
            pytest.skip("rubric_prompts_v2 not available")

        from pipeline.config import PS_DIMS
        # Check whichever prompt dict exists
        prompt_keys = set()
        for attr in ["PS_RUBRIC_PROMPTS", "PS_PROMPTS"]:
            if hasattr(rp, attr):
                prompt_keys = set(getattr(rp, attr).keys())
                break
        if prompt_keys:
            assert prompt_keys == set(PS_DIMS)


# ---------------------------------------------------------------------------
# Import validation
# ---------------------------------------------------------------------------

class TestImports:
    """All modules should import cleanly."""

    def test_pipeline_config_imports(self) -> None:
        from pipeline import config  # noqa: F401

    def test_pipeline_feature_engineering_imports(self) -> None:
        from pipeline import feature_engineering  # noqa: F401

    def test_pipeline_model_verification_imports(self) -> None:
        from pipeline import model_verification  # noqa: F401

    def test_pipeline_score_pipeline_imports(self) -> None:
        from pipeline import score_pipeline  # noqa: F401
