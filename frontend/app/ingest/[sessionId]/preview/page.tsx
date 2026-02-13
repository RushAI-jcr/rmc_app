"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  FileSpreadsheet,
  Info,
  Loader2,
  XCircle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { getPreview, approveSession } from "@/lib/api";
import type { PreviewData, FilePreview, ValidationResult } from "@/lib/types";

function FileSummaryCard({
  file,
  expanded,
  onToggle,
}: {
  file: FilePreview;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="rounded-lg border border-gray">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-sage/10 transition-colors"
      >
        <div className="flex items-center gap-3">
          <FileSpreadsheet className="h-4 w-4 text-growth-green" />
          <div>
            <p className="text-sm font-medium">{file.filename}</p>
            <p className="text-xs text-raw-umber">
              {file.detected_type
                ? file.detected_type.replace(/_/g, " ")
                : "Unknown type"}{" "}
              &middot; {file.row_count.toLocaleString()} rows &middot;{" "}
              {file.column_count} columns
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronDown className="h-4 w-4 text-raw-umber" />
        ) : (
          <ChevronRight className="h-4 w-4 text-raw-umber" />
        )}
      </button>

      {expanded && file.sample_rows.length > 0 && (
        <div className="border-t border-gray overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-sage/20">
                {file.columns.map((col) => (
                  <th key={col} className="text-left py-1.5 px-2 font-medium whitespace-nowrap">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {file.sample_rows.map((row, i) => (
                <tr key={i} className="border-t border-gray/50">
                  {file.columns.map((col) => (
                    <td key={col} className="py-1.5 px-2 whitespace-nowrap max-w-[200px] truncate">
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function ValidationPanel({ validation }: { validation: ValidationResult }) {
  const { errors, warnings, info } = validation;

  return (
    <div className="space-y-3">
      {errors.length > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="h-4 w-4 text-red-600" />
            <p className="text-sm font-medium text-red-800">
              {errors.length} Error{errors.length !== 1 ? "s" : ""} &mdash; Must fix before approval
            </p>
          </div>
          <ul className="space-y-1">
            {errors.map((e, i) => (
              <li key={i} className="text-sm text-red-700">
                {e.message}
                {e.detail && (
                  <span className="text-red-500 text-xs block ml-4">{e.detail}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <p className="text-sm font-medium text-amber-800">
              {warnings.length} Warning{warnings.length !== 1 ? "s" : ""}
            </p>
          </div>
          <ul className="space-y-1">
            {warnings.map((w, i) => (
              <li key={i} className="text-sm text-amber-700">
                {w.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {info.length > 0 && (
        <div className="rounded-lg border border-gray bg-white p-4">
          <div className="flex items-center gap-2 mb-2">
            <Info className="h-4 w-4 text-raw-umber" />
            <p className="text-sm font-medium">Summary</p>
          </div>
          <ul className="space-y-1">
            {info.map((msg, i) => (
              <li key={i} className="text-sm text-raw-umber">
                {msg}
              </li>
            ))}
          </ul>
        </div>
      )}

      {errors.length === 0 && warnings.length === 0 && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <p className="text-sm font-medium text-green-800">
              All validations passed
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PreviewPage() {
  const params = useParams<{ sessionId: string }>();
  const router = useRouter();
  const sessionId = params.sessionId;

  const [data, setData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approvalState, setApprovalState] = useState<"idle" | "approving" | "error">("idle");
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());

  const approving = useRef(false);

  useEffect(() => {
    getPreview(sessionId)
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Failed to load preview");
        setLoading(false);
      });
  }, [sessionId]);

  const toggleFile = (filename: string) => {
    setExpandedFiles((prev) => {
      const next = new Set(prev);
      if (next.has(filename)) next.delete(filename);
      else next.add(filename);
      return next;
    });
  };

  const hasErrors = (data?.validation?.errors.length ?? 0) > 0;

  const handleApprove = () => {
    if (approving.current) return;
    approving.current = true;
    setApprovalState("approving");
    setApprovalError(null);

    approveSession(sessionId)
      .then((res) => {
        router.push(`/ingest/${sessionId}/status?run=${res.run_id}`);
      })
      .catch((e) => {
        approving.current = false;
        setApprovalState("error");
        setApprovalError(e instanceof Error ? e.message : "Approval failed");
      });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-raw-umber" />
        <span className="ml-2 text-raw-umber">Loading preview...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 mb-2">Failed to load preview</p>
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
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Preview &amp; Validate</h2>
          <p className="text-sm text-raw-umber">
            Cycle {data.cycle_year}
            {data.total_applicants !== null &&
              ` \u00B7 ${data.total_applicants.toLocaleString()} applicants`}
          </p>
        </div>
        <button
          onClick={() => router.push("/ingest")}
          className="text-sm text-raw-umber hover:text-legacy-green transition-colors"
        >
          Re-upload
        </button>
      </div>

      {/* Validation panel */}
      {data.validation && (
        <div className="mb-6">
          <ValidationPanel validation={data.validation} />
        </div>
      )}

      {/* File previews */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>
            Uploaded Files ({data.files.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.files.map((file) => (
              <FileSummaryCard
                key={file.filename}
                file={file}
                expanded={expandedFiles.has(file.filename)}
                onToggle={() => toggleFile(file.filename)}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleApprove}
          disabled={hasErrors || approvalState === "approving"}
          className={cn(
            "rounded-md px-6 py-2.5 text-sm font-medium text-white transition-colors",
            hasErrors || approvalState === "approving"
              ? "bg-gray cursor-not-allowed"
              : "bg-legacy-green hover:bg-legacy-green/90",
          )}
        >
          {approvalState === "approving" ? (
            <span className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Approving...
            </span>
          ) : (
            "Approve & Run Pipeline"
          )}
        </button>

        {hasErrors && (
          <p className="text-sm text-red-600">
            Fix validation errors before approving
          </p>
        )}
      </div>

      {approvalError && (
        <p role="alert" className="mt-3 text-sm text-red-600">
          {approvalError}
        </p>
      )}
    </div>
  );
}
