"""Data preparation: load, normalize, join, clean, and impute all admissions data.

Consolidates the former data_ingestion.py and data_cleaning.py into a single
module with a clear pipeline: read xlsx → normalize → aggregate → join → clean.

Public API:
    prepare_dataset()              — main entry point, returns one-row-per-applicant
    load_applicants()              — load Applicants table (used by rubric scoring)
    load_experiences()             — load Experiences table (used by rubric scoring)
    load_personal_statements()     — load Personal Statement table
    load_secondary_applications()  — load Secondary Application table
    build_personal_statements_dict() — AMCAS ID -> PS text dict (for LLM scoring)
    build_secondary_texts_dict()     — AMCAS ID -> secondary essays dict (for LLM scoring)
"""

import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from pipeline.config import (
    BUCKET_MAP,
    COLUMNS_TO_DROP,
    DATA_DIR,
    EXP_TYPE_TO_FLAG,
    FILE_MAP,
    GPA_TREND_MAP,
    ID_ALIASES,
    ID_COLUMN,
    PARENT_EDUCATION_MAP,
    PATIENT_CARE_EXP_TYPES,
    PROCESSED_DIR,
    SECONDARY_ESSAY_COLUMNS,
    TARGET_BUCKET,
    TARGET_BUCKET_NUM,
    TARGET_SCORE,
    YEAR_FOLDERS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Column & ID normalization
# ---------------------------------------------------------------------------


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names: strip, spaces → underscores, remove parens."""
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df


def _normalize_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure join key is consistently named Amcas_ID."""
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


def _fix_known_typos(df: pd.DataFrame) -> pd.DataFrame:
    """Fix known column-name typos across years."""
    if "Disadvantanged_Ind" in df.columns and "Disadvantaged_Ind" not in df.columns:
        df = df.rename(columns={"Disadvantanged_Ind": "Disadvantaged_Ind"})
        logger.info("Fixed typo: Disadvantanged_Ind -> Disadvantaged_Ind")
    return df


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------


def _read_xlsx(
    year: int,
    file_key: str,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Read an xlsx file for a given year, with column normalization.

    Args:
        data_dir: Override base data directory (default: DATA_DIR).
        file_map: Override file lookup — maps logical type to exact Path.
    """
    if file_map and file_key in file_map:
        path = file_map[file_key]
    else:
        base = data_dir or DATA_DIR
        folder = YEAR_FOLDERS.get(year, str(year))
        if file_key == "schools":
            # "8. School.xlsx" (2024) vs "8. Schools.xlsx" (older years)
            fname = "8. School.xlsx" if year >= 2024 else "8. Schools.xlsx"
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
    df = _fix_known_typos(df)
    df["app_year"] = year
    return df


def _load_table(
    file_key: str,
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load and concatenate a table type across years."""
    years = years or list(YEAR_FOLDERS.keys())
    frames = [_read_xlsx(y, file_key, data_dir=data_dir, file_map=file_map) for y in years]
    combined = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    logger.info("Loaded %d rows for '%s' across %s", len(combined), file_key, years)
    return combined


# ---------------------------------------------------------------------------
# Public table loaders (used by rubric scoring and smoke tests)
# ---------------------------------------------------------------------------


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
        # Normalize target column names
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
    return _load_table("experiences", years, data_dir, file_map)


def load_personal_statements(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Personal Statement table (one row per applicant)."""
    return _load_table("personal_statement", years, data_dir, file_map)


def load_secondary_applications(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
) -> pd.DataFrame:
    """Load Secondary Application table."""
    return _load_table("secondary_application", years, data_dir, file_map)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _aggregate_languages(languages: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: count of languages."""
    if languages.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Num_Languages"])
    agg = (
        languages.groupby(ID_COLUMN)
        .agg(Num_Languages=("Language_Desc" if "Language_Desc" in languages.columns else ID_COLUMN, "count"))
        .reset_index()
    )
    return agg


def _aggregate_parents(parents: pd.DataFrame) -> pd.DataFrame:
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


def _aggregate_gpa_trend(gpa_trend: pd.DataFrame) -> pd.DataFrame:
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


def _aggregate_siblings(siblings: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: count of siblings."""
    if siblings.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Num_Siblings"])
    agg = (
        siblings.groupby(ID_COLUMN)
        .size()
        .reset_index(name="Num_Siblings")
    )
    return agg


def _aggregate_academic_records(academic_records: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: course count, total credits, distinct schools."""
    if academic_records.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Num_Courses", "Total_Credit_Hours", "Num_Schools_Academic"])

    academic_records = academic_records.copy()
    agg_dict: dict = {}

    # Count courses
    agg_dict["Num_Courses"] = (ID_COLUMN, "count")

    # Sum credit hours if column exists
    credit_col = None
    for candidate in ["Credit_Hours", "Credit_Hrs", "Credits"]:
        if candidate in academic_records.columns:
            credit_col = candidate
            break
    if credit_col:
        academic_records[credit_col] = pd.to_numeric(academic_records[credit_col], errors="coerce").fillna(0)
        agg_dict["Total_Credit_Hours"] = (credit_col, "sum")

    # Distinct schools
    school_col = None
    for candidate in ["School_Name", "Institution_Name", "School"]:
        if candidate in academic_records.columns:
            school_col = candidate
            break
    if school_col:
        agg_dict["Num_Schools_Academic"] = (school_col, "nunique")

    agg = academic_records.groupby(ID_COLUMN).agg(**agg_dict).reset_index()

    # Fill missing columns with defaults
    for col, default in [("Num_Courses", 0), ("Total_Credit_Hours", 0), ("Num_Schools_Academic", 0)]:
        if col not in agg.columns:
            agg[col] = default

    return agg


def _aggregate_schools(schools: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: distinct schools, primary undergrad, major, highest degree."""
    if schools.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Num_Schools", "Primary_Undergrad_School", "Primary_Major", "Highest_Degree"])

    result_rows = []
    for amcas_id, group in schools.groupby(ID_COLUMN):
        row: dict = {ID_COLUMN: amcas_id}

        # Distinct school count
        school_col = None
        for candidate in ["School_Name", "Institution_Name", "School"]:
            if candidate in group.columns:
                school_col = candidate
                break
        row["Num_Schools"] = group[school_col].nunique() if school_col else len(group)

        # Primary undergrad school (look for type indicators)
        school_name = None
        major = None
        type_col = None
        for candidate in ["School_Type", "Type", "Degree_Type"]:
            if candidate in group.columns:
                type_col = candidate
                break

        if type_col and school_col:
            undergrad = group[group[type_col].astype(str).str.contains("undergrad|baccalaureate|bachelor", case=False, na=False)]
            if not undergrad.empty:
                school_name = undergrad.iloc[0][school_col]
        elif school_col:
            school_name = group.iloc[0][school_col]

        row["Primary_Undergrad_School"] = school_name if pd.notna(school_name) else None

        # Primary major
        major_col = None
        for candidate in ["Major_Long_Desc", "Major", "Major_Desc"]:
            if candidate in group.columns:
                major_col = candidate
                break
        if major_col:
            major = group.iloc[0][major_col]
        row["Primary_Major"] = major if pd.notna(major) else None

        # Highest degree
        degree_col = None
        for candidate in ["Degree_Long_Desc", "Degree", "Degree_Desc"]:
            if candidate in group.columns:
                degree_col = candidate
                break
        row["Highest_Degree"] = group.iloc[0][degree_col] if degree_col and pd.notna(group.iloc[0].get(degree_col)) else None

        result_rows.append(row)

    return pd.DataFrame(result_rows)


def _aggregate_military(military: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to one row per applicant: first row's service and status descriptions."""
    if military.empty:
        return pd.DataFrame(columns=[ID_COLUMN, "Military_Service_Desc", "Military_Status_Desc"])

    first_rows = military.drop_duplicates(subset=ID_COLUMN, keep="first")

    result = first_rows[[ID_COLUMN]].copy()

    svc_col = None
    for candidate in ["Military_Service_Desc", "Service_Desc", "Branch"]:
        if candidate in first_rows.columns:
            svc_col = candidate
            break
    result["Military_Service_Desc"] = first_rows[svc_col].values if svc_col else None

    status_col = None
    for candidate in ["Military_Status_Desc", "Status_Desc", "Military_Service_Status"]:
        if candidate in first_rows.columns:
            status_col = candidate
            break
    result["Military_Status_Desc"] = first_rows[status_col].values if status_col else None

    return result


def _derive_experience_flags(experiences: pd.DataFrame) -> pd.DataFrame:
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


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------


def _drop_high_missingness(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns with >70% missingness (defined in COLUMNS_TO_DROP)."""
    dropped = []
    for col in COLUMNS_TO_DROP:
        if col in df.columns:
            pct_missing = df[col].isna().mean() * 100
            df = df.drop(columns=[col])
            dropped.append((col, pct_missing))

    for col, pct in dropped:
        logger.info("Dropped column %-35s (%.1f%% missing)", col, pct)
    logger.info("Dropped %d high-missingness columns", len(dropped))
    return df


def _impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Impute remaining NaN values using safe defaults.

    - Hours columns → 0
    - Percentage columns → 0
    - Age → median
    """
    df = df.copy()

    # Hours → 0
    hour_cols = [c for c in df.columns if "Hour" in c or "Hours" in c]
    for col in hour_cols:
        n_filled = df[col].isna().sum()
        if n_filled > 0:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            logger.info("Imputed %d NaN -> 0 in %s", n_filled, col)

    # Percentages → 0
    pct_cols = [c for c in df.columns if "Pct" in c or "Percent" in c]
    for col in pct_cols:
        n_filled = df[col].isna().sum()
        if n_filled > 0:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            logger.info("Imputed %d NaN -> 0 in %s", n_filled, col)

    # Age → median
    if "Age" in df.columns:
        n_missing_age = df["Age"].isna().sum()
        if n_missing_age > 0:
            median_age = df["Age"].median()
            df["Age"] = df["Age"].fillna(median_age)
            logger.info("Imputed %d missing Age values with median %.1f", n_missing_age, median_age)

    return df


def _normalize_binary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Yes/No string columns to 0/1 integers."""
    for col in df.columns:
        if df[col].dtype == object:
            unique_vals = set(df[col].dropna().unique())
            if unique_vals <= {"Yes", "No", "Y", "N"}:
                df[col] = df[col].map({"Yes": 1, "No": 0, "Y": 1, "N": 0})
    return df


# ---------------------------------------------------------------------------
# Join & secondary field extraction
# ---------------------------------------------------------------------------


def _join_secondary_fields(
    df: pd.DataFrame,
    personal_statements: pd.DataFrame,
    secondary_apps: pd.DataFrame,
) -> pd.DataFrame:
    """Join personal statement and secondary essay text to the main DataFrame."""
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
        # Extract "Employed Undergrad" structured field
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

    return df


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def prepare_dataset(
    years: list[int] | None = None,
    data_dir: Path | None = None,
    file_map: dict[str, Path] | None = None,
    progress_callback: Callable[[str, int], None] | None = None,
) -> pd.DataFrame:
    """Build a clean, unified applicant dataset from raw xlsx files.

    Stages:
      1. Load all xlsx files (per year or from file_map)
      2. Normalize columns and IDs
      3. Aggregate multi-row tables
      4. Left-join everything to Applicants on Amcas_ID
      5. Clean: drop high-missingness cols, impute NaNs
      6. Normalize binary Yes/No → 0/1, map bucket labels

    Args:
        years: Which cycle years to load. Defaults to all in YEAR_FOLDERS.
        data_dir: Override base data directory (default: DATA_DIR).
        file_map: Override file lookup — maps logical type to exact Path.
            When provided, treats as single-cycle API mode.
        progress_callback: Called with (step_name, percent_complete).

    Returns:
        One-row-per-applicant DataFrame with app_year column.
    """
    cb = progress_callback or (lambda _s, _p: None)
    years = years or list(YEAR_FOLDERS.keys())
    kw: dict = {"data_dir": data_dir, "file_map": file_map}

    # --- Step 1: Load tables ---
    cb("ingestion", 0)
    applicants = load_applicants(years, **kw)
    experiences = load_experiences(years, **kw)
    personal_statements = load_personal_statements(years, **kw)
    secondary_apps = load_secondary_applications(years, **kw)
    gpa_trend = _load_table("gpa_trend", years, **kw)
    languages = _load_table("language", years, **kw)
    parents = _load_table("parents", years, **kw)
    siblings = _load_table("siblings", years, **kw)
    academic_records = _load_table("academic_records", years, **kw)
    schools = _load_table("schools", years, **kw)
    military = _load_table("military", years, **kw)
    cb("ingestion", 10)

    # --- Step 2: Aggregate multi-row tables ---
    lang_agg = _aggregate_languages(languages)
    parent_agg = _aggregate_parents(parents)
    gpa_agg = _aggregate_gpa_trend(gpa_trend)
    exp_flags = _derive_experience_flags(experiences)
    siblings_agg = _aggregate_siblings(siblings)
    academic_agg = _aggregate_academic_records(academic_records)
    schools_agg = _aggregate_schools(schools)
    military_agg = _aggregate_military(military)
    cb("aggregation", 20)

    # --- Step 3: Join everything to applicants ---
    df = applicants.copy()

    for aux_df in [lang_agg, parent_agg, gpa_agg, exp_flags, siblings_agg, academic_agg, schools_agg, military_agg]:
        if not aux_df.empty and ID_COLUMN in aux_df.columns:
            df = df.merge(aux_df, on=ID_COLUMN, how="left", suffixes=("", "_dup"))
            dup_cols = [c for c in df.columns if c.endswith("_dup")]
            df = df.drop(columns=dup_cols)

    df = _join_secondary_fields(df, personal_statements, secondary_apps)
    cb("joining", 30)

    # --- Step 4: Clean ---
    df = _normalize_binary_columns(df)
    df = _drop_high_missingness(df)
    df = _fix_known_typos(df)
    df = _impute_missing(df)
    cb("cleaning", 40)

    # Map bucket labels to integers
    if TARGET_BUCKET in df.columns:
        df["bucket_label"] = df[TARGET_BUCKET].map(BUCKET_MAP)

    logger.info(
        "Prepared dataset: %d applicants, %d columns, years %s",
        len(df), len(df.columns), years,
    )
    return df


def save_master_csvs(
    df: pd.DataFrame,
    output_dir: Path | None = None,
) -> dict[int, Path]:
    """Save per-year CSVs from a prepared dataset."""
    output_dir = output_dir or PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    for year in df["app_year"].unique():
        year_df = df[df["app_year"] == year]
        out_path = output_dir / f"master_{int(year)}.csv"
        year_df.to_csv(out_path, index=False)
        paths[int(year)] = out_path
        logger.info("Saved %d rows to %s", len(year_df), out_path)

    return paths


# ---------------------------------------------------------------------------
# Text dict builders (used by rubric scoring runners)
# ---------------------------------------------------------------------------


def build_personal_statements_dict(years: list[int]) -> dict[int, str]:
    """Build mapping of AMCAS ID -> personal statement text.

    Used by rubric scoring runners to prepare text for LLM scoring.
    """
    ps_df = load_personal_statements(years)
    if ps_df.empty:
        return {}

    # Find the personal statement text column
    ps_col = None
    for candidate in ["personal_statement", "Personal_Statement", "PS_Text"]:
        if candidate in ps_df.columns:
            ps_col = candidate
            break

    if ps_col is None:
        # Try any column that looks like it contains long text
        for col in ps_df.columns:
            if col == ID_COLUMN or col == "app_year":
                continue
            sample = ps_df[col].dropna().head(5)
            if len(sample) > 0 and sample.str.len().mean() > 200:
                ps_col = col
                break

    if ps_col is None:
        logger.warning("Could not identify PS text column. Columns: %s", list(ps_df.columns))
        return {}

    # Vectorized approach: filter valid rows, then create dict
    valid_mask = ps_df[ps_col].notna() & (ps_df[ps_col].astype(str).str.strip() != "")
    filtered = ps_df.loc[valid_mask, [ID_COLUMN, ps_col]]
    result = dict(zip(
        filtered[ID_COLUMN].astype(int),
        filtered[ps_col].astype(str).str.strip(),
    ))

    logger.info("Loaded %d personal statements", len(result))
    return result


def build_secondary_texts_dict(years: list[int]) -> dict[int, str]:
    """Build mapping of AMCAS ID -> concatenated secondary essay text.

    Used by rubric scoring runners to prepare text for LLM scoring.
    """
    sec_df = load_secondary_applications(years)
    if sec_df.empty:
        return {}

    # Find essay columns
    essay_cols = []
    for col in sec_df.columns:
        orig = col.replace("_", " ")
        if any(ec.replace(" ", "_") == col or ec == orig for ec in SECONDARY_ESSAY_COLUMNS):
            essay_cols.append(col)

    if not essay_cols:
        logger.warning("No secondary essay columns found. Columns: %s", list(sec_df.columns))
        return {}

    # Vectorized: concatenate essay columns per row using .apply (avoids iterrows)
    def _concat_essays(row: pd.Series) -> str:
        parts = []
        for col in essay_cols:
            val = row[col]
            if pd.notna(val) and str(val).strip():
                prompt_name = col.replace("_", " ").strip()
                parts.append(f"[{prompt_name}]\n{str(val).strip()}")
        return "\n\n---\n\n".join(parts)

    sec_df["_combined"] = sec_df[essay_cols].apply(_concat_essays, axis=1)
    valid = sec_df["_combined"].str.len() > 0
    result = dict(zip(
        sec_df.loc[valid, ID_COLUMN].astype(int),
        sec_df.loc[valid, "_combined"],
    ))

    logger.info("Loaded %d secondary essay sets", len(result))
    return result
