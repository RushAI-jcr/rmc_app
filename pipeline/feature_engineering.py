"""Feature engineering with fit/transform pattern for leakage-safe pipelines.

The FeaturePipeline class fits imputation statistics on training data only,
then applies identical transformations to test and scoring data.

Public API:
    FeaturePipeline  — fit/transform class (sklearn-style)
"""

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from pipeline.config import (
    ALL_RUBRIC_DIMS,
    PS_DIMS,
    EXPERIENCE_QUALITY_DIMS,
    SECONDARY_DIMS,
    BINARY_FEATURES,
    CACHE_DIR,
    DEMOGRAPHICS_FOR_FAIRNESS_ONLY,
    EXPERIENCE_BINARY_FLAGS,
    ID_COLUMN,
    NUMERIC_FEATURES,
    PROCESSED_DIR,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_binary(series: pd.Series) -> pd.Series:
    """Convert a column to 0/1 integer, handling Yes/No strings."""
    if series.dtype in (int, float, np.int64, np.float64):
        return series.fillna(0).astype(int)
    return series.map(
        lambda x: 1 if str(x).strip().lower().startswith("y") else 0
    )


_BINARY_ALIASES = {
    "Disadvantaged_Ind": ["Disadvantanged_Ind", "Disadvantaged_Ind"],
}


# ---------------------------------------------------------------------------
# FeaturePipeline
# ---------------------------------------------------------------------------


class FeaturePipeline:
    """Fit on training data, transform any dataset consistently.

    This replaces the old scattered extract/engineer/combine functions with
    a single class that learns imputation values during fit() and applies
    them identically during transform().

    Args:
        include_rubric: Whether to load and include LLM rubric features.
        rubric_path: Path to rubric_scores.json (default: CACHE_DIR).

    Fitted attributes (available after fit()):
        numeric_medians_: dict[str, float] — imputation values for numeric features
        feature_columns_: list[str] — ordered list of all feature column names
        rubric_medians_: dict[str, float] — imputation values for rubric zero-as-missing
        is_fitted_: bool — whether fit() has been called
    """

    def __init__(
        self,
        include_rubric: bool = True,
        rubric_path: Path | None = None,
    ) -> None:
        self.include_rubric = include_rubric
        self.rubric_path = rubric_path or (CACHE_DIR / "rubric_scores.json")
        self.is_fitted_: bool = False
        self.numeric_medians_: dict[str, float] = {}
        self.rubric_medians_: dict[str, float] = {}
        self.feature_columns_: list[str] = []
        self._rubric_data: dict[str, dict] | None = None

    def fit(self, df: pd.DataFrame) -> "FeaturePipeline":
        """Fit imputation statistics on training data only.

        Learns:
          - Median values for numeric features (used when NaN)
          - Median values for rubric quality dimensions (used when 0 = missing)
          - Final feature column ordering
        """
        # Learn numeric medians from training data
        self.numeric_medians_ = {}
        for col in NUMERIC_FEATURES:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors="coerce")
                median_val = float(series.median()) if series.notna().any() else 0.0
                self.numeric_medians_[col] = median_val

        # Load rubric data if needed
        if self.include_rubric:
            self._rubric_data = self._load_rubric_json()
            if self._rubric_data:
                # Learn rubric medians from training IDs only
                train_ids = set(df[ID_COLUMN].astype(str).values)
                self.rubric_medians_ = self._compute_rubric_medians(train_ids)

        # Build feature column list by transforming training data
        features_df = self._transform_impl(df)
        self.feature_columns_ = [c for c in features_df.columns if c != ID_COLUMN]

        # Guard: ensure no protected attributes leaked in
        forbidden = set(self.feature_columns_) & DEMOGRAPHICS_FOR_FAIRNESS_ONLY
        if forbidden:
            raise ValueError(
                f"Feature list must not include demographics (fairness-only): {forbidden}"
            )

        self.is_fitted_ = True
        logger.info(
            "FeaturePipeline fitted: %d features, rubric=%s",
            len(self.feature_columns_),
            "yes" if self._rubric_data else "no",
        )
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply fitted transformations to any dataset.

        Returns DataFrame with ID_COLUMN + all feature columns.
        """
        if not self.is_fitted_:
            raise RuntimeError("FeaturePipeline.transform() called before fit()")

        features_df = self._transform_impl(df)

        # Ensure consistent column ordering (add missing cols as 0, drop extras)
        for col in self.feature_columns_:
            if col not in features_df.columns:
                features_df[col] = 0.0

        return features_df[[ID_COLUMN] + self.feature_columns_]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convenience: fit + transform in one call."""
        self.fit(df)
        return self.transform(df)

    def save(self, path: Path) -> None:
        """Persist fitted state to disk."""
        if not self.is_fitted_:
            raise RuntimeError("Cannot save unfitted pipeline")

        state = {
            "include_rubric": self.include_rubric,
            "numeric_medians_": self.numeric_medians_,
            "rubric_medians_": self.rubric_medians_,
            "feature_columns_": self.feature_columns_,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(state, path)
        logger.info("Saved FeaturePipeline to %s (%d features)", path, len(self.feature_columns_))

    @classmethod
    def load(cls, path: Path) -> "FeaturePipeline":
        """Load a previously fitted pipeline from disk."""
        state = joblib.load(path)
        pipe = cls(include_rubric=state["include_rubric"])
        pipe.numeric_medians_ = state["numeric_medians_"]
        pipe.rubric_medians_ = state["rubric_medians_"]
        pipe.feature_columns_ = state["feature_columns_"]
        pipe.is_fitted_ = True

        # Load rubric JSON if needed for transform
        if pipe.include_rubric:
            pipe._rubric_data = pipe._load_rubric_json()

        logger.info("Loaded FeaturePipeline from %s (%d features)", path, len(pipe.feature_columns_))
        return pipe

    # -------------------------------------------------------------------
    # Internal transform implementation
    # -------------------------------------------------------------------

    def _transform_impl(self, df: pd.DataFrame) -> pd.DataFrame:
        """Core transform logic shared by fit() and transform()."""
        structured = self._extract_structured(df)
        engineered = self._engineer_composites(df)
        binary_flags = self._extract_binary_flags(df)

        # Combine structured + engineered + binary flags
        combined = structured.copy()
        for aux_df in [engineered, binary_flags]:
            if not aux_df.empty:
                combined = combined.merge(aux_df, on=ID_COLUMN, how="left", suffixes=("", "_dup"))
                combined = combined.drop(columns=[c for c in combined.columns if c.endswith("_dup")])

        # Add rubric features if available
        if self.include_rubric and self._rubric_data:
            rubric_df = self._build_rubric_features(combined[ID_COLUMN])
            if not rubric_df.empty:
                combined = combined.merge(rubric_df, on=ID_COLUMN, how="left", suffixes=("", "_dup"))
                combined = combined.drop(columns=[c for c in combined.columns if c.endswith("_dup")])

        # Final NaN sweep
        feature_cols = [c for c in combined.columns if c != ID_COLUMN]
        for col in feature_cols:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0.0)

        return combined

    def _extract_structured(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract numeric + binary features from the prepared dataset."""
        features = pd.DataFrame()
        features[ID_COLUMN] = df[ID_COLUMN]

        # Numeric features
        active_numeric = [col for col in NUMERIC_FEATURES if col in df.columns]
        skipped = set(NUMERIC_FEATURES) - set(active_numeric)
        if skipped:
            logger.info("Skipping numeric features not in data: %s", skipped)

        for col in active_numeric:
            series = pd.to_numeric(df[col], errors="coerce")
            # Use fitted median if available, else 0
            fill_val = self.numeric_medians_.get(col, 0.0)
            features[col] = series.fillna(fill_val)

        # Numeric features not in data -> fill with 0
        for col in skipped:
            features[col] = 0.0

        # Binary features with alias handling
        for col in BINARY_FEATURES:
            matched = False
            candidates = _BINARY_ALIASES.get(col, []) + [col]
            for candidate in candidates:
                if candidate in df.columns:
                    features[col] = _to_binary(df[candidate])
                    matched = True
                    break
            if not matched:
                features[col] = 0

        logger.info(
            "Extracted %d structured features for %d applicants",
            len(features.columns) - 1,
            len(features),
        )
        return features

    def _engineer_composites(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create reviewer-aligned composite features."""
        out = pd.DataFrame()
        out[ID_COLUMN] = df[ID_COLUMN]

        # Volunteering composites
        med_vol = df.get("Exp_Hour_Volunteer_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
        non_med_vol = df.get("Exp_Hour_Volunteer_Non_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
        out["Total_Volunteer_Hours"] = med_vol + non_med_vol
        out["Community_Engaged_Ratio"] = np.where(
            out["Total_Volunteer_Hours"] > 0,
            non_med_vol / out["Total_Volunteer_Hours"],
            0.0,
        )

        # Clinical composites
        shadowing = df.get("Exp_Hour_Shadowing", pd.Series(0, index=df.index)).fillna(0).astype(float)
        med_employ = df.get("Exp_Hour_Employ_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
        out["Clinical_Total_Hours"] = shadowing + med_employ
        out["Direct_Care_Ratio"] = np.where(
            out["Clinical_Total_Hours"] > 0,
            med_employ / out["Clinical_Total_Hours"],
            0.0,
        )

        # Adversity count
        grit_cols = ["First_Generation_Ind", "Disadvantaged_Ind", "SES_Value", "Pell_Grant", "Fee_Assistance_Program"]
        adversity_sum = pd.Series(0, index=df.index, dtype=float)
        for col in grit_cols:
            if col in df.columns:
                adversity_sum = adversity_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
        out["Adversity_Count"] = adversity_sum.astype(int)

        # Grit Index (broader)
        grit_extra = ["Paid_Employment_BF_18", "Contribution_to_Family", "Childhood_Med_Underserved"]
        grit_total = adversity_sum.copy()
        for col in grit_extra:
            if col in df.columns:
                grit_total = grit_total + pd.to_numeric(df[col], errors="coerce").fillna(0)
        out["Grit_Index"] = grit_total.astype(int)

        # Experience Diversity
        exp_flag_cols = [
            "has_direct_patient_care", "has_volunteering", "has_community_service",
            "has_shadowing", "has_clinical_experience", "has_leadership",
            "has_research", "has_military_service", "has_honors",
        ]
        diversity_sum = pd.Series(0, index=df.index, dtype=float)
        for col in exp_flag_cols:
            if col in df.columns:
                diversity_sum = diversity_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
        out["Experience_Diversity"] = diversity_sum.astype(int)

        logger.info("Engineered 7 composite features for %d applicants", len(out))
        return out

    def _extract_binary_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract the 9 binary experience flags already derived during ingestion."""
        flag_cols = [col for col in EXPERIENCE_BINARY_FLAGS if col in df.columns]
        missing = set(EXPERIENCE_BINARY_FLAGS) - set(flag_cols)
        if missing:
            logger.warning("Missing binary flag columns: %s", missing)

        flags = df[[ID_COLUMN] + flag_cols].copy()
        for col in EXPERIENCE_BINARY_FLAGS:
            if col not in flags.columns:
                flags[col] = 0

        return flags

    # -------------------------------------------------------------------
    # Rubric score helpers
    # -------------------------------------------------------------------

    def _load_rubric_json(self) -> dict[str, dict] | None:
        """Load v2 rubric scores from cache JSON.

        v2 format: {applicant_id: {scores: {...}, details: {...}, metadata: {...}}}
        Flattens to: {applicant_id: {dimension: score, ...}}
        """
        if not self.rubric_path.exists():
            logger.warning("Rubric scores not found at %s", self.rubric_path)
            return None
        with open(self.rubric_path) as f:
            data = json.load(f)

        # Check if v2 format (nested with "scores" key)
        first_id = next(iter(data))
        first_record = data[first_id]

        if isinstance(first_record, dict) and "scores" in first_record:
            # v2 format — flatten scores dict
            flattened = {}
            for aid, record in data.items():
                flattened[aid] = record.get("scores", {})
            logger.info("Loaded v2 rubric scores for %d applicants", len(flattened))
            return flattened
        else:
            # Already flat format
            logger.info("Loaded rubric scores for %d applicants", len(data))
            return data

    def _compute_rubric_medians(self, train_ids: set[str]) -> dict[str, float]:
        """Compute median of non-zero values for each quality dimension, using training IDs only."""
        if not self._rubric_data:
            return {}

        quality_dims = PS_DIMS + EXPERIENCE_QUALITY_DIMS + SECONDARY_DIMS
        medians: dict[str, float] = {}

        for dim in quality_dims:
            values = []
            for amcas_id, scores in self._rubric_data.items():
                if amcas_id in train_ids:
                    val = scores.get(dim, 0)
                    if val > 0:
                        values.append(val)
            # v2 uses 1-4 scale, median typically 2.5
            medians[dim] = float(np.median(values)) if values else 2.5

        return medians

    def _build_rubric_features(self, ids: pd.Series) -> pd.DataFrame:
        """Build rubric feature DataFrame for given applicant IDs.

        Returns all v2 rubric dimensions (PS + Experience + Secondary) + rubric_scored_flag.
        """
        if not self._rubric_data:
            return pd.DataFrame()

        quality_dims = PS_DIMS + EXPERIENCE_QUALITY_DIMS + SECONDARY_DIMS

        rows = []
        for amcas_id in ids:
            scores = self._rubric_data.get(str(int(amcas_id)), {})
            row = {ID_COLUMN: amcas_id}

            for dim in quality_dims:
                raw_val = scores.get(dim, 0)
                # Treat 0 as missing -> impute with fitted median
                if raw_val > 0:
                    row[dim] = raw_val
                else:
                    row[dim] = self.rubric_medians_.get(dim, 2.5)  # v2 scale 1-4, median 2.5

            # Binary flag: was applicant scored at all
            row["rubric_scored_flag"] = 1 if scores.get("writing_quality", 0) > 0 else 0
            rows.append(row)

        rubric_df = pd.DataFrame(rows)

        # Save raw rubric CSV for reference
        self._save_rubric_csv(ids)

        n_scored = int(rubric_df["rubric_scored_flag"].sum())
        logger.info(
            "Built rubric features: %d dims, %d/%d applicants scored",
            len(quality_dims), n_scored, len(rubric_df),
        )
        return rubric_df

    def _save_rubric_csv(self, ids: pd.Series) -> None:
        """Save raw rubric scores CSV for reference."""
        if not self._rubric_data:
            return

        rows = []
        for amcas_id in ids:
            scores = self._rubric_data.get(str(int(amcas_id)), {})
            row = {ID_COLUMN: amcas_id}
            for dim in ALL_RUBRIC_DIMS:
                row[dim] = scores.get(dim, 0)
            rows.append(row)

        raw_df = pd.DataFrame(rows)
        raw_path = PROCESSED_DIR / "rubric_features_raw_v2.csv"
        raw_df.to_csv(raw_path, index=False)
        logger.info("Saved raw rubric scores to %s", raw_path)
