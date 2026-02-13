"""Data ingestion pipeline: load, join, and normalize all admissions data."""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

from pipeline.config import (
    DATA_DIR,
    YEAR_FOLDERS,
    FILE_MAP,
    ID_COLUMN,
    ID_ALIASES,
    TARGET_SCORE,
    TARGET_BUCKET,
    TARGET_BUCKET_NUM,
    BUCKET_MAP,
    GPA_TREND_MAP,
    PARENT_EDUCATION_MAP,
    EXP_TYPE_TO_FLAG,
    PATIENT_CARE_EXP_TYPES,
    SECONDARY_ESSAY_COLUMNS,
    PROCESSED_DIR,
)

logger = logging.getLogger(__name__)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names: spaces -> underscores, strip, remove parens."""
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


def _normalize_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure join key is consistently named Amcas_ID, dropping duplicates."""
    target_lower = ID_COLUMN.lower()

    matching_cols = [c for c in df.columns if c.lower() == target_lower]

    if not matching_cols:
        for alias in ID_ALIASES:
            alias_norm = alias.replace(" ", "_").lower()
            matching_cols = [c for c in df.columns if c.lower() == alias_norm]
            if matching_cols:
                break

    if not matching_cols:
        raise KeyError(f"No ID column found. Columns: {list(df.columns)}")

    keep_col = matching_cols[0]
    drop_cols = matching_cols[1:]
    if drop_cols:
        df = df.drop(columns=drop_cols)
    if keep_col != ID_COLUMN:
        df = df.rename(columns={keep_col: ID_COLUMN})

    return df


