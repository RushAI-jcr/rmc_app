---
status: resolved
priority: P3
issue_id: 020
tags: [style, type-hints, consistency]
---

# Legacy Type Hints in `rubric_scorer_v2.py`

## Problem Statement

`rubric_scorer_v2.py` uses `Dict`, `List`, `Optional` from `typing` instead of modern `dict`, `list`, `X | None` syntax. The rest of the codebase uses modern syntax.

## Findings

- `pipeline/rubric_scorer_v2.py`: imports and uses `Dict`, `List`, `Optional` from `typing`
- All other modules use Python 3.10+ built-in generics and union syntax

## Proposed Solutions

- Replace `Dict[K, V]` with `dict[K, V]`
- Replace `List[T]` with `list[T]`
- Replace `Optional[T]` with `T | None`
- Remove unused `typing` imports
