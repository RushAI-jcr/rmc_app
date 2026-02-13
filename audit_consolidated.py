"""
Consolidated audit - writes markdown directly.
Run this with: python3 audit_consolidated.py > /Users/JCR/Desktop/rmc_every/data/raw_data_audit.md
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/Users/JCR/Desktop/rmc_every/data/raw")

def print_header(text, level=1):
    """Print markdown header."""
    print(f"\n{'#' * level} {text}\n")

def print_table_row(*cols):
    """Print markdown table row."""
    print("|" + "|".join(str(c) for c in cols) + "|")

def audit_file(filepath, year):
    """Audit and print markdown for a single file."""
    try:
        df = pd.read_excel(filepath)

        print(f"\n{'='*80}")
        print_header(f"{filepath.name} - {year}", 3)

        print(f"**Shape:** {len(df):,} rows × {len(df.columns)} columns\n")

        # Column schema table
        print_header("Column Schema", 4)
        print_table_row("Column", "Type", "Non-Null", "Unique", "Missing %")
        print_table_row("---", "---", "---", "---", "---")

        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            unique = df[col].nunique()
            missing_pct = (df[col].isnull().sum() / len(df) * 100)
            print_table_row(col, dtype, f"{non_null:,}", f"{unique:,}", f"{missing_pct:.1f}%")

        # Sample data
        print_header("Sample Data (First 3 Rows)", 4)
        print("```")
        for idx in range(min(3, len(df))):
            print(f"Row {idx+1}:")
            for col in list(df.columns)[:15]:  # Limit columns for readability
                val = df.iloc[idx][col]
                if pd.isna(val):
                    val_str = "NULL"
                else:
                    val_str = str(val)[:50]
                print(f"  {col}: {val_str}")
            if len(df.columns) > 15:
                print(f"  ... ({len(df.columns) - 15} more columns)")
            print()
        print("```\n")

        # Categorical distributions
        cat_cols = [col for col in df.columns if 1 < df[col].nunique() <= 30]
        if cat_cols:
            print_header("Categorical Distributions", 4)
            for col in cat_cols[:10]:  # Limit to first 10
                print(f"\n**{col}** ({df[col].nunique()} unique values):\n")
                vc = df[col].value_counts().head(10)
                for val, count in vc.items():
                    pct = count / len(df) * 100
                    print(f"- `{val}`: {count:,} ({pct:.1f}%)")

        # Numeric stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print_header("Numeric Statistics", 4)
            print_table_row("Column", "Mean", "Std", "Min", "25%", "50%", "75%", "Max")
            print_table_row("---", "---", "---", "---", "---", "---", "---", "---")

            stats = df[numeric_cols].describe()
            for col in numeric_cols:
                print_table_row(
                    col,
                    f"{stats[col]['mean']:.2f}",
                    f"{stats[col]['std']:.2f}",
                    f"{stats[col]['min']:.2f}",
                    f"{stats[col]['25%']:.2f}",
                    f"{stats[col]['50%']:.2f}",
                    f"{stats[col]['75%']:.2f}",
                    f"{stats[col]['max']:.2f}"
                )

        # Quality issues
        issues = []
        for col in df.columns:
            missing_pct = df[col].isnull().sum() / len(df) * 100
            if missing_pct > 50:
                issues.append(f"HIGH MISSINGNESS: {col} ({missing_pct:.1f}% null)")
            if missing_pct == 100:
                issues.append(f"COMPLETELY EMPTY: {col}")
            if df[col].nunique() == 1 and len(df) > 1:
                issues.append(f"CONSTANT VALUE: {col}")

        if issues:
            print_header("Data Quality Issues", 4)
            for issue in issues:
                print(f"- {issue}")

        return df.columns.tolist()

    except Exception as e:
        print(f"\n**ERROR loading {filepath.name}:** {e}\n")
        return []

# Main audit
print_header("Raw Data Audit Report", 1)
print("**Generated:** 2026-02-13")
print("**Purpose:** Comprehensive examination of all raw Excel files across 2022, 2023, and 2024.\n")
print("---\n")

# Executive summary
print_header("Executive Summary", 2)

files_map = {}

for year in [2022, 2023, 2024]:
    print_header(f"{year} Overview", 3)
    print_table_row("File", "Rows", "Columns")
    print_table_row("---", "---", "---")

    year_dir = BASE / str(year)
    year_files = sorted(year_dir.glob("*.xlsx"))

    for fpath in year_files:
        try:
            df = pd.read_excel(fpath)
            print_table_row(fpath.name, f"{len(df):,}", len(df.columns))

            # Track files for schema comparison
            normalized_name = fpath.name.replace("School.xlsx", "Schools.xlsx")
            if normalized_name not in files_map:
                files_map[normalized_name] = {}
            files_map[normalized_name][year] = fpath

        except Exception as e:
            print_table_row(fpath.name, "ERROR", "-")

print("\n---\n")

# Detailed analysis
print_header("Detailed File Analysis", 2)

for fname in sorted(files_map.keys()):
    print(f"\n{'='*80}")
    print_header(f"FILE: {fname}", 2)
    print(f"{'='*80}\n")

    # Year overview for this file
    print_header("Year-over-Year Summary", 3)
    print_table_row("Year", "Rows", "Columns", "Status")
    print_table_row("---", "---", "---", "---")

    year_columns = {}

    for year in [2022, 2023, 2024]:
        if year in files_map[fname]:
            fpath = files_map[fname][year]
            try:
                df = pd.read_excel(fpath)
                print_table_row(year, f"{len(df):,}", len(df.columns), "✓")
                year_columns[year] = set(df.columns)
            except:
                print_table_row(year, "-", "-", "ERROR")
        else:
            print_table_row(year, "-", "-", "NOT FOUND")

    # Detailed audit for each year
    for year in [2022, 2023, 2024]:
        if year in files_map[fname]:
            audit_file(files_map[fname][year], year)

    # Schema consistency
    if len(year_columns) > 1:
        print_header("Schema Consistency Analysis", 3)

        all_cols = set()
        for cols in year_columns.values():
            all_cols.update(cols)

        print_table_row("Column", "2022", "2023", "2024", "Notes")
        print_table_row("---", "---", "---", "---", "---")

        for col in sorted(all_cols):
            p2022 = "✓" if 2022 in year_columns and col in year_columns[2022] else "✗"
            p2023 = "✓" if 2023 in year_columns and col in year_columns[2023] else "✗"
            p2024 = "✓" if 2024 in year_columns and col in year_columns[2024] else "✗"

            notes = ""
            if p2022 == "✗" and p2023 == "✓":
                notes = "Added 2023"
            elif p2023 == "✓" and p2024 == "✗":
                notes = "Removed 2024"
            elif p2022 == "✓" and p2023 == "✗":
                notes = "Removed 2023"

            print_table_row(col, p2022, p2023, p2024, notes)

# Final recommendations
print("\n---\n")
print_header("Feature Engineering Recommendations", 2)

print("""
### Column Categories

