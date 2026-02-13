# AMCAS File Ingestion Wizard - Frontend Architecture Specification

**Target Users:** Non-technical admissions office staff at medical schools
**Tech Stack:** Next.js 16 (App Router), React 19, Tailwind 4, TypeScript
**Design Philosophy:** Clear feedback, progressive disclosure, error prevention over error handling

---

## Table of Contents

1. [Shared Infrastructure](#shared-infrastructure)
2. [Page 1: Login](#page-1-login)
3. [Page 2: Upload](#page-2-upload)
4. [Page 3: Preview](#page-3-preview)
5. [Page 4: Status](#page-4-status)
6. [API Contracts](#api-contracts)
7. [Accessibility Checklist](#accessibility-checklist)

---

## Shared Infrastructure

### 1. Auth Context Provider

**File:** `/frontend/lib/auth-context.tsx`

```typescript
"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";

interface User {
  username: string;
  role: string; // 'admin' | 'staff'
  session_id: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const checkAuth = async () => {
    try {
      const res = await fetch("/api/auth/me", { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.message || "Invalid credentials");
    }

    const data = await res.json();
    setUser(data.user);

    // Redirect to returnTo URL or default to /ingest
    const returnTo = searchParams.get("returnTo") || "/ingest";
    router.push(returnTo);
  };

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
    router.push("/login");
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Redirect unauthenticated users to login (except on /login page)
  useEffect(() => {
    if (!isLoading && !user && pathname !== "/login") {
      router.push(`/login?returnTo=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, user, pathname, router]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

**Props:** None (provider)
**State:**
- `user: User | null` - Current authenticated user
- `isLoading: boolean` - Auth check in progress

**Accessibility:**
- Automatic redirect preserves user intent via returnTo param
- Loading state prevents flash of wrong content

**Edge Cases:**
- Session expiry during polling: handled per-component (inline message, not redirect)
- Multiple tabs: relies on cookie sync from backend
- Network failure during checkAuth: treats as unauthenticated

---

### 2. usePolling Hook

**File:** `/frontend/lib/hooks/use-polling.ts`

```typescript
import { useEffect, useRef, useCallback } from "react";

interface UsePollingOptions<T> {
  fn: () => Promise<T>;
  interval: number; // milliseconds
  enabled: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  shouldStop?: (data: T) => boolean; // Return true to stop polling
}

export function usePolling<T>({
  fn,
  interval,
  enabled,
  onSuccess,
  onError,
  shouldStop,
}: UsePollingOptions<T>) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isPollingRef = useRef(false);

  const poll = useCallback(async () => {
    if (!enabled || isPollingRef.current) return;

    isPollingRef.current = true;
    abortControllerRef.current = new AbortController();

    try {
      const data = await fn();

      if (shouldStop && shouldStop(data)) {
        isPollingRef.current = false;
        onSuccess?.(data);
        return;
      }

      onSuccess?.(data);

      // Schedule next poll with recursive setTimeout
      timeoutRef.current = setTimeout(() => {
        isPollingRef.current = false;
        poll();
      }, interval);
    } catch (error) {
      isPollingRef.current = false;
      onError?.(error as Error);

      // Continue polling on error (unless disabled)
      if (enabled) {
        timeoutRef.current = setTimeout(() => {
          poll();
        }, interval);
      }
    }
  }, [fn, interval, enabled, onSuccess, onError, shouldStop]);

  // Start polling when enabled
  useEffect(() => {
    if (enabled) {
      poll();
    }

    return () => {
      isPollingRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [enabled, poll]);

  // Pause polling when tab is hidden (Page Visibility API)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Tab hidden: clear timeout but don't stop polling flag
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      } else {
        // Tab visible: resume polling if enabled and not already polling
        if (enabled && !isPollingRef.current) {
          poll();
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [enabled, poll]);

  const stopPolling = useCallback(() => {
    isPollingRef.current = false;
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  }, []);

  return { stopPolling };
}
```

**Features:**
- Recursive setTimeout (more reliable than setInterval)
- AbortController for in-flight request cleanup
- Page Visibility API integration (pause when tab hidden)
- Automatic stop via shouldStop predicate
- Error handling with retry

**Edge Cases:**
- Tab switches during polling: pauses and resumes automatically
- Network errors: continues polling with same interval
- Component unmount: cleans up timeout and aborts in-flight requests

---

### 3. useMutationGuard Hook

**File:** `/frontend/lib/hooks/use-mutation-guard.ts`

```typescript
import { useRef } from "react";

/**
 * Prevents double-click and concurrent mutations.
 * Returns a wrapper function that guards the async operation.
 */
export function useMutationGuard() {
  const isExecutingRef = useRef(false);

  const guard = <T extends any[], R>(
    fn: (...args: T) => Promise<R>
  ): ((...args: T) => Promise<R | null>) => {
    return async (...args: T): Promise<R | null> => {
      if (isExecutingRef.current) {
        console.warn("Mutation already in progress, ignoring duplicate call");
        return null;
      }

      isExecutingRef.current = true;
      try {
        const result = await fn(...args);
        return result;
      } finally {
        isExecutingRef.current = false;
      }
    };
  };

  return { guard };
}
```

**Usage Example:**
```typescript
const { guard } = useMutationGuard();
const handleSubmit = guard(async () => {
  await api.submitForm(data);
});
```

---

### 4. useAbortController Hook

**File:** `/frontend/lib/hooks/use-abort-controller.ts`

```typescript
import { useEffect, useRef } from "react";

/**
 * Creates an AbortController that is automatically aborted on unmount.
 * Useful for cleanup of in-flight fetch requests.
 */
export function useAbortController() {
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    abortControllerRef.current = new AbortController();

    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  return abortControllerRef.current;
}
```

---

### 5. Shared Type Definitions

**File:** `/frontend/lib/types-ingestion.ts`

```typescript
// File type detection and metadata
export type AmcasFileType =
  | "biographic"
  | "experiences"
  | "coursework"
  | "grades"
  | "mcat"
  | "letters"
  | "supplemental"
  | "unknown";

export interface FileMetadata {
  file_id: string; // UUID
  filename: string;
  size_bytes: number;
  detected_type: AmcasFileType;
  manual_override_type: AmcasFileType | null;
  upload_progress: number; // 0-100
  upload_status: "pending" | "uploading" | "complete" | "failed";
  upload_error?: string;
}

// Ingestion session
export interface IngestionSession {
  session_id: string;
  cycle_year: number;
  created_at: string; // ISO timestamp
  status: "uploading" | "validating" | "approved" | "running" | "complete" | "failed";
  files: FileMetadata[];
  applicant_count: number | null;
  validation_results?: ValidationResults;
  pipeline_status?: PipelineStatus;
}

// Validation
export interface ValidationIssue {
  level: "error" | "warning" | "info";
  file_type: AmcasFileType;
  message: string;
  details?: string;
  affected_rows?: number;
}

export interface ValidationResults {
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  info: ValidationIssue[];
  file_summaries: FileSummary[];
}

export interface FileSummary {
  file_type: AmcasFileType;
  row_count: number;
  column_count: number;
  sample_rows: Record<string, any>[]; // First 10 rows
}

// Pipeline execution
export type PipelineStep = "ingestion" | "cleaning" | "features" | "scoring" | "triage";

export interface PipelineStepStatus {
  step: PipelineStep;
  status: "pending" | "running" | "complete" | "failed";
  started_at: string | null; // ISO timestamp
  completed_at: string | null; // ISO timestamp
  elapsed_seconds: number | null;
  error_message?: string;
}

export interface PipelineStatus {
  session_id: string;
  overall_status: "running" | "complete" | "failed";
  overall_progress: number; // 0-100
  started_at: string;
  completed_at: string | null;
  elapsed_seconds: number;
  steps: PipelineStepStatus[];
  tier_distribution?: Record<number, number>; // Only present on complete
  error_summary?: string; // User-friendly error message
}

// Required file checklist
export const REQUIRED_FILE_TYPES: AmcasFileType[] = [
  "biographic",
  "experiences",
  "coursework",
  "mcat",
];

export const FILE_TYPE_LABELS: Record<AmcasFileType, string> = {
  biographic: "Biographic Data",
  experiences: "Experiences",
  coursework: "Coursework",
  grades: "Grades",
  mcat: "MCAT Scores",
  letters: "Letters of Recommendation",
  supplemental: "Supplemental",
  unknown: "Unknown File Type",
};
```

---

## Page 1: Login

**Route:** `/frontend/app/login/page.tsx`
**Purpose:** Simple username/password authentication with error handling
**Layout:** Centered card on full-screen background

### Component Tree

```
LoginPage (Server Component)
└── LoginForm (Client Component)
    ├── Card
    │   ├── CardHeader
    │   │   └── CardTitle
    │   └── CardContent
    │       ├── FormField (username)
    │       ├── FormField (password)
    │       ├── ErrorMessage (conditional)
    │       └── SubmitButton
```

### LoginPage Component

**File:** `/frontend/app/login/page.tsx`

```typescript
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-sage px-4">
      <div className="w-full max-w-md">
        <LoginForm />
      </div>
    </div>
  );
}
```

**Styling:**
- Full viewport height: `min-h-screen`
- Centered: `flex items-center justify-center`
- Background: `bg-sage` (light green from brand palette)
- Max width: `max-w-md` (28rem / 448px)
- Padding: `px-4` for mobile margins

---

### LoginForm Component

**File:** `/frontend/components/auth/login-form.tsx`

```typescript
"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function LoginForm() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(username, password);
      // Redirect handled by AuthContext
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sign In</CardTitle>
        <p className="text-sm text-raw-umber mt-1">
          Enter your credentials to access the AMCAS ingestion system.
        </p>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username Field */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-raw-umber mb-1"
            >
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              disabled={isLoading}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={cn(
                "w-full px-3 py-2 border rounded-md transition-colors",
                "border-gray focus:border-growth-green focus:outline-none focus:ring-2 focus:ring-growth-green/20",
                "disabled:bg-gray disabled:cursor-not-allowed"
              )}
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? "login-error" : undefined}
            />
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-raw-umber mb-1"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              disabled={isLoading}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={cn(
                "w-full px-3 py-2 border rounded-md transition-colors",
                "border-gray focus:border-growth-green focus:outline-none focus:ring-2 focus:ring-growth-green/20",
                "disabled:bg-gray disabled:cursor-not-allowed"
              )}
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? "login-error" : undefined}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div
              id="login-error"
              role="alert"
              className="flex items-start gap-2 p-3 bg-rose/10 border border-rose/30 rounded-md"
            >
              <svg
                className="w-5 h-5 text-rose flex-shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm text-rose">{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={cn(
              "w-full px-4 py-2 font-medium text-white rounded-md transition-all",
              "bg-growth-green hover:bg-legacy-green",
              "focus:outline-none focus:ring-2 focus:ring-growth-green focus:ring-offset-2",
              "disabled:bg-wash-gray disabled:cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Signing in...
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>
      </CardContent>
    </Card>
  );
}
```

**Props:** None

**State:**
- `username: string` - Input value
- `password: string` - Input value
- `error: string | null` - Error message from failed login
- `isLoading: boolean` - Submit in progress

**Interactions:**
- Form submit: calls `login()` from AuthContext
- Inputs disabled during loading
- Error clears on new submit attempt

**Accessibility:**
- Semantic form with labels
- `aria-invalid` on inputs when error present
- `aria-describedby` links inputs to error message
- `role="alert"` on error message for screen reader announcement
- Icon has `aria-hidden="true"`
- Loading spinner hidden from screen readers

**Edge Cases:**
- Network timeout: shows generic error after fetch timeout
- Invalid credentials: displays backend error message
- Already authenticated: AuthContext redirects away
- Empty fields: browser validation via `required` attribute

**Color Usage:**
- Background: `bg-sage` (light green, calming)
- Primary action: `bg-growth-green` (brand green)
- Error: `bg-rose/10` background with `text-rose` and `border-rose/30`
- Text: `text-raw-umber` (dark brown, readable)
- Disabled: `bg-wash-gray`

---

## Page 2: Upload

**Route:** `/frontend/app/ingest/page.tsx`
**Purpose:** Upload AMCAS Excel files, auto-detect types, validate completeness
**Layout:** Header with cycle selector, drag-drop zone, session history table

### Component Tree

```
UploadPage (Client Component)
├── PageHeader
│   ├── Title
│   └── CycleYearSelector
├── PipelineRunningBanner (conditional)
├── UploadZone
│   ├── DropZone
│   │   ├── DropZoneIdle
│   │   ├── DropZoneActive (hover)
│   │   └── DropZoneUploading
│   ├── FileList
│   │   └── FileListItem[] (per file)
│   │       ├── FileIcon
│   │       ├── FileInfo (name, size)
│   │       ├── FileTypeSelector
│   │       ├── ProgressBar (uploading)
│   │       └── RemoveButton
│   ├── RequiredFilesChecklist
│   │   └── ChecklistItem[] (per required type)
│   └── UploadButton
└── SessionHistoryTable
    └── SessionRow[] (per session)
        ├── DateCell
        ├── CycleYearCell
        ├── StatusBadge
        ├── ApplicantCountCell
        └── ActionsCell
```

### UploadPage Component

**File:** `/frontend/app/ingest/page.tsx`

```typescript
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CycleYearSelector } from "@/components/ingest/cycle-year-selector";
import { UploadZone } from "@/components/ingest/upload-zone";
import { SessionHistoryTable } from "@/components/ingest/session-history-table";
import { PipelineRunningBanner } from "@/components/ingest/pipeline-running-banner";
import { useAuth } from "@/lib/auth-context";
import { IngestionSession } from "@/lib/types-ingestion";

export default function UploadPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [cycleYear, setCycleYear] = useState(new Date().getFullYear());
  const [sessions, setSessions] = useState<IngestionSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [pipelineRunning, setPipelineRunning] = useState(false);

  // Fetch session history
  useEffect(() => {
    const fetchSessions = async () => {
      setIsLoadingSessions(true);
      try {
        const res = await fetch("/api/ingest/sessions", { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          setSessions(data.sessions);

          // Check if any pipeline is currently running
          const hasRunning = data.sessions.some(
            (s: IngestionSession) => s.status === "running"
          );
          setPipelineRunning(hasRunning);
        }
      } catch (error) {
        console.error("Failed to fetch sessions:", error);
      } finally {
        setIsLoadingSessions(false);
      }
    };

    fetchSessions();
  }, []);

  const handleUploadComplete = (sessionId: string) => {
    router.push(`/ingest/${sessionId}/preview`);
  };

  const handleSessionRefresh = () => {
    // Re-fetch sessions when pipeline status changes
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-ivory p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-raw-umber">AMCAS File Upload</h1>
            <p className="text-sm text-wash-gray mt-1">
              Upload Excel files exported from AMCAS for processing.
            </p>
          </div>
          <CycleYearSelector value={cycleYear} onChange={setCycleYear} />
        </div>

        {/* Pipeline Running Banner */}
        {pipelineRunning && <PipelineRunningBanner />}

        {/* Upload Zone */}
        <UploadZone
          cycleYear={cycleYear}
          disabled={pipelineRunning}
          onUploadComplete={handleUploadComplete}
        />

        {/* Session History */}
        <Card>
          <CardHeader>
            <CardTitle>Upload History</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingSessions ? (
              <div className="flex items-center justify-center py-8 text-wash-gray">
                <svg
                  className="animate-spin h-6 w-6 mr-2"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Loading upload history...
              </div>
            ) : (
              <SessionHistoryTable sessions={sessions} onRefresh={handleSessionRefresh} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**Props:** None (page component)

**State:**
- `cycleYear: number` - Selected cycle year
- `sessions: IngestionSession[]` - Upload history
- `isLoadingSessions: boolean` - Loading state for history
- `pipelineRunning: boolean` - Any pipeline currently running

**Accessibility:**
- Semantic heading hierarchy (h1 for page title)
- Loading spinner with descriptive text
- Disabled state clearly communicated

---

### CycleYearSelector Component

**File:** `/frontend/components/ingest/cycle-year-selector.tsx`

```typescript
"use client";

interface CycleYearSelectorProps {
  value: number;
  onChange: (year: number) => void;
}

export function CycleYearSelector({ value, onChange }: CycleYearSelectorProps) {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="cycle-year" className="text-sm font-medium text-raw-umber">
        Cycle Year:
      </label>
      <select
        id="cycle-year"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="px-3 py-2 border border-gray rounded-md bg-white focus:border-growth-green focus:outline-none focus:ring-2 focus:ring-growth-green/20"
      >
        {years.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
    </div>
  );
}
```

**Props:**
- `value: number` - Current selected year
- `onChange: (year: number) => void` - Year change handler

**Accessibility:**
- Label associated with select via `htmlFor`
- Semantic select element

---

### PipelineRunningBanner Component

**File:** `/frontend/components/ingest/pipeline-running-banner.tsx`

```typescript
"use client";

export function PipelineRunningBanner() {
  return (
    <div
      role="status"
      className="flex items-start gap-3 p-4 bg-cerulean-blue/10 border border-cerulean-blue/30 rounded-md"
    >
      <svg
        className="w-5 h-5 text-cerulean-blue flex-shrink-0 mt-0.5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <div className="flex-1">
        <p className="font-medium text-cerulean-blue">Pipeline Currently Running</p>
        <p className="text-sm text-raw-umber mt-1">
          A processing pipeline is currently running. New uploads are temporarily disabled.
          You can monitor progress on the Status page.
        </p>
      </div>
    </div>
  );
}
```

**Props:** None

**Accessibility:**
- `role="status"` for screen reader announcement
- Clear informational text

---

### UploadZone Component

**File:** `/frontend/components/ingest/upload-zone.tsx`

```typescript
"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { FileList } from "./file-list";
import { RequiredFilesChecklist } from "./required-files-checklist";
import { cn } from "@/lib/utils";
import { FileMetadata, AmcasFileType, REQUIRED_FILE_TYPES } from "@/lib/types-ingestion";

interface UploadZoneProps {
  cycleYear: number;
  disabled: boolean;
  onUploadComplete: (sessionId: string) => void;
}

export function UploadZone({ cycleYear, disabled, onUploadComplete }: UploadZoneProps) {
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if all required file types are present
  const hasAllRequiredFiles = REQUIRED_FILE_TYPES.every((type) =>
    files.some((f) => (f.manual_override_type || f.detected_type) === type)
  );

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (f) => f.name.endsWith(".xlsx") || f.name.endsWith(".xls")
    );

    addFiles(droppedFiles);
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = async (newFiles: File[]) => {
    const fileMetadataList: FileMetadata[] = await Promise.all(
      newFiles.map(async (file) => {
        // Auto-detect file type based on filename patterns
        const detectedType = detectFileType(file.name);

        return {
          file_id: crypto.randomUUID(),
          filename: file.name,
          size_bytes: file.size,
          detected_type: detectedType,
          manual_override_type: null,
          upload_progress: 0,
          upload_status: "pending" as const,
        };
      })
    );

    setFiles((prev) => [...prev, ...fileMetadataList]);
  };

  const detectFileType = (filename: string): AmcasFileType => {
    const lower = filename.toLowerCase();
    if (lower.includes("biographic")) return "biographic";
    if (lower.includes("experience")) return "experiences";
    if (lower.includes("coursework") || lower.includes("course")) return "coursework";
    if (lower.includes("grade")) return "grades";
    if (lower.includes("mcat")) return "mcat";
    if (lower.includes("letter") || lower.includes("lor")) return "letters";
    if (lower.includes("supplemental") || lower.includes("supplement")) return "supplemental";
    return "unknown";
  };

  const handleFileTypeChange = (fileId: string, newType: AmcasFileType) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.file_id === fileId ? { ...f, manual_override_type: newType } : f
      )
    );
  };

  const handleFileRemove = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.file_id !== fileId));
  };

  const handleUpload = async () => {
    if (files.length === 0 || !hasAllRequiredFiles) return;

    setIsUploading(true);

    try {
      // Create session
      const sessionRes = await fetch("/api/ingest/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ cycle_year: cycleYear }),
      });

      if (!sessionRes.ok) {
        throw new Error("Failed to create session");
      }

      const { session_id } = await sessionRes.json();

      // Upload each file with XHR for progress tracking
      for (const fileMeta of files) {
        await uploadFileWithProgress(session_id, fileMeta);
      }

      // Trigger validation
      await fetch(`/api/ingest/sessions/${session_id}/validate`, {
        method: "POST",
        credentials: "include",
      });

      onUploadComplete(session_id);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const uploadFileWithProgress = (sessionId: string, fileMeta: FileMetadata): Promise<void> => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Progress handler
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setFiles((prev) =>
            prev.map((f) =>
              f.file_id === fileMeta.file_id
                ? { ...f, upload_progress: progress, upload_status: "uploading" as const }
                : f
            )
          );
        }
      });

      // Completion handler
      xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
          setFiles((prev) =>
            prev.map((f) =>
              f.file_id === fileMeta.file_id
                ? { ...f, upload_status: "complete" as const }
                : f
            )
          );
          resolve();
        } else {
          setFiles((prev) =>
            prev.map((f) =>
              f.file_id === fileMeta.file_id
                ? { ...f, upload_status: "failed" as const, upload_error: "Upload failed" }
                : f
            )
          );
          reject(new Error("Upload failed"));
        }
      });

      // Error handler
      xhr.addEventListener("error", () => {
        setFiles((prev) =>
          prev.map((f) =>
            f.file_id === fileMeta.file_id
              ? { ...f, upload_status: "failed" as const, upload_error: "Network error" }
              : f
          )
        );
        reject(new Error("Network error"));
      });

      // Prepare FormData
      const formData = new FormData();
      const fileInput = document.querySelector<HTMLInputElement>(`input[data-file-id="${fileMeta.file_id}"]`);
      if (fileInput?.files?.[0]) {
        formData.append("file", fileInput.files[0]);
        formData.append("file_type", fileMeta.manual_override_type || fileMeta.detected_type);
      }

      // Send request
      xhr.open("POST", `/api/ingest/sessions/${sessionId}/upload`);
      xhr.send(formData);
    });
  };

  // beforeunload warning during upload
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isUploading) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [isUploading]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Files</CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Drop Zone */}
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          className={cn(
            "relative border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer",
            isDragging && !disabled
              ? "border-growth-green bg-sage"
              : "border-gray hover:border-wash-gray",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-label="Upload AMCAS Excel files"
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            multiple
            onChange={handleFileInputChange}
            disabled={disabled}
            className="hidden"
            aria-hidden="true"
          />

          <svg
            className="mx-auto h-12 w-12 text-wash-gray"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <p className="mt-2 text-sm font-medium text-raw-umber">
            {isDragging ? "Drop files here" : "Drag and drop Excel files here"}
          </p>
          <p className="mt-1 text-xs text-wash-gray">or click to browse</p>
          <p className="mt-1 text-xs text-wash-gray">.xlsx or .xls files only</p>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <FileList
            files={files}
            onTypeChange={handleFileTypeChange}
            onRemove={handleFileRemove}
            disabled={isUploading}
          />
        )}

        {/* Required Files Checklist */}
        <RequiredFilesChecklist files={files} />

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={disabled || files.length === 0 || !hasAllRequiredFiles || isUploading}
          className={cn(
            "w-full px-4 py-3 font-medium text-white rounded-md transition-all",
            "bg-growth-green hover:bg-legacy-green",
            "focus:outline-none focus:ring-2 focus:ring-growth-green focus:ring-offset-2",
            "disabled:bg-wash-gray disabled:cursor-not-allowed"
          )}
        >
          {isUploading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Uploading...
            </span>
          ) : (
            "Upload & Validate"
          )}
        </button>
      </CardContent>
    </Card>
  );
}
```

**Props:**
- `cycleYear: number` - Selected cycle year for upload
- `disabled: boolean` - Disable upload when pipeline running
- `onUploadComplete: (sessionId: string) => void` - Callback after successful upload

**State:**
- `files: FileMetadata[]` - List of selected files
- `isDragging: boolean` - Drag-over state
- `isUploading: boolean` - Upload in progress

**Interactions:**
- Drag and drop: visual feedback with border/background change
- Click to browse: opens file picker
- Keyboard: Enter/Space on drop zone opens file picker
- File type override: dropdown per file
- Remove file: X button per file
- Upload button: disabled until all required files present

**Accessibility:**
- `role="button"` on drop zone
- `tabIndex={0}` for keyboard navigation
- `aria-label` describes drop zone purpose
- Keyboard handler for Enter/Space
- Hidden file input (`aria-hidden="true"`)
- beforeunload warning prevents accidental navigation during upload

**Edge Cases:**
- Non-Excel files dropped: filtered out
- Duplicate filenames: allowed (backend uses UUID)
- Upload failure: shows error per file, allows retry
- Missing required files: button disabled with checklist showing gaps

**Color Usage:**
- Active drag: `border-growth-green bg-sage`
- Default: `border-gray`
- Success: `bg-growth-green`
- Disabled: `bg-wash-gray`

---

### FileList Component

**File:** `/frontend/components/ingest/file-list.tsx`

```typescript
"use client";

