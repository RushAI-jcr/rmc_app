---
status: pending
priority: P1
issue_id: 027
tags: [code-review, architecture, simplicity]
dependencies: []
---

# Plan Scope Contains 60-70% YAGNI for MVP

## Problem Statement
The simplicity reviewer found 60-70% of the plan is YAGNI for an MVP. The true MVP to "serve scores to reviewers this cycle" is ~100-150 lines across 6 items: (A) auth on endpoints, (B) role-based sidebar filtering, (C) inline rubric on review page, (D) login redirect by role, (E) strip SHAP from staff response, (F) auto-resume at first unreviewed. The plan compounds a security fix with a PostgreSQL migration, UserContext provider, /progress endpoint, keyboard shortcuts, concurrent reviewer awareness, dashboard cards, audit trail, and localStorage recovery — turning a 2-hour fix into a multi-day project.

## Findings
Simplicity reviewer identified 10 specific YAGNI violations. Items the reviewer recommends cutting: PostgreSQL migration (use file lock instead), UserContext provider (call getMe() in sidebar), keyboard shortcuts, "Change Decision" feature, concurrent reviewer awareness, audit log on decision change, /progress endpoint, JWT localStorage recovery, dashboard flag/progress cards, "Other" text min-length validation.

## Proposed Solutions
### Option A: Reduce plan to MVP-only phase (Recommended)
Reduce plan to a single phase with items A-F. Ship, get feedback from real reviewers, then decide on Phase 2+ based on actual usage.
- Pros: Ships in hours not days, validates with real users first
- Cons: Defers useful features that may be needed
- Effort: Small (plan rewrite)

### Option B: Label MVP gate within existing plan
Keep plan structure but explicitly label items A-F as "MVP Gate" and everything else as "Post-MVP". Implement A-F first, validate, then continue.
- Pros: Preserves existing planning work, clear priority ordering
- Cons: Temptation to scope-creep into post-MVP items
- Effort: Small (plan annotation)

## Technical Details
- Affected files: `docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md`
- Components: Plan document, project scope

## Acceptance Criteria
- [ ] Plan clearly separates MVP-gate items from post-MVP enhancements
- [ ] MVP items can be implemented in <1 day
- [ ] No unnecessary abstractions block the critical path

## Work Log
- 2026-02-13: Created from plan review

## Resources
- Plan: docs/plans/2026-02-13-feat-mvp-reviewer-score-serving-plan.md
