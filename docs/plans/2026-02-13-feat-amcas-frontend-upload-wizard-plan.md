---
title: "feat: AMCAS Frontend Upload Wizard & Integration"
type: feat
date: 2026-02-13
parent_plan: docs/plans/2026-02-13-feat-amcas-ingestion-ui-plan.md
phases: [5, 6]
---

# feat: AMCAS Frontend Upload Wizard & Integration

Implements **Phase 5** (Frontend Upload Wizard) and **Phase 6** (Integration & Polish) from the parent ingestion plan. All backend APIs (auth, ingest, pipeline) are already built and committed on `feat/amcas-ingestion-ui`.

## Overview

Build the complete frontend experience for AMCAS file ingestion: login, multi-file drag-and-drop upload, data preview with validation, pipeline progress monitoring, and integration polish (cycle-year filtering, sidebar updates). The backend is ready -- this is purely frontend work plus minor backend filter params.

## Existing Frontend Patterns

The codebase uses:
- **Next.js 16.1.6** with App Router, React 19, Tailwind CSS 4
- **`"use client"` pages** with `useEffect` + `useState` data fetching (no server components for data)
- **`fetchJSON<T>()`** helper in `frontend/lib/api.ts` for typed API calls
- **Custom components**: `Card`, `Badge`, `Sidebar` (all in `frontend/components/ui/`)
- **Rush brand colors**: `legacy-green`, `vitality-green`, `growth-green`, `sage`, `cerulean-blue`, `purple`, `rose`, `ivory`
- **Calibre font**, `@/lib/utils.ts` with `cn()` helper (clsx + tailwind-merge)
- **lucide-react** for icons

## Backend APIs Available

All endpoints require JWT cookie auth (`credentials: "include"`).

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /api/auth/login` | POST | Login (sets httpOnly cookie) |
| `POST /api/auth/logout` | POST | Logout (clears cookie) |
| `GET /api/auth/me` | GET | Current user info |
| `POST /api/ingest/upload` | POST | Upload xlsx files (multipart/form-data) |
| `GET /api/ingest/sessions` | GET | List past upload sessions |
| `GET /api/ingest/{id}/preview` | GET | Preview + auto-validate |
| `GET /api/ingest/{id}/validation` | GET | Get/run validation |
| `POST /api/ingest/{id}/approve` | POST | Approve & start pipeline |
| `POST /api/ingest/{id}/retry` | POST | Retry failed session |
| `PATCH /api/ingest/{id}/file-types` | PATCH | Override file type detection |
| `GET /api/pipeline/runs/{id}` | GET | Pipeline run status (for polling) |
| `GET /api/pipeline/runs` | GET | List pipeline runs |

## Implementation Phases

### Stage 5: Frontend Upload Wizard

#### 5.1 Shared Infrastructure

- [ ] Update `fetchJSON` in `frontend/lib/api.ts`
  - Add `credentials: "include"` to all requests (JWT cookies)
  - Detect `FormData` body and skip `Content-Type: application/json` header
  - Pass `signal` through for AbortController support
  - Add `X-Requested-With: XMLHttpRequest` header

```typescript
// frontend/lib/api.ts -- updated fetchJSON
async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      "X-Requested-With": "XMLHttpRequest",
      ...init?.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}
```

- [ ] Add ingestion types to `frontend/lib/types.ts`

```typescript
// Ingestion types (append to existing types.ts)
export interface UploadResponse {
  session_id: string;
  cycle_year: number;
  files_received: number;
  detected_types: Record<string, string>;
  status: string;
}

export interface ValidationIssue {
  severity: "error" | "warning" | "info";
  file_type: string | null;
  message: string;
  detail: string | null;
}

export interface ValidationResult {
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  info: string[];
}

export interface FilePreview {
  filename: string;
  detected_type: string | null;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_rows: Record<string, unknown>[];
}

export interface PreviewData {
  session_id: string;
  cycle_year: number;
  status: string;
  files: FilePreview[];
  validation: ValidationResult | null;
  total_applicants: number | null;
}

