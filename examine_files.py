#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

base = Path("/Users/JCR/Desktop/rmc_every/data/raw")

# Just examine 2022 Applicants first
file = base / "2022" / "1. Applicants.xlsx"
df = pd.read_excel(file)

print("APPLICANTS 2022")
print("="*80)
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nMissing:\n{df.isnull().sum()}")
print(f"\nUnique counts:\n{df.nunique()}")
print(f"\nFirst 3 rows:\n{df.head(3)}")

# Save to text
output = base / "applicants_2022_info.txt"
with open(output, 'w') as f:
    f.write("APPLICANTS 2022\n")
    f.write("="*80 + "\n")
    f.write(f"Shape: {df.shape}\n\n")
    f.write(f"Columns ({len(df.columns)}):\n")
    for i, col in enumerate(df.columns, 1):
        f.write(f"{i:3d}. {col}\n")

    f.write(f"\n\nColumn Details:\n")
    for col in df.columns:
        f.write(f"\n{col}:\n")
        f.write(f"  Type: {df[col].dtype}\n")
        f.write(f"  Null: {df[col].isnull().sum()} ({df[col].isnull().sum()/len(df)*100:.1f}%)\n")
        f.write(f"  Unique: {df[col].nunique()}\n")

        if df[col].nunique() <= 20 and df[col].nunique() > 0:
            f.write(f"  Values:\n")
            vc = df[col].value_counts()
            for val, count in vc.items():
                f.write(f"    {val}: {count}\n")

print(f"\nSaved to {output}")