import { FileMetadata, AmcasFileType, FILE_TYPE_LABELS } from "@/lib/types-ingestion";
import { cn } from "@/lib/utils";

interface FileListProps {
  files: FileMetadata[];
  onTypeChange: (fileId: string, newType: AmcasFileType) => void;
  onRemove: (fileId: string) => void;
  disabled: boolean;
}

export function FileList({ files, onTypeChange, onRemove, disabled }: FileListProps) {
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-raw-umber">Selected Files</h4>
      <div className="space-y-2">
        {files.map((file) => (
          <div
            key={file.file_id}
            className="flex items-center gap-3 p-3 border border-gray rounded-md bg-white"
          >
            {/* File Icon */}
            <svg
              className="w-8 h-8 text-growth-green flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-raw-umber truncate">
                {file.filename}
              </p>
              <p className="text-xs text-wash-gray">{formatBytes(file.size_bytes)}</p>

              {/* Progress Bar (uploading) */}
              {file.upload_status === "uploading" && (
                <div className="mt-2 w-full bg-gray rounded-full h-1.5">
                  <div
                    className="bg-growth-green h-1.5 rounded-full transition-all"
                    style={{ width: `${file.upload_progress}%` }}
                    role="progressbar"
                    aria-valuenow={file.upload_progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Upload progress: ${file.upload_progress}%`}
                  />
                </div>
              )}

              {/* Error Message */}
              {file.upload_status === "failed" && (
                <p className="mt-1 text-xs text-rose" role="alert">
                  {file.upload_error || "Upload failed"}
                </p>
              )}
            </div>

            {/* File Type Selector */}
            <select
              value={file.manual_override_type || file.detected_type}
              onChange={(e) => onTypeChange(file.file_id, e.target.value as AmcasFileType)}
              disabled={disabled || file.upload_status === "uploading"}
              className={cn(
                "px-2 py-1 text-sm border border-gray rounded-md",
                "focus:border-growth-green focus:outline-none focus:ring-1 focus:ring-growth-green",
                "disabled:bg-gray disabled:cursor-not-allowed"
              )}
              aria-label={`File type for ${file.filename}`}
            >
              {Object.entries(FILE_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>

            {/* Remove Button */}
            <button
              onClick={() => onRemove(file.file_id)}
              disabled={disabled || file.upload_status === "uploading"}
              className={cn(
                "p-1 text-wash-gray hover:text-rose transition-colors",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
              aria-label={`Remove ${file.filename}`}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Props:**
- `files: FileMetadata[]` - List of files
- `onTypeChange: (fileId: string, newType: AmcasFileType) => void` - Type override handler
- `onRemove: (fileId: string) => void` - Remove file handler
- `disabled: boolean` - Disable interactions during upload

**Interactions:**
- Type selector: dropdown per file
- Remove button: X icon, disabled during upload
- Progress bar: animates during upload

**Accessibility:**
- Progress bar with `role="progressbar"` and ARIA attributes
- `aria-label` on type selector and remove button
- Error message with `role="alert"`
- Truncate long filenames with ellipsis

---

### RequiredFilesChecklist Component

**File:** `/frontend/components/ingest/required-files-checklist.tsx`

```typescript
"use client";

import { FileMetadata, REQUIRED_FILE_TYPES, FILE_TYPE_LABELS } from "@/lib/types-ingestion";

interface RequiredFilesChecklistProps {
  files: FileMetadata[];
}

export function RequiredFilesChecklist({ files }: RequiredFilesChecklistProps) {
  const checkType = (type: string) => {
    return files.some((f) => (f.manual_override_type || f.detected_type) === type);
  };

  return (
    <div className="p-4 bg-sage/30 border border-sage rounded-md">
      <h4 className="text-sm font-medium text-raw-umber mb-2">Required Files</h4>
      <div className="space-y-1">
        {REQUIRED_FILE_TYPES.map((type) => {
          const isPresent = checkType(type);
          return (
            <div key={type} className="flex items-center gap-2">
              {isPresent ? (
                <svg
                  className="w-5 h-5 text-growth-green"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 text-rose"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              )}
              <span
                className={
                  isPresent ? "text-sm text-raw-umber" : "text-sm text-wash-gray"
                }
              >
                {FILE_TYPE_LABELS[type]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

**Props:**
- `files: FileMetadata[]` - Current file list

**Accessibility:**
- Icons have `aria-hidden="true"`
- Visual state (green check vs red X) supplemented by color contrast
- Text color changes for missing items (gray)

---

### SessionHistoryTable Component

**File:** `/frontend/components/ingest/session-history-table.tsx`

```typescript
"use client";

import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { IngestionSession } from "@/lib/types-ingestion";

interface SessionHistoryTableProps {
  sessions: IngestionSession[];
  onRefresh: () => void;
}

export function SessionHistoryTable({ sessions, onRefresh }: SessionHistoryTableProps) {
  const router = useRouter();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete":
        return "#00A66C"; // growth-green
      case "failed":
        return "#E63946"; // rose
      case "running":
        return "#54ADD3"; // cerulean-blue
      default:
        return "#A59F9F"; // wash-gray
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "uploading":
        return "Uploading";
      case "validating":
        return "Validating";
      case "approved":
        return "Approved";
      case "running":
        return "Running";
      case "complete":
        return "Complete";
      case "failed":
        return "Failed";
      default:
        return status;
    }
  };

  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).format(date);
  };

  const handleViewPreview = (sessionId: string) => {
    router.push(`/ingest/${sessionId}/preview`);
  };

  const handleViewStatus = (sessionId: string) => {
    router.push(`/ingest/${sessionId}/status`);
  };

  if (sessions.length === 0) {
    return (
      <p className="text-sm text-wash-gray text-center py-8">
        No upload history yet. Upload your first batch above.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="border-b border-gray">
          <tr>
            <th className="text-left py-3 px-4 font-medium text-raw-umber">Date</th>
            <th className="text-left py-3 px-4 font-medium text-raw-umber">Cycle Year</th>
            <th className="text-left py-3 px-4 font-medium text-raw-umber">Status</th>
            <th className="text-left py-3 px-4 font-medium text-raw-umber">Applicants</th>
            <th className="text-left py-3 px-4 font-medium text-raw-umber">Actions</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((session) => (
            <tr key={session.session_id} className="border-b border-gray hover:bg-sage/10">
              <td className="py-3 px-4 text-raw-umber">
                {formatDate(session.created_at)}
              </td>
              <td className="py-3 px-4 text-raw-umber">{session.cycle_year}</td>
              <td className="py-3 px-4">
                <Badge color={getStatusColor(session.status)}>
                  {getStatusLabel(session.status)}
                </Badge>
              </td>
              <td className="py-3 px-4 text-raw-umber">
                {session.applicant_count !== null ? session.applicant_count : "-"}
              </td>
              <td className="py-3 px-4">
                <div className="flex gap-2">
                  {(session.status === "validating" || session.status === "approved") && (
                    <button
                      onClick={() => handleViewPreview(session.session_id)}
                      className="text-growth-green hover:underline"
                    >
                      View Preview
                    </button>
                  )}
                  {(session.status === "running" || session.status === "complete" || session.status === "failed") && (
                    <button
                      onClick={() => handleViewStatus(session.session_id)}
                      className="text-growth-green hover:underline"
                    >
                      View Status
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Props:**
- `sessions: IngestionSession[]` - Session history
- `onRefresh: () => void` - Refresh callback (not currently used, for future polling)

**Interactions:**
- Row hover: subtle background change
- Action buttons: navigate to preview or status page based on session state

**Accessibility:**
- Semantic table with thead/tbody
- Clear column headers
- Link text describes action

---

## Page 3: Preview

**Route:** `/frontend/app/ingest/[sessionId]/preview/page.tsx`
**Purpose:** Show validation results, file summaries, approve/reject upload
**Layout:** File summary cards, validation panel, approve button

### Component Tree

```
PreviewPage (Client Component)
├── PageHeader
│   └── BackLink
├── FileSummaryGrid
│   └── FileSummaryCard[] (per file)
│       ├── FileTypeBadge
│       ├── MetadataRow (rows, columns)
│       ├── ExpandButton
│       └── SampleDataTable (expandable)
├── ValidationPanel
│   ├── ErrorList (conditional)
│   │   └── ValidationIssueItem[]
│   ├── WarningList (conditional)
│   │   └── ValidationIssueItem[]
│   └── InfoList (conditional)
│       └── ValidationIssueItem[]
└── ActionBar
    ├── ReUploadLink
    └── ApproveButton
        └── ConfirmationDialog (conditional)
```

### PreviewPage Component

**File:** `/frontend/app/ingest/[sessionId]/preview/page.tsx`

```typescript
"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { FileSummaryGrid } from "@/components/ingest/file-summary-grid";
import { ValidationPanel } from "@/components/ingest/validation-panel";
import { ApproveButton } from "@/components/ingest/approve-button";
import { IngestionSession, ValidationResults } from "@/lib/types-ingestion";

export default function PreviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<IngestionSession | null>(null);
  const [validationResults, setValidationResults] = useState<ValidationResults | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      setIsLoading(true);
      try {
        const res = await fetch(`/api/ingest/sessions/${sessionId}`, {
          credentials: "include",
        });

        if (!res.ok) {
          throw new Error("Failed to fetch session");
        }

        const data = await res.json();
        setSession(data.session);
        setValidationResults(data.session.validation_results);
      } catch (error) {
        console.error("Failed to load session:", error);
        router.push("/ingest");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSession();
  }, [sessionId, router]);

  const handleApprove = async () => {
    try {
      const res = await fetch(`/api/ingest/sessions/${sessionId}/approve`, {
        method: "POST",
        credentials: "include",
      });

      if (!res.ok) {
        throw new Error("Failed to approve session");
      }

      router.push(`/ingest/${sessionId}/status`);
    } catch (error) {
      console.error("Approval failed:", error);
      alert("Failed to start pipeline. Please try again.");
    }
  };

  const handleReUpload = () => {
    router.push("/ingest");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2 text-wash-gray">
          <svg
            className="animate-spin h-6 w-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          Loading validation results...
        </div>
      </div>
    );
  }

  if (!session || !validationResults) {
    return null;
  }

  const hasErrors = validationResults.errors.length > 0;

  return (
    <div className="min-h-screen bg-ivory p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Page Header */}
        <div>
          <button
            onClick={() => router.push("/ingest")}
            className="flex items-center gap-1 text-sm text-growth-green hover:underline mb-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Upload
          </button>

          <h1 className="text-3xl font-bold text-raw-umber">Preview & Validate</h1>
          <p className="text-sm text-wash-gray mt-1">
            Review file summaries and validation results before running the pipeline.
          </p>
        </div>

        {/* File Summaries */}
        <FileSummaryGrid summaries={validationResults.file_summaries} />

        {/* Validation Results */}
        <ValidationPanel results={validationResults} />

        {/* Action Bar */}
        <div className="flex items-center justify-between gap-4">
          <button
            onClick={handleReUpload}
            className="text-wash-gray hover:text-raw-umber hover:underline"
          >
            Re-upload Files
          </button>

          <ApproveButton
            disabled={hasErrors}
            hasWarnings={validationResults.warnings.length > 0}
            onApprove={handleApprove}
          />
        </div>
      </div>
    </div>
  );
}
```

**Props:** None (page component, uses params)

**State:**
- `session: IngestionSession | null` - Session data
- `validationResults: ValidationResults | null` - Validation output
- `isLoading: boolean` - Loading state

**Accessibility:**
- Back button with arrow icon
- Loading state with spinner and text
- Clear error messaging

---

### FileSummaryGrid Component

**File:** `/frontend/components/ingest/file-summary-grid.tsx`

```typescript
"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileSummary, FILE_TYPE_LABELS } from "@/lib/types-ingestion";
import { cn } from "@/lib/utils";

interface FileSummaryGridProps {
  summaries: FileSummary[];
}

export function FileSummaryGrid({ summaries }: FileSummaryGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {summaries.map((summary) => (
        <FileSummaryCard key={summary.file_type} summary={summary} />
      ))}
    </div>
  );
}

interface FileSummaryCardProps {
  summary: FileSummary;
}

function FileSummaryCard({ summary }: FileSummaryCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">
            {FILE_TYPE_LABELS[summary.file_type]}
          </CardTitle>
          <Badge color="#694FA0">{summary.file_type}</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Metadata */}
        <div className="flex gap-6 text-sm">
          <div>
            <span className="text-wash-gray">Rows:</span>{" "}
            <span className="font-medium text-raw-umber">{summary.row_count.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-wash-gray">Columns:</span>{" "}
            <span className="font-medium text-raw-umber">{summary.column_count}</span>
          </div>
        </div>

        {/* Expand Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-sm text-growth-green hover:underline"
        >
          {isExpanded ? "Hide" : "Show"} Sample Data
          <svg
            className={cn("w-4 h-4 transition-transform", isExpanded && "rotate-180")}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {/* Sample Data Table */}
        {isExpanded && (
          <div className="overflow-x-auto border border-gray rounded-md">
            <table className="w-full text-xs">
              <thead className="bg-sage/20">
                <tr>
                  {Object.keys(summary.sample_rows[0] || {}).map((col) => (
                    <th key={col} className="text-left py-2 px-3 font-medium text-raw-umber">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {summary.sample_rows.slice(0, 10).map((row, idx) => (
                  <tr key={idx} className="border-t border-gray">
                    {Object.values(row).map((val, colIdx) => (
                      <td key={colIdx} className="py-2 px-3 text-wash-gray">
                        {String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**Props:**
- `summaries: FileSummary[]` - File metadata and sample rows

**State (per card):**
- `isExpanded: boolean` - Show/hide sample data table

**Interactions:**
- Expand/collapse button with animated arrow icon
- Responsive grid (1 column mobile, 2 columns desktop)

**Accessibility:**
- Semantic table structure
- Clear column headers
- Icon has `aria-hidden="true"`

---

### ValidationPanel Component

**File:** `/frontend/components/ingest/validation-panel.tsx`

```typescript
"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ValidationResults, ValidationIssue } from "@/lib/types-ingestion";

interface ValidationPanelProps {
  results: ValidationResults;
}

export function ValidationPanel({ results }: ValidationPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Validation Results</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Errors */}
        {results.errors.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-rose mb-2 flex items-center gap-2">
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              Errors ({results.errors.length})
            </h4>
            <div className="space-y-2">
              {results.errors.map((issue, idx) => (
                <ValidationIssueItem key={idx} issue={issue} level="error" />
              ))}
            </div>
          </div>
        )}

        {/* Warnings */}
        {results.warnings.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-amber-600 mb-2 flex items-center gap-2">
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Warnings ({results.warnings.length})
            </h4>
            <div className="space-y-2">
              {results.warnings.map((issue, idx) => (
                <ValidationIssueItem key={idx} issue={issue} level="warning" />
              ))}
            </div>
          </div>
        )}

        {/* Info */}
        {results.info.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-wash-gray mb-2 flex items-center gap-2">
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Info ({results.info.length})
            </h4>
            <div className="space-y-2">
              {results.info.map((issue, idx) => (
                <ValidationIssueItem key={idx} issue={issue} level="info" />
              ))}
            </div>
          </div>
        )}

        {/* No Issues */}
        {results.errors.length === 0 &&
          results.warnings.length === 0 &&
          results.info.length === 0 && (
            <div className="flex items-center gap-2 p-4 bg-sage/20 rounded-md text-growth-green">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">All validation checks passed!</span>
            </div>
          )}
      </CardContent>
    </Card>
  );
}

interface ValidationIssueItemProps {
  issue: ValidationIssue;
  level: "error" | "warning" | "info";
}

function ValidationIssueItem({ issue, level }: ValidationIssueItemProps) {
  const colors = {
    error: "bg-rose/10 border-rose/30 text-rose",
    warning: "bg-amber-50 border-amber-200 text-amber-700",
    info: "bg-gray/30 border-gray text-wash-gray",
  };

  return (
    <div
      className={`p-3 border rounded-md ${colors[level]}`}
      role={level === "error" ? "alert" : "status"}
    >
      <p className="text-sm font-medium">{issue.message}</p>
      {issue.details && (
        <p className="text-xs mt-1 opacity-80">{issue.details}</p>
      )}
      {issue.affected_rows !== undefined && (
        <p className="text-xs mt-1 opacity-80">
          Affected rows: {issue.affected_rows.toLocaleString()}
        </p>
      )}
    </div>
  );
}
```

**Props:**
- `results: ValidationResults` - Validation output

**Accessibility:**
- `role="alert"` for errors
- `role="status"` for warnings/info
- Icons have `aria-hidden="true"`
- Clear visual hierarchy with color and icons

**Color Usage:**
- Errors: `text-rose`, `bg-rose/10`, `border-rose/30`
- Warnings: `text-amber-700`, `bg-amber-50`, `border-amber-200`
- Info: `text-wash-gray`, `bg-gray/30`, `border-gray`
- Success: `text-growth-green`, `bg-sage/20`

---

### ApproveButton Component

**File:** `/frontend/components/ingest/approve-button.tsx`

```typescript
"use client";

import { useState, useRef } from "react";
import { useMutationGuard } from "@/lib/hooks/use-mutation-guard";
import { cn } from "@/lib/utils";

interface ApproveButtonProps {
  disabled: boolean;
  hasWarnings: boolean;
  onApprove: () => Promise<void>;
}

export function ApproveButton({ disabled, hasWarnings, onApprove }: ApproveButtonProps) {
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const { guard } = useMutationGuard();

  const handleClick = () => {
    if (hasWarnings) {
      setShowConfirmation(true);
    } else {
      handleConfirm();
    }
  };

  const handleConfirm = guard(async () => {
    setIsExecuting(true);
    try {
      await onApprove();
    } finally {
      setIsExecuting(false);
      setShowConfirmation(false);
    }
  });

  const handleCancel = () => {
    setShowConfirmation(false);
  };

  return (
    <>
      <button
        onClick={handleClick}
        disabled={disabled || isExecuting}
        className={cn(
          "px-6 py-3 font-medium text-white rounded-md transition-all",
          "bg-growth-green hover:bg-legacy-green",
          "focus:outline-none focus:ring-2 focus:ring-growth-green focus:ring-offset-2",
          "disabled:bg-wash-gray disabled:cursor-not-allowed"
        )}
      >
        {isExecuting ? "Starting Pipeline..." : "Approve & Run Pipeline"}
      </button>

      {/* Confirmation Dialog */}
      {showConfirmation && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-dialog-title"
        >
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-start gap-3">
              <svg
                className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div className="flex-1">
                <h3 id="confirm-dialog-title" className="text-lg font-semibold text-raw-umber">
                  Warnings Detected
                </h3>
                <p className="text-sm text-wash-gray mt-1">
                  There are validation warnings. Proceeding may result in incomplete or
                  inaccurate data. Are you sure you want to continue?
                </p>
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={handleCancel}
                disabled={isExecuting}
                className="px-4 py-2 text-sm font-medium text-wash-gray hover:text-raw-umber transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={isExecuting}
                className={cn(
                  "px-4 py-2 text-sm font-medium text-white rounded-md",
                  "bg-amber-600 hover:bg-amber-700",
                  "disabled:bg-wash-gray disabled:cursor-not-allowed"
                )}
              >
                {isExecuting ? "Starting..." : "Continue Anyway"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

**Props:**
- `disabled: boolean` - Disable button (e.g., when errors present)
- `hasWarnings: boolean` - Show confirmation dialog before approve
- `onApprove: () => Promise<void>` - Approval handler

**State:**
- `showConfirmation: boolean` - Dialog visibility
- `isExecuting: boolean` - Prevent double-click

**Interactions:**
- No warnings: immediate approval
- Has warnings: show confirmation dialog
- Dialog: cancel or confirm
- useMutationGuard prevents double-click

**Accessibility:**
- Dialog with `role="dialog"` and `aria-modal="true"`
- `aria-labelledby` links to dialog title
- Focus management (browser default)
- Escape key to close (could add with onKeyDown)

---

## Page 4: Status

**Route:** `/frontend/app/ingest/[sessionId]/status/page.tsx`
**Purpose:** Real-time pipeline execution monitoring with polling
**Layout:** Progress indicator, step statuses, success/error states

### Component Tree

```
StatusPage (Client Component)
├── PageHeader
├── PipelineProgressBar
├── StepStatusList
│   └── StepStatusItem[] (per pipeline step)
│       ├── StepIcon (pending/running/complete/failed)
│       ├── StepName
│       └── ElapsedTime
├── ElapsedTimeCounter
├── SuccessState (conditional)
│   ├── TierDistributionTable
│   └── GoToReviewButton
├── ErrorState (conditional)
│   ├── ErrorMessage
│   ├── GuidanceText
│   ├── RetryButton
│   └── ReUploadButton
└── SessionExpiredMessage (conditional)
```

### StatusPage Component

**File:** `/frontend/app/ingest/[sessionId]/status/page.tsx`

```typescript
"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { usePolling } from "@/lib/hooks/use-polling";
import { PipelineStatusDisplay } from "@/components/ingest/pipeline-status-display";
import { PipelineStatus } from "@/lib/types-ingestion";

export default function StatusPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`/api/ingest/sessions/${sessionId}/status`, {
        credentials: "include",
      });

      if (res.status === 401) {
        // Session expired during polling - show inline message, don't redirect
        setSessionExpired(true);
        return null;
      }

      if (!res.ok) {
        throw new Error("Failed to fetch status");
      }

      const data = await res.json();
      return data.status as PipelineStatus;
    } catch (error) {
      console.error("Failed to fetch status:", error);
      return null;
    }
  }, [sessionId]);

  // Initial load
  useEffect(() => {
    const loadInitialStatus = async () => {
      setIsLoading(true);
      const status = await fetchStatus();
      if (status) {
        setPipelineStatus(status);
      }
      setIsLoading(false);
    };

    loadInitialStatus();
  }, [fetchStatus]);

  // Polling
  const shouldStopPolling = useCallback((status: PipelineStatus | null) => {
    if (!status) return false;
    return status.overall_status === "complete" || status.overall_status === "failed";
  }, []);

  usePolling({
    fn: fetchStatus,
    interval: 2000, // Poll every 2 seconds
    enabled: !isLoading && !sessionExpired && pipelineStatus?.overall_status === "running",
    onSuccess: (status) => {
      if (status) {
        setPipelineStatus(status);
      }
    },
    shouldStop: shouldStopPolling,
  });

  const handleRetry = async () => {
    try {
      const res = await fetch(`/api/ingest/sessions/${sessionId}/retry`, {
        method: "POST",
        credentials: "include",
      });

      if (!res.ok) {
        throw new Error("Failed to retry");
      }

      // Reload page to restart polling
      window.location.reload();
    } catch (error) {
      console.error("Retry failed:", error);
      alert("Failed to retry. Please try again.");
    }
  };

  const handleReUpload = () => {
    router.push("/ingest");
  };

  const handleGoToReview = () => {
    router.push("/review");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2 text-wash-gray">
          <svg
            className="animate-spin h-6 w-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          Loading pipeline status...
        </div>
      </div>
    );
  }

  if (sessionExpired) {
    return (
      <div className="min-h-screen bg-ivory p-6">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="py-12">
              <div className="text-center space-y-4">
                <svg
                  className="mx-auto w-16 h-16 text-wash-gray"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
                <h2 className="text-xl font-semibold text-raw-umber">Session Expired</h2>
                <p className="text-wash-gray">
                  Your session has expired. Please log in again to view pipeline status.
                </p>
                <button
                  onClick={() => router.push("/login")}
                  className="px-4 py-2 bg-growth-green text-white rounded-md hover:bg-legacy-green"
                >
                  Go to Login
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!pipelineStatus) {
    return null;
  }

  return (
    <div className="min-h-screen bg-ivory p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-raw-umber">Pipeline Status</h1>
          <p className="text-sm text-wash-gray mt-1">
            Monitoring pipeline execution for session {sessionId.slice(0, 8)}...
          </p>
        </div>

        {/* Pipeline Status Display */}
        <PipelineStatusDisplay
          status={pipelineStatus}
          onRetry={handleRetry}
          onReUpload={handleReUpload}
          onGoToReview={handleGoToReview}
        />
      </div>
    </div>
  );
}
```

**Props:** None (page component, uses params)

**State:**
- `pipelineStatus: PipelineStatus | null` - Current pipeline state
- `sessionExpired: boolean` - 401 during polling
- `isLoading: boolean` - Initial load

**Polling:**
- Enabled when status is "running"
- Stops when "complete" or "failed"
- 2-second interval
- Pauses when tab hidden (via usePolling hook)

**Edge Cases:**
- Session expired (401): show inline message, not redirect
- Network error: continues polling
- Tab hidden: pauses polling, resumes on visibility

---

### PipelineStatusDisplay Component

**File:** `/frontend/components/ingest/pipeline-status-display.tsx`

```typescript
"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PipelineStatus, PipelineStepStatus } from "@/lib/types-ingestion";
import { cn } from "@/lib/utils";

interface PipelineStatusDisplayProps {
  status: PipelineStatus;
  onRetry: () => void;
  onReUpload: () => void;
  onGoToReview: () => void;
}

export function PipelineStatusDisplay({
  status,
  onRetry,
  onReUpload,
  onGoToReview,
}: PipelineStatusDisplayProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(status.elapsed_seconds);

  // Update elapsed time counter every second
  useEffect(() => {
    if (status.overall_status === "running") {
      const interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [status.overall_status]);

  // Sync with server elapsed time when status updates
  useEffect(() => {
    setElapsedSeconds(status.elapsed_seconds);
  }, [status.elapsed_seconds]);

  const formatElapsedTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Overall Progress</CardTitle>
            <span className="text-sm text-wash-gray">
              {formatElapsedTime(elapsedSeconds)} elapsed
            </span>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-raw-umber font-medium">
                {status.overall_progress}% Complete
              </span>
              <Badge
                color={
                  status.overall_status === "complete"
                    ? "#00A66C"
                    : status.overall_status === "failed"
                    ? "#E63946"
                    : "#54ADD3"
                }
              >
                {status.overall_status === "running"
                  ? "Running"
                  : status.overall_status === "complete"
                  ? "Complete"
                  : "Failed"}
              </Badge>
            </div>

            <div className="w-full bg-gray rounded-full h-2">
              <div
                className={cn(
                  "h-2 rounded-full transition-all duration-500",
                  status.overall_status === "failed"
                    ? "bg-rose"
                    : "bg-growth-green"
                )}
                style={{ width: `${status.overall_progress}%` }}
                role="progressbar"
                aria-valuenow={status.overall_progress}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Overall progress: ${status.overall_progress}%`}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step Status List */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Steps</CardTitle>
        </CardHeader>

        <CardContent>
          <div className="space-y-3">
            {status.steps.map((step, idx) => (
              <StepStatusItem key={step.step} step={step} isLast={idx === status.steps.length - 1} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Success State */}
      {status.overall_status === "complete" && status.tier_distribution && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Complete</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center gap-2 text-growth-green">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">
                Pipeline completed successfully in {formatElapsedTime(status.elapsed_seconds)}
              </span>
            </div>

            {/* Tier Distribution */}
            <div>
              <h4 className="text-sm font-medium text-raw-umber mb-2">Tier Distribution</h4>
              <table className="w-full text-sm">
                <thead className="border-b border-gray">
                  <tr>
                    <th className="text-left py-2 font-medium text-raw-umber">Tier</th>
                    <th className="text-right py-2 font-medium text-raw-umber">Applicants</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(status.tier_distribution).map(([tier, count]) => (
                    <tr key={tier} className="border-b border-gray">
                      <td className="py-2 text-raw-umber">Tier {tier}</td>
                      <td className="py-2 text-right text-raw-umber font-medium">
                        {count.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button
              onClick={onGoToReview}
              className="w-full px-4 py-3 bg-growth-green text-white font-medium rounded-md hover:bg-legacy-green transition-colors"
            >
              Go to Review Queue
            </button>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {status.overall_status === "failed" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-rose">Pipeline Failed</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-start gap-2 text-rose">
              <svg
                className="w-6 h-6 flex-shrink-0 mt-0.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <p className="font-medium">
                  {status.error_summary || "An error occurred during pipeline execution."}
                </p>
              </div>
            </div>

            {/* Guidance */}
            <div className="p-4 bg-sage/20 rounded-md">
              <p className="text-sm text-raw-umber font-medium mb-2">What to do next:</p>
              <ul className="text-sm text-wash-gray space-y-1 list-disc list-inside">
                <li>
                  <strong>Retry:</strong> Attempt to re-run the pipeline with the same files.
                  Use this if the error was transient (e.g., network issue).
                </li>
                <li>
                  <strong>Re-upload:</strong> Go back to upload new files. Use this if there
                  was an issue with the data itself.
                </li>
              </ul>
            </div>

            <div className="flex gap-3">
              <button
                onClick={onRetry}
                className="flex-1 px-4 py-2 bg-cerulean-blue text-white font-medium rounded-md hover:bg-cerulean-blue/80 transition-colors"
              >
                Retry Pipeline
              </button>
              <button
                onClick={onReUpload}
                className="flex-1 px-4 py-2 border border-gray text-raw-umber font-medium rounded-md hover:bg-sage/10 transition-colors"
              >
                Re-upload Files
              </button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface StepStatusItemProps {
  step: PipelineStepStatus;
  isLast: boolean;
}

function StepStatusItem({ step, isLast }: StepStatusItemProps) {
  const getStepIcon = () => {
    switch (step.status) {
      case "complete":
        return (
          <svg
            className="w-6 h-6 text-growth-green"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
      case "running":
        return (
          <svg
            className="animate-spin w-6 h-6 text-cerulean-blue"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        );
      case "failed":
        return (
          <svg
            className="w-6 h-6 text-rose"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
      default: // pending
        return (
          <div className="w-6 h-6 rounded-full border-2 border-gray bg-white" aria-hidden="true" />
        );
    }
  };

  const getStepLabel = () => {
    const labels = {
      ingestion: "Data Ingestion",
      cleaning: "Data Cleaning",
      features: "Feature Engineering",
      scoring: "Model Scoring",
      triage: "Tier Assignment",
    };
    return labels[step.step] || step.step;
  };

  const formatElapsedTime = (seconds: number | null) => {
    if (seconds === null) return "-";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="flex items-start gap-3">
      {/* Icon */}
      <div className="flex flex-col items-center">
        {getStepIcon()}
        {!isLast && <div className="w-0.5 h-8 bg-gray mt-1" aria-hidden="true" />}
      </div>

      {/* Step Info */}
      <div className="flex-1 pb-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-raw-umber">{getStepLabel()}</h4>
          {step.elapsed_seconds !== null && (
            <span className="text-xs text-wash-gray">
              {formatElapsedTime(step.elapsed_seconds)}
            </span>
          )}
        </div>

        {step.error_message && (
          <p className="text-xs text-rose mt-1" role="alert">
            {step.error_message}
          </p>
        )}
      </div>
    </div>
  );
}
```

**Props:**
- `status: PipelineStatus` - Pipeline execution state
- `onRetry: () => void` - Retry handler
- `onReUpload: () => void` - Re-upload handler
- `onGoToReview: () => void` - Navigate to review queue

**State:**
- `elapsedSeconds: number` - Local counter for elapsed time

**Interactions:**
- Elapsed time counter: updates every second when running
- Progress bar: animates with transition
- Step icons: spinner for running, check for complete, X for failed
- Success state: tier distribution table, review queue button
- Error state: guidance text, retry/re-upload buttons

**Accessibility:**
- Progress bar with `role="progressbar"` and ARIA attributes
- Error messages with `role="alert"`
- Icons have `aria-hidden="true"`
- Clear visual hierarchy

**Color Usage:**
- Running: `text-cerulean-blue`, spinner
- Complete: `text-growth-green`, `bg-growth-green`
- Failed: `text-rose`, `bg-rose`
- Pending: `border-gray`, white background

---

## API Contracts

### Authentication

**POST /api/auth/login**
```typescript
Request: { username: string; password: string }
Response: { user: { username: string; role: string; session_id: string } }
Errors: 401 (invalid credentials)
```

**GET /api/auth/me**
```typescript
Response: { user: { username: string; role: string; session_id: string } }
Errors: 401 (not authenticated)
```

**POST /api/auth/logout**
```typescript
Response: { status: "success" }
```

### Ingestion

**GET /api/ingest/sessions**
```typescript
Response: { sessions: IngestionSession[] }
```

**POST /api/ingest/sessions**
```typescript
Request: { cycle_year: number }
Response: { session_id: string }
```

**POST /api/ingest/sessions/:sessionId/upload**
```typescript
Request: FormData { file: File; file_type: AmcasFileType }
Response: { file_id: string }
Errors: 400 (invalid file), 413 (file too large)
```

**POST /api/ingest/sessions/:sessionId/validate**
```typescript
Response: { validation_results: ValidationResults }
```

**GET /api/ingest/sessions/:sessionId**
```typescript
Response: { session: IngestionSession }
Errors: 404 (session not found)
```

**POST /api/ingest/sessions/:sessionId/approve**
```typescript
Response: { status: "approved" }
Errors: 400 (validation errors present)
```

**GET /api/ingest/sessions/:sessionId/status**
```typescript
Response: { status: PipelineStatus }
Errors: 401 (session expired), 404 (session not found)
```

**POST /api/ingest/sessions/:sessionId/retry**
```typescript
Response: { status: "retrying" }
```

---

## Accessibility Checklist

### General
- [ ] All pages use semantic HTML (headings, landmarks, lists)
- [ ] Color is not the only means of conveying information
- [ ] Focus styles are visible on all interactive elements
- [ ] Keyboard navigation works throughout (Tab, Enter, Space, Arrow keys)
- [ ] Loading states announced to screen readers

### Login Page
- [ ] Form inputs have associated labels
- [ ] Error messages linked to inputs via aria-describedby
- [ ] Submit button shows loading state
- [ ] Password field has type="password"

### Upload Page
- [ ] Drop zone accessible via keyboard (Enter/Space to open file picker)
- [ ] File input hidden but functional
- [ ] Progress bars have role="progressbar" and ARIA values
- [ ] Required files checklist uses icons + text
- [ ] beforeunload warning prevents accidental navigation

### Preview Page
- [ ] Validation errors have role="alert"
- [ ] Warnings have role="status"
- [ ] Sample data tables have proper headers
- [ ] Expandable sections keyboard accessible
- [ ] Approve confirmation dialog has role="dialog" and aria-modal

### Status Page
- [ ] Progress bars have ARIA attributes
- [ ] Step status icons supplemented by text
- [ ] Live region for status updates (could add aria-live)
- [ ] Session expired message clear and actionable
- [ ] Error messages user-friendly (no stack traces)

---

## Performance Considerations

### Code Splitting
- Use Next.js dynamic imports for heavy components:
  ```typescript
  const SampleDataTable = dynamic(() => import('./sample-data-table'), {
    loading: () => <p>Loading...</p>
  });
  ```

### Memoization
- Wrap expensive computations in `useMemo`:
  ```typescript
  const hasAllRequiredFiles = useMemo(() =>
    REQUIRED_FILE_TYPES.every(type =>
      files.some(f => (f.manual_override_type || f.detected_type) === type)
    ),
    [files]
  );
  ```

- Wrap callbacks in `useCallback` to prevent re-renders:
  ```typescript
  const handleFileRemove = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.file_id !== fileId));
  }, []);
  ```

### Polling Optimization
- Use recursive setTimeout instead of setInterval
- Integrate Page Visibility API to pause when tab hidden
- Debounce rapid state updates

### Upload Optimization
- Use XHR instead of fetch for progress tracking
- Upload files in parallel (Promise.all)
- Show per-file progress bars

### Image/Asset Optimization
- Use Next.js Image component for any images
- Lazy load images below the fold
- Use SVG icons (inline) instead of icon fonts

---

## File Paths Summary

### Shared Infrastructure
- `/frontend/lib/auth-context.tsx` - Auth provider
- `/frontend/lib/hooks/use-polling.ts` - Polling hook
- `/frontend/lib/hooks/use-mutation-guard.ts` - Double-click prevention
- `/frontend/lib/hooks/use-abort-controller.ts` - Request cleanup
- `/frontend/lib/types-ingestion.ts` - Type definitions

### Page 1: Login
- `/frontend/app/login/page.tsx` - Login page
- `/frontend/components/auth/login-form.tsx` - Login form component

### Page 2: Upload
- `/frontend/app/ingest/page.tsx` - Upload page
- `/frontend/components/ingest/cycle-year-selector.tsx` - Year dropdown
- `/frontend/components/ingest/pipeline-running-banner.tsx` - Banner
- `/frontend/components/ingest/upload-zone.tsx` - Drag-drop zone
- `/frontend/components/ingest/file-list.tsx` - File list
- `/frontend/components/ingest/required-files-checklist.tsx` - Checklist
- `/frontend/components/ingest/session-history-table.tsx` - History table

### Page 3: Preview
- `/frontend/app/ingest/[sessionId]/preview/page.tsx` - Preview page
- `/frontend/components/ingest/file-summary-grid.tsx` - File summaries
- `/frontend/components/ingest/validation-panel.tsx` - Validation results
- `/frontend/components/ingest/approve-button.tsx` - Approve button with dialog

### Page 4: Status
- `/frontend/app/ingest/[sessionId]/status/page.tsx` - Status page
- `/frontend/components/ingest/pipeline-status-display.tsx` - Status display with steps

---

## Next Steps

1. **Implement backend API endpoints** matching the contracts above
2. **Add unit tests** for hooks and complex components
3. **Add integration tests** for complete user flows (Playwright)
4. **Set up error tracking** (Sentry) for production monitoring
5. **Add analytics** to track upload success rates and error patterns
6. **Enhance error messages** with specific guidance based on error types
7. **Add keyboard shortcuts** for power users (e.g., "R" to retry)
8. **Implement optimistic UI updates** for immediate feedback
9. **Add toast notifications** for background events (upload complete, validation done)
10. **Create admin dashboard** for monitoring all sessions across users

---

This specification provides complete component designs, TypeScript interfaces, state management patterns, accessibility attributes, and Tailwind styling for all four pages of the AMCAS file ingestion wizard. All components are designed for non-technical users with clear feedback, error prevention, and progressive disclosure of complexity.
