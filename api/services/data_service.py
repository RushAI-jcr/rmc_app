"""Load processed data and trained models at API startup."""

import json
import logging
import pickle
from pathlib import Path

import pandas as pd
import numpy as np

from api.config import (
    PROCESSED_DIR,
    MODELS_DIR,
    CACHE_DIR,
    WORKING_PKLS,
    BUCKET_MAP,
    BINARY_FEATURES,
    ID_COLUMN,
)
from pipeline.feature_engineering import engineer_composite_features

logger = logging.getLogger(__name__)


class DataStore:
    """Holds all loaded data and models in memory."""

    def __init__(self) -> None:
        self.master_data: pd.DataFrame = pd.DataFrame()
        self.model_results: dict[str, dict] = {}
        self.rubric_scores: dict = {}
        self.rubric_details: dict = {}
        self.rubric_features: pd.DataFrame = pd.DataFrame()
        self.experiences_data: pd.DataFrame = pd.DataFrame()
        self._prediction_cache: dict[str, list[dict]] = {}
        self._test_predictions_cache: dict[str, dict | None] = {}

    def get_predictions(self, config_name: str) -> list[dict]:
        """Return cached predictions, computing on first call per config."""
        if config_name not in self._prediction_cache:
            from api.services.prediction_service import build_prediction_table
            self._prediction_cache[config_name] = build_prediction_table(config_name, self)
        return self._prediction_cache[config_name]

    def invalidate_prediction_cache(self) -> None:
        """Clear the prediction cache (call after decisions change or pipeline re-runs)."""
        self._prediction_cache.clear()
        self._test_predictions_cache.clear()

    def load_all(self) -> None:
        self._load_master_data()
        self._load_models()
        self._load_rubric()
        self._load_experiences()

    def _load_master_data(self) -> None:
        dfs = []
        for year in [2022, 2023, 2024]:
            p = PROCESSED_DIR / f"master_{year}.csv"
            if p.exists():
                dfs.append(pd.read_csv(p))
                logger.info("Loaded master_%d.csv (%d rows)", year, len(dfs[-1]))
        if dfs:
            self.master_data = pd.concat(dfs, ignore_index=True)

            # Fix typo
            if "Disadvantanged_Ind" in self.master_data.columns and "Disadvantaged_Ind" not in self.master_data.columns:
                self.master_data["Disadvantaged_Ind"] = self.master_data["Disadvantanged_Ind"]

            # Normalize binary features
            for col in BINARY_FEATURES:
                if col in self.master_data.columns:
                    if self.master_data[col].dtype == object:
                        self.master_data[col] = self.master_data[col].map(
                            lambda x: 1 if str(x).strip().lower().startswith("y") else 0
                        )
                    else:
                        self.master_data[col] = self.master_data[col].fillna(0).astype(float)

            # Ensure bucket_label exists
            if "bucket_label" not in self.master_data.columns:
                if "Service_Rating_Categorical" in self.master_data.columns:
                    self.master_data["bucket_label"] = self.master_data["Service_Rating_Categorical"].map(BUCKET_MAP)

            # Compute engineered features if missing
            self._compute_engineered_features()

            logger.info("Total master data: %d rows", len(self.master_data))
        else:
            logger.warning("No master CSVs found in %s", PROCESSED_DIR)

    def _compute_engineered_features(self) -> None:
        """Compute reviewer-aligned composite features on the fly.

        Delegates the 7 composite formulas to the shared
        engineer_composite_features() function, then normalizes extra
        columns that only exist in the legacy master CSVs.
        """
        df = self.master_data

        # Compute 7 composites via shared function (if not already present)
        if "Total_Volunteer_Hours" not in df.columns:
            composites = engineer_composite_features(df)
            for col in composites.columns:
                if col != ID_COLUMN:
                    df[col] = composites[col]

        # --- Extra normalization for legacy master CSV columns ---

        # Childhood_Med_Underserved from raw column
        if "Childhood_Med_Underserved" not in df.columns:
            src = "Childhood_Med_Underserved_Self_Reported"
            if src in df.columns:
                df["Childhood_Med_Underserved"] = (df[src] == "Yes").astype(int)
            else:
                df["Childhood_Med_Underserved"] = 0

        # Paid_Employment_BF_18, Contribution_to_Family (normalize if string)
        for col in ["Paid_Employment_BF_18", "Contribution_to_Family"]:
            if col in df.columns and df[col].dtype == object:
                df[col] = df[col].map(lambda x: 1 if str(x).strip().lower().startswith("y") else 0)
            elif col not in df.columns:
                df[col] = 0

        # Employed_Undergrad (may not exist in master CSVs)
        if "Employed_Undergrad" not in df.columns:
            df["Employed_Undergrad"] = 0

        # Num_Dependents (ensure numeric)
        if "Num_Dependents" in df.columns:
            df["Num_Dependents"] = pd.to_numeric(df["Num_Dependents"], errors="coerce").fillna(0)
        else:
            df["Num_Dependents"] = 0

        logger.info("Engineered features computed for master data")

    def _load_models(self) -> None:
        from pipeline.model_verification import load_verified_pickle

        for config_name, filename in WORKING_PKLS.items():
            path = MODELS_DIR / filename
            if path.exists():
                try:
                    self.model_results[config_name] = load_verified_pickle(path)
                    logger.info("Loaded model: %s (verified)", config_name)
                except FileNotFoundError:
                    # Hash file missing — fallback for backward compatibility
                    # TODO: Remove after retraining models with save_verified_pickle()
                    logger.warning("Model hash missing, loading without verification: %s", config_name)
                    with open(path, "rb") as f:
                        self.model_results[config_name] = pickle.load(f)
            else:
                logger.warning("Model not found: %s", path)

    def _load_rubric(self) -> None:
        # Prefer v2 format; fall back to v1 for backward compat
        rubric_path = CACHE_DIR / "rubric_scores_v2.json"
        if not rubric_path.exists():
            rubric_path = CACHE_DIR / "rubric_scores.json"

        if rubric_path.exists():
            with open(rubric_path) as f:
                raw = json.load(f)

            # Detect v2 nested format: {amcas_id: {scores: {...}, details: {...}}}
            sample = next(iter(raw.values()), None) if raw else None
            if isinstance(sample, dict) and "scores" in sample:
                # v2 format
                for amcas_id, record in raw.items():
                    self.rubric_scores[amcas_id] = record.get("scores", {})
                    self.rubric_details[amcas_id] = record.get("details", {})
                logger.info("Loaded %d rubric scores (v2 format with details)", len(self.rubric_scores))
            else:
                # v1 flat format: {amcas_id: {dim: score}}
                self.rubric_scores = raw
                logger.info("Loaded %d rubric scores (v1 format)", len(self.rubric_scores))

        rubric_feat_path = PROCESSED_DIR / "rubric_features.csv"
        if rubric_feat_path.exists():
            self.rubric_features = pd.read_csv(rubric_feat_path)
            logger.info("Loaded rubric features: %d rows", len(self.rubric_features))

    def _load_experiences(self) -> None:
        """Load raw experiences table for per-applicant lookups."""
        from pipeline.data_preparation import load_experiences
        try:
            self.experiences_data = load_experiences()
            logger.info("Loaded %d experience records", len(self.experiences_data))
        except (FileNotFoundError, KeyError, pd.errors.EmptyDataError):
            logger.warning("Could not load experiences data", exc_info=True)
