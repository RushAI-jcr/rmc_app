"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import {
  CheckCircle2,
  Circle,
  Loader2,
  XCircle,
  RefreshCw,
  ArrowRight,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { getPipelineRun, getPipelineRuns, retrySession } from "@/lib/api";
import type { PipelineRunStatus } from "@/lib/types";

const PIPELINE_STEPS = [
  { key: "ingestion", label: "Data Ingestion" },
  { key: "llm_scoring", label: "LLM Scoring" },
  { key: "cleaning", label: "Data Cleaning" },
  { key: "features", label: "Feature Engineering" },
  { key: "ml_scoring", label: "ML Scoring" },
  { key: "triage", label: "Tier Assignment" },
] as const;

function StepIndicator({
  step,
  status,
  isCurrent,
}: {
  step: { key: string; label: string };
  status: "pending" | "active" | "complete" | "failed";
  isCurrent: boolean;
}) {
  return (
    <div className="flex items-center gap-3 py-2">
      {status === "complete" && (
        <CheckCircle2 className="h-5 w-5 text-growth-green" />
      )}
      {status === "active" && (
        <Loader2 className="h-5 w-5 animate-spin text-purple" />
      )}
      {status === "failed" && (
        <XCircle className="h-5 w-5 text-red-500" />
      )}
      {status === "pending" && (
        <Circle className="h-5 w-5 text-gray" />
      )}
      <span
        className={cn(
          "text-sm",
          isCurrent ? "font-semibold" : "",
          status === "complete" ? "text-growth-green" : "",
          status === "failed" ? "text-red-600" : "",
          status === "pending" ? "text-raw-umber" : "",
        )}
      >
        {step.label}
        {status === "active" && step.key === "llm_scoring" && (
          <span className="ml-2 text-xs text-raw-umber font-normal">
            (Waiting for batch results...)
          </span>
        )}
      </span>
    </div>
  );
}

function formatElapsed(startedAt: string): string {
  const ms = Date.now() - new Date(startedAt).getTime();
  const secs = Math.floor(ms / 1000);
  const mins = Math.floor(secs / 60);
  const hours = Math.floor(mins / 60);
  if (hours > 0) return `${hours}h ${mins % 60}m`;
  if (mins > 0) return `${mins}m ${secs % 60}s`;
  return `${secs}s`;
}