def _read_xlsx(
    year: int,
    file_key: str,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Read an xlsx file for a given year, with column normalization.

    Args:
        data_dir: Override base data directory (default: DATA_DIR).
        file_map: Override file lookup -- maps logical type to exact Path.
    """
    # If a file_map is provided, use it directly (bypasses folder/filename logic)
    if file_map and file_key in file_map:
        path = file_map[file_key]
    else:
        base = data_dir or DATA_DIR
        folder = YEAR_FOLDERS.get(year, str(year))
        if file_key == "schools":
            fname = FILE_MAP["schools_2024"] if year == 2024 else FILE_MAP["schools_2022_2023"]
        else:
            fname = FILE_MAP[file_key]
        path = base / folder / fname

    if not path.exists():
        logger.warning("File not found: %s", path)
        return pd.DataFrame()

    df = pd.read_excel(path, engine="openpyxl")
    df = _normalize_columns(df)
    df = df.loc[:, ~df.columns.duplicated()]
    df = _normalize_id_column(df)
    df["app_year"] = year
    return df


# -- Individual table loaders ------------------------------------------------


def load_applicants(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load and concatenate Applicants table across years."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = []
    for year in years:
        df = _read_xlsx(year, "applicants", data_dir=data_dir, file_map=file_map)
        if df.empty:
            continue
        for col in df.columns:
            if "Application_Review_Score" in col or "Application Review Score" in col.replace("_", " "):
                df = df.rename(columns={col: TARGET_SCORE})
            if "Service_Rating_Categorical" in col or "Service Rating Categorical" in col.replace("_", " "):
                df = df.rename(columns={col: TARGET_BUCKET})
            if "Service_Rating_Numerical" in col or "Service Rating Numerical" in col.replace("_", " "):
                df = df.rename(columns={col: TARGET_BUCKET_NUM})
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Loaded %d applicants across %s", len(combined), years)
    return combined


def load_experiences(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Experiences table (one row per experience, many per applicant)."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "experiences", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d experience records", len(combined))
    return combined


def load_personal_statements(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Personal Statement table (one row per applicant)."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "personal_statement", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d personal statements", len(combined))
    return combined


def load_secondary_applications(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Secondary Application table."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "secondary_application", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d secondary applications", len(combined))
    return combined


def load_gpa_trend(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load GPA Trend table."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "gpa_trend", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d GPA trend records", len(combined))
    return combined


def load_languages(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Language table (one row per language per applicant)."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "language", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d language records", len(combined))
    return combined


def load_parents(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Parents table (1-2 rows per applicant)."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, "parents", data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d parent records", len(combined))
    return combined


# -- Aggregation helpers -----------------------------------------------------


def aggregate_languages(languages: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: count of languages."""
    if languages.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Num_Languages"])
    agg = (
        languages.groupby(ID_COLUMN)
        .agg(Num_Languages=("Language_Desc" if "Language_Desc" in languages.columns else ID_COLUMN, "count"))
        .reset_index()
    )
    return agg


def aggregate_parents(parents: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: max education ordinal."""
    if parents.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Parent_Max_Education_Ordinal"])

    ed_col = None
    for candidate in ["Edu_Level", "Parent_Education_Level", "Parent_Education"]:
        if candidate in parents.columns:
            ed_col = candidate
            break

    if ed_col is None:
        logger.warning("No education column found in Parents. Columns: %s", list(parents.columns))
        return pd.DataFrame(columns=[ID_COLUMN, "Parent_Max_Education_Ordinal"])

    parents = parents.copy()
    parents["_ed_ordinal"] = parents[ed_col].map(PARENT_EDUCATION_MAP).fillna(2)
    agg = (
        parents.groupby(ID_COLUMN)
        .agg(Parent_Max_Education_Ordinal=("_ed_ordinal", "max"))
        .reset_index()
    )
    return agg


def aggregate_gpa_trend(gpa_trend: pd.DataFrame) -> pd.DataFrame:
    """Extract GPA trend as ordinal (one row per applicant)."""
    if gpa_trend.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "GPA_Trend_Ordinal"])

    if "Total_GPA_Trend" in gpa_trend.columns:
        result = gpa_trend[[ID_COLUMN, "Total_GPA_Trend"]].drop_duplicates(subset=ID_COLUMN)
        result = result.rename(columns={"Total_GPA_Trend": "GPA_Trend_Ordinal"})
        result["GPA_Trend_Ordinal"] = result["GPA_Trend_Ordinal"].fillna(0.5)
        return result

    trend_col = None
    for candidate in ["GPA_Trend", "Gpa_Trend"]:
        if candidate in gpa_trend.columns:
            trend_col = candidate
            break

    if trend_col is None:
        logger.warning("No GPA trend column found. Columns: %s", list(gpa_trend.columns))
        return pd.DataFrame(columns=[ID_COLUMN, "GPA_Trend_Ordinal"])

    gpa_trend = gpa_trend.copy()
    gpa_trend["GPA_Trend_Ordinal"] = gpa_trend[trend_col].map(GPA_TREND_MAP).fillna(1)
    return gpa_trend[[ID_COLUMN, "GPA_Trend_Ordinal"]].drop_duplicates(subset=ID_COLUMN)


def derive_experience_binary_flags(experiences: pd.DataFrame) -> pd.DataFrame:
    """Derive 9 binary experience flags per applicant from experience records."""
    if experiences.empty:
        return pd.DataFrame(columns=[ID_COLUMN])

    exp_type_col = None
    for candidate in ["Exp_Type", "exp_type"]:
        if candidate in experiences.columns:
            exp_type_col = candidate
            break

    if exp_type_col is None:
        return pd.DataFrame(columns=[ID_COLUMN])

    flags_per_applicant = {}
    for amcas_id, group in experiences.groupby(ID_COLUMN):
        types = set(group[exp_type_col].dropna().unique())
        flags = {}
        for exp_type, flag_name in EXP_TYPE_TO_FLAG.items():
            flags[flag_name] = int(any(exp_type.lower() in t.lower() for t in types))

        flags["has_direct_patient_care"] = int(
            any(
                any(pct.lower() in t.lower() for pct in PATIENT_CARE_EXP_TYPES)
                for t in types
            )
        )

        text_fields = []
        for col in ["Exp_Name", "Exp_Desc"]:
            if col in group.columns:
                text_fields.extend(group[col].dropna().str.lower().tolist())
        all_text = " ".join(text_fields)
        flags["has_honors"] = int(
            any(kw in all_text for kw in ["honor", "honours", "dean's list", "cum laude", "phi beta kappa", "award"])
        )

        flags_per_applicant[amcas_id] = flags

    flags_df = pd.DataFrame.from_dict(flags_per_applicant, orient="index")
    flags_df.index.name = ID_COLUMN
    flags_df = flags_df.reset_index()
    return flags_df


# -- Main pipeline -----------------------------------------------------------


def build_unified_dataset(
    years: list[int] | None = None,
    exclude_zero_scores: bool = True,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Build the unified applicant dataset by joining all tables.

    Args:
        data_dir: Override base data directory (default: DATA_DIR).
        file_map: Override file lookup -- maps logical type to exact Path.

    Returns a single DataFrame with one row per applicant.
    """
    years = years or list(YEAR_FOLDERS.keys())
    kw = {"data_dir": data_dir, "file_map": file_map}

    applicants = load_applicants(years, **kw)
    experiences = load_experiences(years, **kw)
    personal_statements = load_personal_statements(years, **kw)
    secondary_apps = load_secondary_applications(years, **kw)
    gpa_trend = load_gpa_trend(years, **kw)
    languages = load_languages(years, **kw)
    parents = load_parents(years, **kw)

    lang_agg = aggregate_languages(languages)
    parent_agg = aggregate_parents(parents)
    gpa_agg = aggregate_gpa_trend(gpa_trend)
    exp_flags = derive_experience_binary_flags(experiences)

    df = applicants.copy()

    for aux_df in [lang_agg, parent_agg, gpa_agg, exp_flags]:
        if not aux_df.empty and ID_COLUMN in aux_df.columns:
            df = df.merge(aux_df, on=ID_COLUMN, how="left", suffixes=("", "_dup"))
            dup_cols = [c for c in df.columns if c.endswith("_dup")]
            df = df.drop(columns=dup_cols)

    if not personal_statements.empty:
        ps_cols = [ID_COLUMN]
        if "personal_statement" in personal_statements.columns:
            ps_cols.append("personal_statement")
        df = df.merge(
            personal_statements[ps_cols].drop_duplicates(subset=ID_COLUMN),
            on=ID_COLUMN,
            how="left",
        )

    if not secondary_apps.empty:
        essay_cols = [ID_COLUMN]
        for col in secondary_apps.columns:
            orig_name = col.replace("_", " ")
            if any(ec.replace(" ", "_") == col or ec == orig_name for ec in SECONDARY_ESSAY_COLUMNS):
                essay_cols.append(col)
        # Also extract "Employed Undergrad" structured field
        for candidate in ["5_-_Employed_Undergrad", "5 - Employed Undergrad"]:
            norm = candidate.replace(" ", "_")
            if norm in secondary_apps.columns and norm not in essay_cols:
                essay_cols.append(norm)
        if len(essay_cols) > 1:
            df = df.merge(
                secondary_apps[essay_cols].drop_duplicates(subset=ID_COLUMN),
                on=ID_COLUMN,
                how="left",
            )
        # Rename Employed Undergrad to standardized name
        eu_col = "5_-_Employed_Undergrad"
        if eu_col in df.columns:
            df["Employed_Undergrad"] = df[eu_col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
            df = df.drop(columns=[eu_col])

    # Derive Childhood_Med_Underserved from existing column
    underserved_col = "Childhood_Med_Underserved_Self_Reported"
    if underserved_col in df.columns and "Childhood_Med_Underserved" not in df.columns:
        df["Childhood_Med_Underserved"] = (df[underserved_col] == "Yes").astype(int)

    # Normalize binary indicator columns to 0/1
    for col in df.columns:
        if df[col].dtype == object:
            unique_vals = set(df[col].dropna().unique())
            if unique_vals <= {"Yes", "No", "Y", "N"}:
                df[col] = df[col].map({"Yes": 1, "No": 0, "Y": 1, "N": 0})

    # Zero-scored applicants: score=0 means reviewer said "no interview" (lowest tier).
    # These are valid data points, not missing data — keep them.
    if exclude_zero_scores and TARGET_SCORE in df.columns:
        n_zeros = int((df[TARGET_SCORE] == 0).sum())
        logger.info(
            "Keeping %d zero-scored applicants (reviewer 'no interview' = lowest tier)",
            n_zeros,
        )

    # Map bucket labels to integers
    if TARGET_BUCKET in df.columns:
        df["bucket_label"] = df[TARGET_BUCKET].map(BUCKET_MAP)

    logger.info(
        "Unified dataset: %d applicants, %d columns", len(df), len(df.columns)
    )
    return df


def save_master_csvs(years: list[int] | None = None) -> dict[int, Path]:
    """Build unified datasets per year and save as CSVs."""
    years = years or list(YEAR_FOLDERS.keys())
    paths = {}
    for year in years:
        df = build_unified_dataset(years=[year], exclude_zero_scores=False)
        out_path = PROCESSED_DIR / f"master_{year}.csv"
        df.to_csv(out_path, index=False)
        paths[year] = out_path
        logger.info("Saved %d rows to %s", len(df), out_path)
    return paths
