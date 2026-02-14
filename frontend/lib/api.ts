import type {
  ApplicantSummary,
  ApplicantDetail,
  TriageSummary,
  ReviewQueueItem,
  StatsOverview,
  FairnessRow,
  UploadResponse,
  SessionSummary,
  PreviewData,
  PipelineRunResponse,
  PipelineRunStatus,
  UserInfo,
  ValidationResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text || `API error: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// -- Auth --

export async function login(
  username: string,
  password: string,
): Promise<{ status: string; username: string; role: string }> {
  return fetchJSON("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function logout(): Promise<{ status: string }> {
  return fetchJSON("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<UserInfo> {
  return fetchJSON("/api/auth/me");
}

// -- Applicants --

export async function getApplicants(params?: {
  config?: string;
  tier?: number;
  search?: string;
  cycle_year?: number;
  page?: number;
  page_size?: number;
}): Promise<{ total: number; page: number; page_size: number; results: ApplicantSummary[] }> {
  const sp = new URLSearchParams();
  if (params?.config) sp.set("config", params.config);
  if (params?.tier !== undefined) sp.set("tier", String(params.tier));
  if (params?.search) sp.set("search", params.search);
  if (params?.cycle_year !== undefined) sp.set("cycle_year", String(params.cycle_year));
  if (params?.page) sp.set("page", String(params.page));
  if (params?.page_size) sp.set("page_size", String(params.page_size));
  return fetchJSON(`/api/applicants?${sp}`);
}

export async function getApplicant(amcasId: number, config?: string): Promise<ApplicantDetail> {
  const sp = new URLSearchParams();
  if (config) sp.set("config", config);
  return fetchJSON(`/api/applicants/${amcasId}?${sp}`);
}

// -- Stats --

export async function getStats(config?: string): Promise<StatsOverview> {
  const sp = new URLSearchParams();
  if (config) sp.set("config", config);
  return fetchJSON(`/api/stats/overview?${sp}`);
}

// -- Triage --

export async function getTriageSummary(config?: string): Promise<TriageSummary> {
  const sp = new URLSearchParams();
  if (config) sp.set("config", config);
  return fetchJSON(`/api/triage/summary?${sp}`);
}

export async function runTriage(configName: string): Promise<{ status: string; total_processed: number; tier_distribution: Record<string, number> }> {
  return fetchJSON("/api/triage/run", {
    method: "POST",
    body: JSON.stringify({ config_name: configName }),
  });
}

// -- Review --

export async function getReviewQueue(config?: string, cycleYear?: number): Promise<ReviewQueueItem[]> {
  const sp = new URLSearchParams();
  if (config) sp.set("config", config);
  if (cycleYear !== undefined) sp.set("cycle_year", String(cycleYear));
  return fetchJSON(`/api/review/queue?${sp}`);
}

export async function submitDecision(
  amcasId: number,
  decision: string,
  notes: string,
  flagReason?: string,
): Promise<{ status: string }> {
  return fetchJSON(`/api/review/${amcasId}/decision`, {
    method: "POST",
    body: JSON.stringify({ decision, notes, flag_reason: flagReason || null }),
  });
}

export async function getNextUnreviewed(config?: string): Promise<ReviewQueueItem | null> {
  const sp = new URLSearchParams();
  if (config) sp.set("config", config);
  return fetchJSON(`/api/review/queue/next?${sp}`);
}

export async function getFlagSummary(): Promise<{ total_flags: number; by_reason: Record<string, number> }> {
  return fetchJSON("/api/review/flag-summary");
}

// -- Fairness --

export async function getFairnessReport(): Promise<{ status: string; report: FairnessRow[] }> {
  return fetchJSON("/api/fairness/report");
}

// -- Ingest --

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

export async function getValidation(sessionId: string): Promise<ValidationResult> {
  return fetchJSON(`/api/ingest/${sessionId}/validation`);
}

export async function approveSession(sessionId: string): Promise<PipelineRunResponse> {
  return fetchJSON(`/api/ingest/${sessionId}/approve`, { method: "POST" });
}

export async function retrySession(sessionId: string): Promise<PipelineRunResponse> {
  return fetchJSON(`/api/ingest/${sessionId}/retry`, { method: "POST" });
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

// -- Pipeline --

export async function getPipelineRun(
  runId: string,
  signal?: AbortSignal,
): Promise<PipelineRunStatus> {
  return fetchJSON(`/api/pipeline/runs/${runId}`, { signal });
}

export async function getPipelineRuns(sessionId?: string): Promise<PipelineRunStatus[]> {
  const sp = new URLSearchParams();
  if (sessionId) sp.set("session_id", sessionId);
  return fetchJSON(`/api/pipeline/runs?${sp}`);
}