function StatusPageContent() {
  const params = useParams<{ sessionId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = params.sessionId;

  const [run, setRun] = useState<PipelineRunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState("");
  const [loading, setLoading] = useState(true);

  const retrying = useRef(false);

  // Resolve run ID -- from query param or fetch latest for session
  const [runId, setRunId] = useState<string | null>(
    searchParams.get("run"),
  );

  useEffect(() => {
    if (runId) return;
    getPipelineRuns(sessionId)
      .then((runs) => {
        if (runs.length > 0) setRunId(runs[0].id);
        else setError("No pipeline run found for this session");
        setLoading(false);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Failed to load pipeline status");
        setLoading(false);
      });
  }, [runId, sessionId]);

  // Poll pipeline status with recursive setTimeout + AbortController
  useEffect(() => {
    if (!runId) return;

    const controller = new AbortController();
    let nextTimeout: ReturnType<typeof setTimeout> | null = null;

    const poll = async () => {
      if (controller.signal.aborted) return;
      try {
        const data = await getPipelineRun(runId, controller.signal);
        if (controller.signal.aborted) return;
        setRun(data);
        setLoading(false);

        if (data.status === "running" || data.status === "pending") {
          const delay = data.current_step === "llm_scoring" ? 60_000 : 3_000;
          nextTimeout = setTimeout(poll, delay);
        }
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return;
        if (controller.signal.aborted) return;
        setError(e instanceof Error ? e.message : "Failed to fetch status");
        setLoading(false);
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

  // Elapsed time counter
  useEffect(() => {
    if (!run?.started_at || (run.status !== "running" && run.status !== "pending")) return;

    const tick = () => setElapsed(formatElapsed(run.started_at!));
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [run?.started_at, run?.status]);

  const handleRetry = () => {
    if (retrying.current) return;
    retrying.current = true;

    retrySession(sessionId)
      .then((res) => {
        setRunId(res.run_id);
        setRun(null);
        setError(null);
        setLoading(true);
        retrying.current = false;
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Retry failed");
        retrying.current = false;
      });
  };

  // Determine step statuses
  function getStepStatus(stepKey: string): "pending" | "active" | "complete" | "failed" {
    if (!run) return "pending";
    if (run.status === "complete") return "complete";

    const currentIdx = PIPELINE_STEPS.findIndex((s) => s.key === run.current_step);
    const stepIdx = PIPELINE_STEPS.findIndex((s) => s.key === stepKey);

    if (run.status === "failed") {
      if (stepIdx < currentIdx) return "complete";
      if (stepIdx === currentIdx) return "failed";
      return "pending";
    }

    if (stepIdx < currentIdx) return "complete";
    if (stepIdx === currentIdx) return "active";
    return "pending";
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-raw-umber" />
        <span className="ml-2 text-raw-umber">Loading pipeline status...</span>
      </div>
    );
  }

  if (error && !run) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 mb-2">Something went wrong</p>
        <p className="text-sm text-raw-umber">{error}</p>
        <button
          onClick={() => router.push("/ingest")}
          className="mt-4 text-sm text-legacy-green hover:underline"
        >
          Back to uploads
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Pipeline Status</h2>

      {/* Progress bar */}
      {run && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              {run.status === "complete"
                ? "Complete"
                : run.status === "failed"
                  ? "Failed"
                  : run.current_step
                    ? run.current_step.replace(/_/g, " ")
                    : "Starting..."}
            </span>
            <span className="text-sm text-raw-umber">
              {run.progress_pct}%
              {elapsed && ` \u00B7 ${elapsed}`}
            </span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={run.progress_pct}
            aria-valuemin={0}
            aria-valuemax={100}
            className="h-2 w-full rounded-full bg-gray"
          >
            <div
              className={cn(
                "h-full rounded-full transition-all duration-500",
                run.status === "failed" ? "bg-red-400" : "bg-growth-green",
              )}
              style={{ width: `${run.progress_pct}%` }}
            />
          </div>
        </div>
      )}

      {/* Step indicators */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Pipeline Steps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-0.5">
            {PIPELINE_STEPS.map((step) => (
              <StepIndicator
                key={step.key}
                step={step}
                status={getStepStatus(step.key)}
                isCurrent={run?.current_step === step.key}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Completion state */}
      {run?.status === "complete" && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-6 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <p className="text-lg font-semibold text-green-800">Pipeline Complete</p>
          </div>

          {run.result_summary && (
            <div className="mb-4">
              {run.result_summary.applicant_count !== undefined && (
                <p className="text-sm text-green-700">
                  Processed {(run.result_summary.applicant_count as number).toLocaleString()} applicants
                </p>
              )}
              {run.result_summary.tier_distribution != null && (
                <div className="mt-2 flex gap-3">
                  {(Object.entries(run.result_summary.tier_distribution) as [string, number][]).map(
                    ([tier, count]) => (
                      <span key={tier} className="text-xs text-green-700">
                        Tier {tier}: {String(count)}
                      </span>
                    ),
                  )}
                </div>
              )}
            </div>
          )}

          <button
            onClick={() => router.push("/review")}
            className="inline-flex items-center gap-2 rounded-md bg-legacy-green px-4 py-2 text-sm font-medium text-white hover:bg-legacy-green/90 transition-colors"
          >
            Go to Review Queue
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Failure state */}
      {run?.status === "failed" && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <XCircle className="h-5 w-5 text-red-600" />
            <p className="text-lg font-semibold text-red-800">Pipeline Failed</p>
          </div>

          {run.error_log && (
            <p role="alert" className="text-sm text-red-700 mb-4">
              {run.error_log}
            </p>
          )}

          <div className="space-y-2 mb-4">
            <p className="text-xs text-red-600">
              <strong>Retry</strong> &mdash; Re-run with the same data (for transient errors like timeouts)
            </p>
            <p className="text-xs text-red-600">
              <strong>Re-upload</strong> &mdash; Upload corrected files (for data issues)
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-2 rounded-md bg-legacy-green px-4 py-2 text-sm font-medium text-white hover:bg-legacy-green/90 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
            <button
              onClick={() => router.push("/ingest")}
              className="rounded-md border border-gray px-4 py-2 text-sm font-medium hover:bg-sage/10 transition-colors"
            >
              Re-upload
            </button>
          </div>
        </div>
      )}

      {error && run && (
        <p role="alert" className="text-sm text-red-600 mt-2">
          {error}
        </p>
      )}
    </div>
  );
}

export default function StatusPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-raw-umber" />
          <span className="ml-2 text-raw-umber">Loading...</span>
        </div>
      }
    >
      <StatusPageContent />
    </Suspense>
  );
}