**Identifiers (DO NOT use as features):**
- Applicant_ID, Application_ID, Record_ID, School_ID
- Any personally identifiable information (names, SSN, addresses)

**Protected Attributes (Bias risk):**
- Race, Ethnicity, Gender
- Age, Date of Birth
- Citizenship, Immigration status
- Geographic location (can proxy SES)
- Disadvantaged/URiM flags

**Numeric Features (ML-ready):**
- Test scores: MCAT, GPA (overall, science, non-science)
- Counts: experiences, languages, siblings, schools
- Durations: months of experience, gap years
- Academic: credit hours, grades, GPA trends

**Categorical Features (Need encoding):**
- Application type, status, decision
- School type, degree, major
- Experience categories
- Binary Yes/No indicators
- Geographic codes

**Text Features (Need NLP):**
- Personal statements
- Secondary essays
- Experience descriptions

**Temporal Features:**
- Application dates
- Decision dates
- GPA progression over time
""")

print_header("Data Cleaning Priorities", 2)

print("""
### High Priority
1. Standardize column names across years
2. Define missing value strategy (drop, impute, or feature)
3. Validate ID consistency across related tables
4. Parse all dates to datetime format
5. Document all year-over-year schema changes

### Medium Priority
6. Encode categorical variables
7. Aggregate child tables to applicant level
8. Text preprocessing
9. Create derived features (experience diversity, GPA slopes)
10. Outlier detection and handling

### Low Priority
11. Business logic validation
12. Create data dictionary
13. Track transformation lineage

### Temporal Training Strategy
- **Training:** 2022 + 2023 combined
- **Testing:** 2024 held out
- **Validation:** K-fold CV within training set
- **Caution:** Monitor for distribution shifts across years
""")

print("\n---\n")
print("**End of Report**")
