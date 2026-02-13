---
status: pending
priority: p2
issue_id: "010"
tags: [code-review, performance, validation, excel]
---

# Double Excel File Read During Validation

## Problem Statement
`validate_session()` reads each Excel file twice: once with `nrows=5` for schema validation and once fully to get the row count. For large Excel files this doubles I/O time and memory pressure unnecessarily.

## Findings
- **Location**: `api/services/upload_service.py` lines 141-142
- **Agents**: performance-oracle, simplicity-reviewer, architecture-strategist
- **Evidence**: Two separate `pd.read_excel()` calls on the same file. The first reads 5 rows for column checking, the second reads the entire file just to count rows via `len(df)`.

## Proposed Solutions
Read the file once and reuse the result:
```python
df_full = pd.read_excel(file_path, engine="openpyxl")
row_count = len(df_full)
df_preview = df_full.head(5)
# Use df_preview for schema validation, row_count for size checks
```

## Acceptance Criteria
- [ ] Each Excel file is read exactly once during validation
- [ ] Row count and preview are derived from the single read
- [ ] Schema validation behavior is unchanged
- [ ] Performance improvement is measurable on files > 10 MB
