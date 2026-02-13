"""
Comprehensive audit of all raw Excel files across 2022, 2023, and 2024.
Analyzes schema, data quality, missingness, and year-over-year consistency.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Base directory
BASE_DIR = Path("/Users/JCR/Desktop/rmc_every/data/raw")

# File mapping (accounting for naming differences)
FILES = {
    '1. Applicants.xlsx': 'Applicants',
    '2. Language.xlsx': 'Language',
    '3. Parents.xlsx': 'Parents',
    '4. Siblings.xlsx': 'Siblings',
    '5. Academic Records.xlsx': 'Academic Records',
    '6. Experiences.xlsx': 'Experiences',
    '8. Schools.xlsx': 'Schools',  # 2022-2023
    '8. School.xlsx': 'Schools',   # 2024
    '9. Personal Statement.xlsx': 'Personal Statement',
    '10. Secondary Application.xlsx': 'Secondary Application',
    '11. Military.xlsx': 'Military',
    '12. GPA Trend.xlsx': 'GPA Trend',
}

def analyze_dataframe(df, year, file_name):
    """Comprehensive analysis of a single dataframe."""
    analysis = {
        'year': year,
        'file': file_name,
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'row_count': len(df),
        'col_count': len(df.columns),
    }

    # Sample data (first 3 rows)
    analysis['sample_data'] = df.head(3).to_dict('records')

    # Missingness analysis
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    analysis['missing_counts'] = missing.to_dict()
    analysis['missing_pct'] = missing_pct.to_dict()

    # Unique value counts for each column
    unique_counts = {}
    categorical_samples = {}

    for col in df.columns:
        n_unique = df[col].nunique()
        unique_counts[col] = n_unique

        # For categorical columns (fewer unique values), get sample values
        if n_unique <= 50 and n_unique > 0:
            value_counts = df[col].value_counts()
            categorical_samples[col] = value_counts.head(10).to_dict()

    analysis['unique_counts'] = unique_counts
    analysis['categorical_samples'] = categorical_samples

    # Data type summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    analysis['numeric_cols'] = numeric_cols
    analysis['object_cols'] = object_cols
    analysis['datetime_cols'] = datetime_cols

    # Basic statistics for numeric columns
    if numeric_cols:
        numeric_stats = df[numeric_cols].describe().to_dict()
        analysis['numeric_stats'] = numeric_stats

    return analysis

def load_and_analyze_all_files():
    """Load and analyze all files across all years."""
    results = {}

    for year in [2022, 2023, 2024]:
        year_dir = BASE_DIR / str(year)
        results[year] = {}

        print(f"\n{'='*80}")
        print(f"ANALYZING YEAR {year}")
        print(f"{'='*80}")

        # Handle different file names for Schools/School
        for file_path in year_dir.glob("*.xlsx"):
            file_name = file_path.name

            # Normalize Schools/School naming
            normalized_name = FILES.get(file_name, file_name.replace('.xlsx', ''))

            try:
                print(f"\nLoading {file_name}...")
                df = pd.read_excel(file_path)
                print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")

                analysis = analyze_dataframe(df, year, file_name)
                results[year][normalized_name] = analysis

            except Exception as e:
                print(f"  ERROR loading {file_name}: {e}")
                results[year][normalized_name] = {'error': str(e)}

    return results

def generate_markdown_report(results, output_path):
    """Generate comprehensive markdown report."""

    with open(output_path, 'w') as f:
        f.write("# Raw Data Audit Report\n\n")
        f.write("**Generated:** 2026-02-13\n\n")
        f.write("**Purpose:** Comprehensive examination of all raw Excel files across 2022, 2023, and 2024.\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")

        for year in [2022, 2023, 2024]:
            f.write(f"### {year} Data Overview\n\n")
            year_data = results[year]

            f.write("| File | Rows | Columns |\n")
            f.write("|------|------|--------|\n")

            for file_name, analysis in year_data.items():
                if 'error' not in analysis:
                    f.write(f"| {file_name} | {analysis['row_count']:,} | {analysis['col_count']} |\n")
                else:
                    f.write(f"| {file_name} | ERROR | ERROR |\n")

            f.write("\n")

        # Detailed Analysis by File
        f.write("---\n\n")
        f.write("## Detailed File Analysis\n\n")

        # Get all unique file names across years
        all_files = set()
        for year_data in results.values():
            all_files.update(year_data.keys())

        for file_name in sorted(all_files):
            f.write(f"\n{'='*80}\n")
            f.write(f"## FILE: {file_name}\n")
            f.write(f"{'='*80}\n\n")

            # Year-over-year comparison
            f.write("### Year-over-Year Overview\n\n")
            f.write("| Year | Rows | Columns | Status |\n")
            f.write("|------|------|---------|--------|\n")

            for year in [2022, 2023, 2024]:
                if file_name in results[year]:
                    analysis = results[year][file_name]
                    if 'error' not in analysis:
                        f.write(f"| {year} | {analysis['row_count']:,} | {analysis['col_count']} | OK |\n")
                    else:
                        f.write(f"| {year} | - | - | ERROR: {analysis['error']} |\n")
                else:
                    f.write(f"| {year} | - | - | NOT FOUND |\n")

            f.write("\n")

            # Detailed analysis for each year
            for year in [2022, 2023, 2024]:
                if file_name not in results[year] or 'error' in results[year][file_name]:
                    continue

                analysis = results[year][file_name]

                f.write(f"### {year} Detailed Analysis\n\n")

                # Schema
                f.write("#### Column Schema\n\n")
                f.write("| Column Name | Data Type | Non-Null Count | Unique Values | Missing % |\n")
                f.write("|-------------|-----------|----------------|---------------|----------|\n")

                for col in analysis['columns']:
                    dtype = str(analysis['dtypes'][col])
                    non_null = analysis['row_count'] - analysis['missing_counts'][col]
                    unique = analysis['unique_counts'][col]
                    missing_pct = analysis['missing_pct'][col]
                    f.write(f"| {col} | {dtype} | {non_null:,} | {unique:,} | {missing_pct:.1f}% |\n")

                f.write("\n")

                # Sample Data
                f.write("#### Sample Data (First 3 Rows)\n\n")
                f.write("```\n")
                for i, row in enumerate(analysis['sample_data'], 1):
                    f.write(f"Row {i}:\n")
                    for key, val in row.items():
                        f.write(f"  {key}: {val}\n")
                    f.write("\n")
                f.write("```\n\n")

                # Categorical value distributions
                if analysis['categorical_samples']:
                    f.write("#### Categorical Column Value Distributions\n\n")
                    for col, values in analysis['categorical_samples'].items():
                        f.write(f"**{col}** (Top values):\n")
                        for val, count in values.items():
                            pct = (count / analysis['row_count'] * 100)
                            f.write(f"- {val}: {count:,} ({pct:.1f}%)\n")
                        f.write("\n")

                # Numeric statistics
                if 'numeric_stats' in analysis and analysis['numeric_stats']:
                    f.write("#### Numeric Column Statistics\n\n")
                    f.write("| Column | Mean | Std | Min | 25% | 50% | 75% | Max |\n")
                    f.write("|--------|------|-----|-----|-----|-----|-----|-----|\n")

                    for col in analysis['numeric_cols']:
                        if col in analysis['numeric_stats']:
                            stats = analysis['numeric_stats'][col]
                            f.write(f"| {col} | {stats.get('mean', 0):.2f} | {stats.get('std', 0):.2f} | "
                                   f"{stats.get('min', 0):.2f} | {stats.get('25%', 0):.2f} | "
                                   f"{stats.get('50%', 0):.2f} | {stats.get('75%', 0):.2f} | "
                                   f"{stats.get('max', 0):.2f} |\n")

                    f.write("\n")

                f.write("\n")

            # Schema consistency check
            f.write("### Schema Consistency Analysis\n\n")

            # Get columns for each year
            year_columns = {}
            for year in [2022, 2023, 2024]:
                if file_name in results[year] and 'error' not in results[year][file_name]:
                    year_columns[year] = set(results[year][file_name]['columns'])

            if len(year_columns) > 1:
                # Check for column differences
                all_cols = set()
                for cols in year_columns.values():
                    all_cols.update(cols)

                f.write("| Column | 2022 | 2023 | 2024 |\n")
                f.write("|--------|------|------|------|\n")

                for col in sorted(all_cols):
                    present_2022 = '✓' if 2022 in year_columns and col in year_columns[2022] else '✗'
                    present_2023 = '✓' if 2023 in year_columns and col in year_columns[2023] else '✗'
                    present_2024 = '✓' if 2024 in year_columns and col in year_columns[2024] else '✗'
                    f.write(f"| {col} | {present_2022} | {present_2023} | {present_2024} |\n")

                f.write("\n")

                # Identify schema changes
                if len(year_columns) >= 2:
                    years = sorted(year_columns.keys())
                    for i in range(len(years) - 1):
                        year1, year2 = years[i], years[i+1]
                        cols1, cols2 = year_columns[year1], year_columns[year2]

                        added = cols2 - cols1
                        removed = cols1 - cols2

                        if added or removed:
                            f.write(f"**Changes from {year1} to {year2}:**\n")
                            if added:
                                f.write(f"- Added columns: {', '.join(sorted(added))}\n")
                            if removed:
                                f.write(f"- Removed columns: {', '.join(sorted(removed))}\n")
                            f.write("\n")

        # Data Quality Summary
        f.write("\n---\n\n")
        f.write("## Data Quality Summary\n\n")

        for year in [2022, 2023, 2024]:
            f.write(f"### {year} Data Quality Issues\n\n")

            for file_name, analysis in results[year].items():
                if 'error' in analysis:
                    continue

                issues = []

                # High missingness
                for col, pct in analysis['missing_pct'].items():
                    if pct > 50:
                        issues.append(f"High missingness in '{col}': {pct:.1f}%")

                # All null columns
                for col, count in analysis['missing_counts'].items():
                    if count == analysis['row_count']:
                        issues.append(f"Completely empty column: '{col}'")

                # Single value columns (potential constants)
                for col, unique in analysis['unique_counts'].items():
                    if unique == 1 and analysis['row_count'] > 1:
                        issues.append(f"Single unique value in '{col}' (potential constant)")

                if issues:
                    f.write(f"**{file_name}:**\n")
                    for issue in issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")

        # Feature Engineering Recommendations
        f.write("\n---\n\n")
        f.write("## Feature Engineering Recommendations\n\n")

        f.write("### Potential Features by Category\n\n")

        f.write("#### Identifiers (DO NOT use as features)\n")
        f.write("- Applicant IDs, Application IDs\n")
        f.write("- School IDs, Institution codes\n")
        f.write("- Any PII (names, addresses, SSN, etc.)\n\n")

        f.write("#### Protected Attributes (Use with caution, potential bias)\n")
        f.write("- Race/Ethnicity indicators\n")
        f.write("- Gender\n")
        f.write("- Age\n")
        f.write("- Citizenship/Immigration status\n")
        f.write("- Geographic location (can proxy for socioeconomic status)\n\n")

        f.write("#### Numeric Features (Structured, ML-ready)\n")
        f.write("- Test scores (MCAT, GPA, etc.)\n")
        f.write("- Counts (number of experiences, siblings, languages, etc.)\n")
        f.write("- Durations (months of experience, gap years)\n")
        f.write("- Academic metrics (credit hours, course grades)\n\n")

        f.write("#### Categorical Features (Require encoding)\n")
        f.write("- School types, degree types\n")
        f.write("- Experience categories\n")
        f.write("- Application status flags\n")
        f.write("- Yes/No binary indicators\n\n")

        f.write("#### Text Features (Require NLP processing)\n")
        f.write("- Personal statements\n")
        f.write("- Secondary application essays\n")
        f.write("- Experience descriptions\n\n")

        f.write("#### Temporal Features\n")
        f.write("- Application dates\n")
        f.write("- GPA trends over time\n")
        f.write("- Experience date ranges\n\n")

        # Recommendations
        f.write("\n---\n\n")
        f.write("## Recommendations for Data Cleaning\n\n")

        f.write("### High Priority\n\n")
        f.write("1. **Standardize column names** across years (handle Schools vs School)\n")
        f.write("2. **Handle missing values** - determine if missing is informative\n")
        f.write("3. **Validate ID consistency** - ensure applicant IDs match across files\n")
        f.write("4. **Encode categorical variables** - create consistent encoding scheme\n")
        f.write("5. **Standardize date formats** - parse all dates to datetime objects\n\n")

        f.write("### Medium Priority\n\n")
        f.write("6. **Text preprocessing** - clean personal statements, remove special characters\n")
        f.write("7. **Outlier detection** - identify and handle extreme values in scores\n")
        f.write("8. **Feature aggregation** - roll up child tables to applicant level\n")
        f.write("9. **Create derived features** - GPA trends, experience diversity, etc.\n\n")

        f.write("### Low Priority\n\n")
        f.write("10. **Data validation** - check for logical inconsistencies\n")
        f.write("11. **Documentation** - create data dictionary with all fields\n")
        f.write("12. **Versioning** - track data lineage and transformations\n\n")

if __name__ == "__main__":
    print("Starting comprehensive raw data audit...")
    print(f"Base directory: {BASE_DIR}")

    # Run analysis
    results = load_and_analyze_all_files()

    # Generate report
    output_path = "/Users/JCR/Desktop/rmc_every/data/raw_data_audit.md"
    print(f"\n\nGenerating markdown report: {output_path}")
    generate_markdown_report(results, output_path)

    print(f"\n✓ Audit complete! Report saved to {output_path}")
