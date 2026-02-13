"""Feature pipeline tests from audit findings P2-011, P3-015, P3-019."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pipeline.config import ID_COLUMN, ENGINEERED_FEATURES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_df(n: int = 50) -> pd.DataFrame:
    """Create a minimal DataFrame with columns needed by FeaturePipeline."""
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        ID_COLUMN: range(1000, 1000 + n),
        "Exp_Hour_Total": rng.uniform(0, 5000, n),
        "Exp_Hour_Research": rng.uniform(0, 2000, n),
        "Exp_Hour_Volunteer_Med": rng.uniform(0, 1000, n),
        "Exp_Hour_Volunteer_Non_Med": rng.uniform(0, 1000, n),
        "Exp_Hour_Employ_Med": rng.uniform(0, 1000, n),
        "Exp_Hour_Shadowing": rng.uniform(0, 500, n),
        "Comm_Service_Total_Hours": rng.uniform(0, 500, n),
        "HealthCare_Total_Hours": rng.uniform(0, 2000, n),
        "Num_Languages": rng.integers(1, 5, n),
        "Parent_Max_Education_Ordinal": rng.integers(0, 7, n),
        "Num_Dependents": rng.integers(0, 3, n),
        "First_Generation_Ind": rng.choice([0, 1], n),
        "Disadvantaged_Ind": rng.choice([0, 1], n),
        "SES_Value": rng.choice([0, 1], n),
        "Pell_Grant": rng.choice([0, 1], n),
        "Fee_Assistance_Program": rng.choice([0, 1], n),
        "Military_Service": rng.choice([0, 1], n),
        "Childhood_Med_Underserved": rng.choice([0, 1], n),
        "Paid_Employment_BF_18": rng.choice([0, 1], n),
        "Contribution_to_Family": rng.choice([0, 1], n),
        "Employed_Undergrad": rng.choice([0, 1], n),
        "has_direct_patient_care": rng.choice([0, 1], n),
        "has_volunteering": rng.choice([0, 1], n),
        "has_community_service": rng.choice([0, 1], n),
        "has_shadowing": rng.choice([0, 1], n),
        "has_clinical_experience": rng.choice([0, 1], n),
        "has_leadership": rng.choice([0, 1], n),
        "has_research": rng.choice([0, 1], n),
        "has_military_service": rng.choice([0, 1], n),
        "has_honors": rng.choice([0, 1], n),
    })
    return df


# ---------------------------------------------------------------------------
# P2-011: fit_transform must not crash or double-transform
# ---------------------------------------------------------------------------

class TestFitTransformCached:
    """fit_transform() should reuse the cached result from fit(), not re-transform."""

    def test_fit_transform_returns_dataframe(self) -> None:
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        pipe = FeaturePipeline(include_rubric=False)
        result = pipe.fit_transform(df)

        assert isinstance(result, pd.DataFrame)
        assert ID_COLUMN in result.columns
        assert len(result) == len(df)

    def test_fit_transform_matches_separate_fit_then_transform(self) -> None:
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()

        # Method 1: fit_transform
        pipe1 = FeaturePipeline(include_rubric=False)
        result1 = pipe1.fit_transform(df)

        # Method 2: separate fit + transform
        pipe2 = FeaturePipeline(include_rubric=False)
        pipe2.fit(df)
        result2 = pipe2.transform(df)

        # Should produce identical results
        feature_cols = pipe1.feature_columns_
        pd.testing.assert_frame_equal(
            result1[feature_cols].reset_index(drop=True),
            result2[feature_cols].reset_index(drop=True),
        )

    def test_fit_transform_only_transforms_once(self) -> None:
        """Verify _transform_impl is called exactly once during fit_transform."""
        from unittest.mock import patch
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        pipe = FeaturePipeline(include_rubric=False)

        call_count = 0
        original = pipe._transform_impl

        def counting_transform(df_arg: pd.DataFrame) -> pd.DataFrame:
            nonlocal call_count
            call_count += 1
            return original(df_arg)

        with patch.object(pipe, "_transform_impl", side_effect=counting_transform):
            pipe.fit_transform(df)

        assert call_count == 1, f"_transform_impl called {call_count} times (expected 1)"

    def test_cached_result_freed_after_fit_transform(self) -> None:
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        pipe = FeaturePipeline(include_rubric=False)
        pipe.fit_transform(df)

        # Cache should be cleared to free memory
        assert pipe._fitted_transform_result is None


# ---------------------------------------------------------------------------
# P3-015: Shared engineer_composite_features
# ---------------------------------------------------------------------------

class TestSharedCompositeFeatures:
    """engineer_composite_features() must be the single source of truth."""

    def test_produces_all_7_composites(self) -> None:
        from pipeline.feature_engineering import engineer_composite_features

        df = _make_test_df()
        result = engineer_composite_features(df)

        assert ID_COLUMN in result.columns
        for feat in ENGINEERED_FEATURES:
            assert feat in result.columns, f"Missing composite: {feat}"

    def test_pipeline_and_standalone_match(self) -> None:
        """FeaturePipeline composites must match standalone function."""
        from pipeline.feature_engineering import FeaturePipeline, engineer_composite_features

        df = _make_test_df()

        standalone = engineer_composite_features(df)
        pipe = FeaturePipeline(include_rubric=False)
        pipe_result = pipe.fit_transform(df)

        for feat in ENGINEERED_FEATURES:
            pd.testing.assert_series_equal(
                standalone[feat].reset_index(drop=True),
                pipe_result[feat].reset_index(drop=True),
                check_names=False,
                obj=f"Composite feature '{feat}'",
            )

    def test_volunteer_hours_sum(self) -> None:
        """Total_Volunteer_Hours = med + non_med."""
        from pipeline.feature_engineering import engineer_composite_features

        df = pd.DataFrame({
            ID_COLUMN: [1, 2],
            "Exp_Hour_Volunteer_Med": [100.0, 0.0],
            "Exp_Hour_Volunteer_Non_Med": [50.0, 200.0],
        })
        result = engineer_composite_features(df)
        assert list(result["Total_Volunteer_Hours"]) == [150.0, 200.0]

    def test_clinical_ratio(self) -> None:
        """Direct_Care_Ratio = med_employ / (shadowing + med_employ)."""
        from pipeline.feature_engineering import engineer_composite_features

        df = pd.DataFrame({
            ID_COLUMN: [1, 2],
            "Exp_Hour_Shadowing": [100.0, 0.0],
            "Exp_Hour_Employ_Med": [100.0, 0.0],
        })
        result = engineer_composite_features(df)
        assert result["Direct_Care_Ratio"].iloc[0] == pytest.approx(0.5)
        assert result["Direct_Care_Ratio"].iloc[1] == pytest.approx(0.0)

    def test_missing_columns_default_to_zero(self) -> None:
        """Composites should handle missing source columns gracefully."""
        from pipeline.feature_engineering import engineer_composite_features

        df = pd.DataFrame({ID_COLUMN: [1, 2]})
        result = engineer_composite_features(df)

        assert len(result) == 2
        assert result["Total_Volunteer_Hours"].sum() == 0
        assert result["Adversity_Count"].sum() == 0


# ---------------------------------------------------------------------------
# Pipeline save/load round-trip
# ---------------------------------------------------------------------------

class TestPipelineSaveLoad:
    """FeaturePipeline state must survive save/load."""

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        pipe = FeaturePipeline(include_rubric=False)
        result_before = pipe.fit_transform(df)

        save_path = tmp_path / "pipeline.json"
        pipe.save(save_path)

        loaded = FeaturePipeline.load(save_path)
        result_after = loaded.transform(df)

        pd.testing.assert_frame_equal(
            result_before.reset_index(drop=True),
            result_after.reset_index(drop=True),
        )

    def test_save_uses_json_not_pickle(self, tmp_path: Path) -> None:
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        pipe = FeaturePipeline(include_rubric=False)
        pipe.fit(df)

        save_path = tmp_path / "pipeline.json"
        pipe.save(save_path)

        # Should be valid JSON
        with open(save_path) as f:
            state = json.load(f)

        assert "feature_columns_" in state
        assert "numeric_medians_" in state

    def test_demographics_blocked_from_features(self) -> None:
        """Protected demographics must never appear in feature columns."""
        from pipeline.config import DEMOGRAPHICS_FOR_FAIRNESS_ONLY
        from pipeline.feature_engineering import FeaturePipeline

        df = _make_test_df()
        # Add demographics that should be blocked
        df["Gender"] = "Female"
        df["Age"] = 25
        df["Race"] = "White"
        df["Citizenship"] = "US"

        pipe = FeaturePipeline(include_rubric=False)
        pipe.fit_transform(df)

        forbidden = set(pipe.feature_columns_) & DEMOGRAPHICS_FOR_FAIRNESS_ONLY
        assert not forbidden, f"Demographics leaked into features: {forbidden}"