export interface SessionSummary {
  id: string;
  cycle_year: number;
  status: string;
  created_at: string;
  uploaded_by: string | null;
  applicant_count: number | null;
}

export interface PipelineRunResponse {
  run_id: string;
  status: string;
}

export interface PipelineRunStatus {
  id: string;
  upload_session_id: string;
  status: "pending" | "running" | "complete" | "failed";
  current_step: string | null;
  progress_pct: number;
  started_at: string | null;
  completed_at: string | null;
  result_summary: Record<string, unknown> | null;
  error_log: string | null;
}
```

- [ ] Add ingestion API functions to `frontend/lib/api.ts`

```typescript
// Ingestion API functions (append to existing api.ts)
export async function login(username: string, password: string): Promise<{ status: string; username: string }> {
  return fetchJSON("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function logout(): Promise<void> {
  await fetchJSON("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<{ id: string; username: string; role: string }> {
  return fetchJSON("/api/auth/me");
}

export async function uploadFiles(
  files: File[],
  cycleYear: number,
  signal?: AbortSignal,
): Promise<UploadResponse> {
  const form = new FormData();
  form.set("cycle_year", String(cycleYear));
  for (const f of files) form.append("files", f);
  return fetchJSON("/api/ingest/upload", { method: "POST", body: form, signal });
}

export async function getSessions(): Promise<SessionSummary[]> {
  return fetchJSON("/api/ingest/sessions");
}

export async function getPreview(sessionId: string): Promise<PreviewData> {
  return fetchJSON(`/api/ingest/${sessionId}/preview`);
}

export async function approveSession(sessionId: string): Promise<PipelineRunResponse> {
  return fetchJSON(`/api/ingest/${sessionId}/approve`, { method: "POST" });
}

export async function retrySession(sessionId: string): Promise<PipelineRunResponse> {
  return fetchJSON(`/api/ingest/${sessionId}/retry`, { method: "POST" });
}

export async function getPipelineRun(
  runId: string,
  signal?: AbortSignal,
): Promise<PipelineRunStatus> {
  return fetchJSON(`/api/pipeline/runs/${runId}`, { signal });
}

export async function updateFileTypes(
  sessionId: string,
  overrides: Record<string, string>,
): Promise<UploadResponse> {
  return fetchJSON(`/api/ingest/${sessionId}/file-types`, {
    method: "PATCH",
    body: JSON.stringify(overrides),
  });
}
```

#### 5.2 Login Page

- [ ] Create `frontend/app/login/page.tsx`
  - Username + password form
  - Error message display (red text, `role="alert"`)
  - Loading spinner on submit
  - Redirect to `/ingest` on success (or `returnTo` query param)
  - Redirect to `/ingest` if already logged in (`GET /api/auth/me` succeeds)

```typescript
// frontend/app/login/page.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { login, getMe } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const submitting = useRef(false);

  useEffect(() => {
    getMe()
      .then(() => router.replace(searchParams.get("returnTo") || "/ingest"))
      .catch(() => {}); // not logged in, show form
  }, [router, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError(null);
    try {
      await login(username, password);
      router.push(searchParams.get("returnTo") || "/ingest");
    } catch {
      setError("Invalid username or password");
      submitting.current = false;
    }
  };

  // ... render login form with Rush branding
}
```

#### 5.3 Upload Page

- [ ] Create `frontend/app/ingest/page.tsx`
  - **Cycle year selector**: dropdown defaulting to current year
  - **Drag-and-drop zone**: accepts `.xlsx` files, shows drop hover state
  - **File list**: each file shows name, size, detected type with manual override dropdown
  - **Required files checklist**: green check for detected, red X for missing (applicants, experiences)
  - **Upload button**: disabled until files selected, uses `useRef` guard against double-click
  - **Session history table**: past sessions with status badges below upload zone
  - **Active pipeline banner**: when a run is active, disable uploads and show banner
  - **Navigation warning**: `beforeunload` event listener during upload

Key patterns:
- `useRef` guard on upload button (not `useState` -- closure stale in same render cycle)
- AbortController for canceling in-flight upload on unmount
- `accept=".xlsx"` on file input, keyboard-accessible (Enter/Space opens picker)

```typescript
// Key state shape for upload page
const [files, setFiles] = useState<File[]>([]);
const [cycleYear, setCycleYear] = useState(new Date().getFullYear());
const [uploading, setUploading] = useState(false);
const [sessions, setSessions] = useState<SessionSummary[]>([]);
const uploadingRef = useRef(false);
const controllerRef = useRef<AbortController | null>(null);
```

- [ ] Create `frontend/app/ingest/layout.tsx` (optional -- auth check wrapper)
  - On mount, call `GET /api/auth/me`
  - If 401, redirect to `/login?returnTo=/ingest`

#### 5.4 Preview Page

- [ ] Create `frontend/app/ingest/[sessionId]/preview/page.tsx`
  - **File summary cards**: per-file card with filename, detected type, row count, column count
  - **Sample rows table**: expandable, first 10 rows per file (collapsible `<details>`)
  - **Validation panel**:
    - Errors (red border, blocks approval)
    - Warnings (amber border, can proceed with acknowledgment)
    - Info (gray, stats)
  - **"Approve & Run Pipeline" button**: disabled when errors exist, `useRef` double-click guard
  - **"Re-upload" button**: navigate back to `/ingest`
  - On mount, call `GET /api/ingest/{sessionId}/preview` (triggers auto-validation)

```typescript
// Approve button with useRef guard
const approving = useRef(false);
const handleApprove = () => {
  if (approving.current) return;
  approving.current = true;
  setApprovalState("approving");
  approveSession(sessionId)
    .then((res) => router.push(`/ingest/${sessionId}/status?run=${res.run_id}`))
    .catch((err) => {
      approving.current = false;
      setApprovalState("error");
      setError(err.message);
    });
};
```

#### 5.5 Status Page

- [ ] Create `frontend/app/ingest/[sessionId]/status/page.tsx`
  - **Pipeline step indicators**: 6 steps with icons (spinner/check/X)
    - Ingestion, LLM Scoring, Cleaning, Features, ML Scoring, Triage
  - **Progress bar**: `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
  - **Elapsed time display**: updates every second
  - **Polling**: recursive `setTimeout` (NOT `setInterval`) with `AbortController`
    - Poll every 3s during active steps, every 60s during LLM scoring phase
    - On visibility change: re-fetch immediately, clear pending timeout
    - Abort on unmount via cleanup function
  - **Completion**: success banner with tier distribution, "Go to Review Queue" link
  - **Failure**: user-friendly error message, "Retry" and "Re-upload" buttons with guidance text
    - Retry = same data (transient errors)
    - Re-upload = fix data issues
  - **Session expired handling**: show inline message (not redirect) since pipeline may have completed

```typescript
// Polling with recursive setTimeout + AbortController + visibility API
useEffect(() => {
  if (!runId) return;
  const controller = new AbortController();
  let nextTimeout: ReturnType<typeof setTimeout> | null = null;

  const poll = async () => {
    if (controller.signal.aborted) return;
    try {
      const run = await getPipelineRun(runId, controller.signal);
      if (controller.signal.aborted) return;
      setRun(run);
      if (run.status === "running" || run.status === "pending") {
        const delay = run.current_step === "llm_scoring" ? 60_000 : 3_000;
        nextTimeout = setTimeout(poll, delay);
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      if (controller.signal.aborted) return;
      setError(String(e));
    }
  };

  poll();

  const onVisibilityChange = () => {
    if (document.visibilityState === "visible" && !controller.signal.aborted) {
      if (nextTimeout !== null) clearTimeout(nextTimeout);
      poll();
    }
  };
  document.addEventListener("visibilitychange", onVisibilityChange);

  return () => {
    controller.abort();
    if (nextTimeout !== null) clearTimeout(nextTimeout);
    document.removeEventListener("visibilitychange", onVisibilityChange);
  };
}, [runId]);
```

#### 5.6 Sidebar Update

- [ ] Add "Ingest" nav item to `frontend/components/ui/sidebar.tsx`
  - Use `Upload` icon from lucide-react
  - Position before "Pipeline" in nav order
  - Active state matches `/ingest` and all sub-routes

```typescript
// Add to navItems array (before Pipeline)
{ href: "/ingest", label: "Ingest", icon: Upload },
```

### Stage 6: Integration & Polish

#### 6.1 Cycle Year Filtering (Backend)

- [ ] Add `cycle_year` query param to `GET /api/review/queue` in `api/routers/review.py`
  - Default to most recent cycle year
  - Filter applicants by `app_year` field
- [ ] Add `cycle_year` query param to `GET /api/applicants` in `api/routers/applicants.py`
  - Default to most recent cycle year

#### 6.2 Cycle Year Filtering (Frontend)

- [ ] Add cycle year dropdown to review page (`frontend/app/review/page.tsx`)
- [ ] Add cycle year dropdown to applicants page (`frontend/app/applicants/page.tsx`)
- [ ] Persist selected cycle year in URL query params

#### 6.3 Auth Guard for All Pages

- [ ] Add auth check to `frontend/app/layout.tsx`
  - Check `GET /api/auth/me` on mount
  - If 401 and not on `/login`, redirect to `/login?returnTo={pathname}`
  - Show loading state while checking auth
  - Exclude `/login` from auth check

#### 6.4 Logout Button

- [ ] Add logout button to sidebar
  - Below nav items, at bottom of sidebar
  - Shows current username
  - Calls `POST /api/auth/logout`, then redirects to `/login`

## Files Created/Modified

| File | Action | Stage |
|------|--------|-------|
| `frontend/lib/api.ts` | Modify -- update fetchJSON, add ingestion + auth API functions | 5.1 |
| `frontend/lib/types.ts` | Modify -- add ingestion types | 5.1 |
| `frontend/app/login/page.tsx` | Create | 5.2 |
| `frontend/app/ingest/page.tsx` | Create | 5.3 |
| `frontend/app/ingest/layout.tsx` | Create (optional auth wrapper) | 5.3 |
| `frontend/app/ingest/[sessionId]/preview/page.tsx` | Create | 5.4 |
| `frontend/app/ingest/[sessionId]/status/page.tsx` | Create | 5.5 |
| `frontend/components/ui/sidebar.tsx` | Modify -- add Ingest nav + logout | 5.6, 6.4 |
| `frontend/app/layout.tsx` | Modify -- add auth guard | 6.3 |
| `api/routers/review.py` | Modify -- add cycle_year param | 6.1 |
| `api/routers/applicants.py` | Modify -- add cycle_year param | 6.1 |

## Success Criteria

- [ ] Staff can log in at `/login` and get redirected to `/ingest`
- [ ] Unauthenticated users get redirected to `/login`
- [ ] Staff can drag-and-drop xlsx files, see detected types, override if needed
- [ ] Upload button disabled during upload, `beforeunload` warning active
- [ ] Preview page shows validation errors (red), warnings (amber), info (gray)
- [ ] Approve button disabled when errors exist
- [ ] Status page shows real-time progress with step indicators (polling every 3s)
- [ ] On completion: success banner with tier distribution, link to review queue
- [ ] On failure: user-friendly error with clear retry vs re-upload guidance
- [ ] Session history shows past uploads with status badges
- [ ] Sidebar shows "Ingest" nav item with active state
- [ ] Review queue and applicants page support cycle_year filtering
- [ ] No TypeScript errors (`strict: true`, no `any` types)
- [ ] All existing tests still pass

## Key Implementation Patterns

1. **Double-click prevention**: `useRef` (not `useState`) on Approve, Retry, Upload buttons
2. **Polling**: Recursive `setTimeout` + `AbortController` + visibility API (not `setInterval`)
3. **Upload progress**: AbortController for cancel on unmount
4. **Auth flow**: `GET /api/auth/me` check, inline 401 handling in polling (not redirect)
5. **fetchJSON**: `credentials: "include"`, FormData detection, signal passthrough
6. **Rush brand**: Use existing CSS vars (`legacy-green`, `vitality-green`, `sage`, `rose`, `ivory`)
7. **Accessibility**: `role="progressbar"` with aria attributes, `role="alert"` on errors, keyboard-accessible upload zone
