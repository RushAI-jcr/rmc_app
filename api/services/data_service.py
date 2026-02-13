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

logger = logging.getLogger(__name__)


class DataStore:
    """Holds all loaded data and models in memory."""

    def __init__(self) -> None:
        self.master_data: pd.DataFrame = pd.DataFrame()
        self.model_results: dict[str, dict] = {}
        self.rubric_scores: dict = {}
        self.rubric_features: pd.DataFrame = pd.DataFrame()
        self.decisions: dict[int, dict] = {}  # amcas_id -> {decision, notes}

    def load_all(self) -> None:
        self._load_master_data()
        self._load_models()
        self._load_rubric()

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
        """Compute reviewer-aligned composite features on the fly."""
        df = self.master_data

        # Total_Volunteer_Hours
        if "Total_Volunteer_Hours" not in df.columns:
            med = df.get("Exp_Hour_Volunteer_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
            non_med = df.get("Exp_Hour_Volunteer_Non_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
            df["Total_Volunteer_Hours"] = med + non_med

        # Community_Engaged_Ratio
        if "Community_Engaged_Ratio" not in df.columns:
            non_med = df.get("Exp_Hour_Volunteer_Non_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
            total_vol = df["Total_Volunteer_Hours"]
            df["Community_Engaged_Ratio"] = np.where(total_vol > 0, non_med / total_vol, 0.0)

        # Clinical_Total_Hours
        if "Clinical_Total_Hours" not in df.columns:
            shadow = df.get("Exp_Hour_Shadowing", pd.Series(0, index=df.index)).fillna(0).astype(float)
            med_emp = df.get("Exp_Hour_Employ_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
            df["Clinical_Total_Hours"] = shadow + med_emp

        # Direct_Care_Ratio
        if "Direct_Care_Ratio" not in df.columns:
            med_emp = df.get("Exp_Hour_Employ_Med", pd.Series(0, index=df.index)).fillna(0).astype(float)
            clin_total = df["Clinical_Total_Hours"]
            df["Direct_Care_Ratio"] = np.where(clin_total > 0, med_emp / clin_total, 0.0)

        # Adversity_Count
        if "Adversity_Count" not in df.columns:
            grit_cols = ["First_Generation_Ind", "Disadvantaged_Ind", "SES_Value", "Pell_Grant", "Fee_Assistance_Program"]
            adversity = pd.Series(0, index=df.index, dtype=float)
            for col in grit_cols:
                if col in df.columns:
                    adversity = adversity + pd.to_numeric(df[col], errors="coerce").fillna(0)
            df["Adversity_Count"] = adversity.astype(int)

        # Grit_Index (broader than Adversity_Count)
        if "Grit_Index" not in df.columns:
            grit_all = ["First_Generation_Ind", "Disadvantaged_Ind", "SES_Value",
                         "Pell_Grant", "Fee_Assistance_Program",
                         "Paid_Employment_BF_18", "Contribution_to_Family", "Childhood_Med_Underserved"]
            grit_sum = pd.Series(0, index=df.index, dtype=float)
            for col in grit_all:
                if col in df.columns:
                    grit_sum = grit_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
            df["Grit_Index"] = grit_sum.astype(int)

        # Experience_Diversity
        if "Experience_Diversity" not in df.columns:
            exp_flags = [
                "has_direct_patient_care", "has_volunteering", "has_community_service",
                "has_shadowing", "has_clinical_experience", "has_leadership",
                "has_research", "has_military_service", "has_honors",
            ]
            div_sum = pd.Series(0, index=df.index, dtype=float)
            for col in exp_flags:
                if col in df.columns:
                    div_sum = div_sum + pd.to_numeric(df[col], errors="coerce").fillna(0)
            df["Experience_Diversity"] = div_sum.astype(int)

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
        rubric_path = CACHE_DIR / "rubric_scores.json"
        if rubric_path.exists():
            with open(rubric_path) as f:
                self.rubric_scores = json.load(f)
            logger.info("Loaded %d rubric scores", len(self.rubric_scores))

        rubric_feat_path = PROCESSED_DIR / "rubric_features.csv"
        if rubric_feat_path.exists():
            self.rubric_features = pd.read_csv(rubric_feat_path)
            logger.info("Loaded rubric features: %d rows", len(self.rubric_features))
