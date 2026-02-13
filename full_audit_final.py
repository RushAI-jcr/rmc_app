#!/usr/bin/env python3
"""
Complete audit of all raw Excel files - generates markdown report.
Run with: python3 full_audit_final.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/JCR/Desktop/rmc_every/data/raw")
OUTPUT_FILE = BASE_DIR / "raw_data_audit.md"

def analyze_df(df, filename, year):
    """Extract comprehensive info from a dataframe."""
    info = {
        'filename': filename,
        'year': year,
        'rows': len(df),
        'cols': len(df.columns),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing': {col: int(df[col].isnull().sum()) for col in df.columns},
        'missing_pct': {col: round(float(df[col].isnull().sum()) / len(df) * 100, 2) for col in df.columns},
        'unique': {col: int(df[col].nunique()) for col in df.columns},
        'sample': []
    }

    # Sample rows
    for idx in range(min(3, len(df))):
        row_data = {}
        for col in df.columns:
            val = df.iloc[idx][col]
            if pd.isna(val):
                row_data[col] = None
            elif isinstance(val, (int, np.integer)):
                row_data[col] = int(val)
            elif isinstance(val, (float, np.floating)):
                if np.isnan(val):
                    row_data[col] = None
                else:
                    row_data[col] = float(val)
            else:
                row_data[col] = str(val)
        info['sample'].append(row_data)

    # Categorical distributions (low cardinality)
    info['categorical'] = {}
    for col in df.columns:
        if 1 < df[col].nunique() <= 30:
            vc = df[col].value_counts().head(15)
            info['categorical'][col] = {str(k): int(v) for k, v in vc.items()}

    # Numeric stats
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        stats = df[numeric_cols].describe()
        info['numeric_stats'] = {}
        for col in numeric_cols:
            info['numeric_stats'][col] = {
                'mean': float(stats[col]['mean']),
                'std': float(stats[col]['std']),
                'min': float(stats[col]['min']),
                '25%': float(stats[col]['25%']),
                '50%': float(stats[col]['50%']),
                '75%': float(stats[col]['75%']),
                'max': float(stats[col]['max'])
            }

    return info

def main():
    """Main audit function."""
    print("Starting comprehensive audit...")

    # Collect all data
    all_data = {}

    for year in [2022, 2023, 2024]:
        print(f"\nProcessing {year}...")
        year_dir = BASE_DIR / str(year)
        all_data[year] = {}

        for xlsx_file in sorted(year_dir.glob("*.xlsx")):
            print(f"  Reading {xlsx_file.name}...")
            try:
                df = pd.read_excel(xlsx_file)
                info = analyze_df(df, xlsx_file.name, year)
                all_data[year][xlsx_file.name] = info
            except Exception as e:
                print(f"    ERROR: {e}")
                all_data[year][xlsx_file.name] = {'error': str(e)}

    # Generate markdown
    print("\nGenerating markdown report...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Header
        f.write("# Raw Data Audit Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**Purpose:** Comprehensive examination of all raw Excel files across 2022, 2023, and 2024.\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")

        for year in [2022, 2023, 2024]:
            f.write(f"### {year} Data Overview\n\n")
            f.write("| File | Rows | Columns |\n")
            f.write("|------|------|--------|\n")

            for fname in sorted(all_data[year].keys()):
                info = all_data[year][fname]
                if 'error' not in info:
                    f.write(f"| {fname} | {info['rows']:,} | {info['cols']} |\n")
                else:
                    f.write(f"| {fname} | ERROR | - |\n")

            f.write("\n")

        f.write("---\n\n")

        # Get all unique files (normalize School/Schools)
        all_files = set()
        for year_data in all_data.values():
            for fname in year_data.keys():
                normalized = fname.replace("8. School.xlsx", "8. Schools.xlsx")
                all_files.add(normalized)

        f.write("## Detailed File Analysis\n\n")

        # Process each file
        for fname in sorted(all_files):
            f.write(f"\n{'='*80}\n")
            f.write(f"## {fname}\n")
            f.write(f"{'='*80}\n\n")

            # Year overview
            f.write("### Year-over-Year Overview\n\n")
            f.write("| Year | Rows | Columns | Status |\n")
            f.write("|------|------|---------|--------|\n")

            year_data_map = {}
            for year in [2022, 2023, 2024]:
                # Check both naming conventions
                actual_fname = None
                if fname in all_data[year]:
                    actual_fname = fname
                elif fname == "8. Schools.xlsx" and "8. School.xlsx" in all_data[year]:
                    actual_fname = "8. School.xlsx"

                if actual_fname and 'error' not in all_data[year][actual_fname]:
                    info = all_data[year][actual_fname]
                    f.write(f"| {year} | {info['rows']:,} | {info['cols']} | ✓ |\n")
                    year_data_map[year] = info
                elif actual_fname and 'error' in all_data[year][actual_fname]:
                    f.write(f"| {year} | - | - | ERROR |\n")
                else:
                    f.write(f"| {year} | - | - | NOT FOUND |\n")

            f.write("\n")

            # Detailed analysis per year
            for year in [2022, 2023, 2024]:
                if year not in year_data_map:
                    continue

                info = year_data_map[year]

                f.write(f"### {year} Analysis\n\n")

                # Schema
                f.write("#### Schema\n\n")
                f.write("| Column | Type | Non-Null | Unique | Missing % |\n")
                f.write("|--------|------|----------|--------|----------|\n")

                for col in info['columns']:
                    dtype = info['dtypes'][col]
                    missing = info['missing'][col]
                    non_null = info['rows'] - missing
                    unique = info['unique'][col]
                    missing_pct = info['missing_pct'][col]

                    f.write(f"| {col} | {dtype} | {non_null:,} | {unique:,} | {missing_pct:.1f}% |\n")

                f.write("\n")

                # Sample data
                f.write("#### Sample Data\n\n")
                f.write("```\n")
                for i, row in enumerate(info['sample'], 1):
                    f.write(f"Row {i}:\n")
                    for col in list(row.keys())[:12]:  # Limit for readability
                        val = row[col]
                        if val is None:
                            val_str = "NULL"
                        elif isinstance(val, float):
                            val_str = f"{val:.2f}"
                        else:
                            val_str = str(val)[:50]
                        f.write(f"  {col}: {val_str}\n")
                    if len(row) > 12:
                        f.write(f"  ... (and {len(row)-12} more columns)\n")
                    f.write("\n")
                f.write("```\n\n")

                # Categorical distributions
                if info.get('categorical'):
                    f.write("#### Categorical Distributions\n\n")
                    for col, dist in list(info['categorical'].items())[:8]:
                        f.write(f"**{col}** ({len(dist)} values shown):\n\n")
                        for val, count in list(dist.items())[:12]:
                            pct = count / info['rows'] * 100
                            f.write(f"- `{val}`: {count:,} ({pct:.1f}%)\n")
                        f.write("\n")

                # Numeric stats
                if info.get('numeric_stats'):
                    f.write("#### Numeric Statistics\n\n")
                    f.write("| Column | Mean | Std | Min | 25% | 50% | 75% | Max |\n")
                    f.write("|--------|------|-----|-----|-----|-----|-----|-----|\n")

                    for col, stats in info['numeric_stats'].items():
                        f.write(f"| {col} | {stats['mean']:.2f} | {stats['std']:.2f} | "
                               f"{stats['min']:.2f} | {stats['25%']:.2f} | {stats['50%']:.2f} | "
                               f"{stats['75%']:.2f} | {stats['max']:.2f} |\n")

                    f.write("\n")

                # Data quality issues
                issues = []
                for col in info['columns']:
                    missing_pct = info['missing_pct'][col]
                    unique = info['unique'][col]

                    if missing_pct == 100:
                        issues.append(f"EMPTY: `{col}` is completely null")
                    elif missing_pct > 50:
                        issues.append(f"HIGH MISSINGNESS: `{col}` is {missing_pct:.1f}% null")

                    if unique == 1 and info['rows'] > 1:
                        issues.append(f"CONSTANT: `{col}` has only 1 unique value")

                if issues:
                    f.write("#### Data Quality Issues\n\n")
                    for issue in issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")

            # Schema consistency
            if len(year_data_map) > 1:
                f.write("### Schema Consistency\n\n")

                # Collect columns per year
                year_columns = {year: set(info['columns']) for year, info in year_data_map.items()}

                all_cols = set()
                for cols in year_columns.values():
                    all_cols.update(cols)

                f.write("| Column | 2022 | 2023 | 2024 |\n")
                f.write("|--------|------|------|------|\n")

                for col in sorted(all_cols):
                    p2022 = "✓" if 2022 in year_columns and col in year_columns[2022] else "✗"
                    p2023 = "✓" if 2023 in year_columns and col in year_columns[2023] else "✗"
                    p2024 = "✓" if 2024 in year_columns and col in year_columns[2024] else "✗"

                    f.write(f"| {col} | {p2022} | {p2023} | {p2024} |\n")

                f.write("\n")

        # Recommendations section
        f.write("---\n\n")
        f.write("## Analysis Summary\n\n")

        f.write("### Column Classification for ML\n\n")

        f.write("#### Identifiers (DO NOT use as features)\n")
        f.write("- Applicant_ID, Application_ID, Record_ID\n")
        f.write("- School codes, Institution IDs\n")
        f.write("- Any PII (names, SSN, addresses)\n\n")

        f.write("#### Protected Attributes (Bias risk)\n")
        f.write("- Race, Ethnicity\n")
        f.write("- Gender\n")
        f.write("- Age, Date of Birth\n")
        f.write("- Citizenship, Disadvantaged status\n")
        f.write("- Geographic location\n\n")

        f.write("#### Numeric Features (ML-ready)\n")
        f.write("- Test scores: MCAT, GPA (overall, science, non-science)\n")
        f.write("- Counts: experiences, languages, siblings, schools\n")
        f.write("- Durations: months of experience, gap years\n")
        f.write("- Academic metrics: credit hours, grades\n\n")

        f.write("#### Categorical Features (Encode)\n")
        f.write("- Application type, status, decision\n")
        f.write("- School type, degree, major\n")
        f.write("- Experience categories\n")
        f.write("- Binary Yes/No flags\n\n")

        f.write("#### Text Features (NLP)\n")
        f.write("- Personal statements\n")
        f.write("- Secondary essays\n")
        f.write("- Experience descriptions\n\n")

        f.write("#### Temporal Features\n")
        f.write("- Application dates\n")
        f.write("- GPA trends\n")
        f.write("- Experience timelines\n\n")

        f.write("### Data Cleaning Checklist\n\n")

        f.write("**High Priority:**\n\n")
        f.write("1. Standardize column names across years\n")
        f.write("2. Handle missing values (drop, impute, or indicator)\n")
        f.write("3. Validate ID consistency across tables\n")
        f.write("4. Parse dates to datetime format\n")
        f.write("5. Document schema changes\n\n")

        f.write("**Medium Priority:**\n\n")
        f.write("6. Encode categorical variables\n")
        f.write("7. Aggregate child tables to applicant level\n")
        f.write("8. Text preprocessing\n")
        f.write("9. Feature engineering (derived metrics)\n")
        f.write("10. Outlier detection\n\n")

        f.write("**Low Priority:**\n\n")
        f.write("11. Business logic validation\n")
        f.write("12. Create data dictionary\n")
        f.write("13. Version control transformations\n\n")

        f.write("### Temporal Training Strategy\n\n")

        f.write("For temporal validation:\n\n")
        f.write("- **Training:** 2022 + 2023 data combined\n")
        f.write("- **Test:** 2024 data held out\n")
        f.write("- **Validation:** K-fold cross-validation within 2022+2023\n")
        f.write("- **Monitor:** Distribution shifts across years\n")
        f.write("- **Caution:** Check if target variable distribution is consistent\n\n")

        f.write("---\n\n")
        f.write("**End of Report**\n")

    print(f"\n✓ Report saved to: {OUTPUT_FILE}")
    print(f"✓ File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
