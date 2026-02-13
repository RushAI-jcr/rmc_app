"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileSpreadsheet, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { uploadFiles, getSessions } from "@/lib/api";
import type { SessionSummary } from "@/lib/types";
import { REQUIRED_FILE_TYPES, AMCAS_FILE_TYPES, SESSION_STATUS_COLORS } from "@/lib/types";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function IngestPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [cycleYear, setCycleYear] = useState(new Date().getFullYear());
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [dragOver, setDragOver] = useState(false);

  const uploadingRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load session history
  useEffect(() => {
    getSessions().then(setSessions).catch(() => {});
  }, []);

  // Warn on navigation during upload
  useEffect(() => {
    if (!uploading) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [uploading]);

  // Abort in-flight upload on unmount
  useEffect(() => {
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const addFiles = useCallback((newFiles: FileList | File[]) => {
    const xlsxFiles = Array.from(newFiles).filter((f) =>
      f.name.toLowerCase().endsWith(".xlsx"),
    );
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      const unique = xlsxFiles.filter((f) => !existing.has(f.name));
      return [...prev, ...unique];
    });
    setError(null);
  }, []);

  const removeFile = (name: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const handleUpload = async () => {
    if (uploadingRef.current || files.length === 0) return;
    uploadingRef.current = true;
    setUploading(true);
    setError(null);

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const res = await uploadFiles(files, cycleYear, controller.signal);
      router.push(`/ingest/${res.session_id}/preview`);
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      setError(e instanceof Error ? e.message : "Upload failed");
      uploadingRef.current = false;
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  };

  // Check if there's an active pipeline run
  const hasActiveRun = sessions.some(
    (s) => s.status === "processing" || s.status === "approved",
  );

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Upload AMCAS Data</h2>

      {hasActiveRun && (
        <div className="mb-6 rounded-lg border border-purple/30 bg-purple/5 p-4">
          <p className="text-sm font-medium text-purple">
            A pipeline is currently running. New uploads are disabled until it completes.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload area */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>New Upload</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Cycle year selector */}
              <div className="mb-4">
                <label htmlFor="cycle-year" className="mb-1 block text-sm font-medium">
                  Cycle Year
                </label>
                <select
                  id="cycle-year"
                  value={cycleYear}
                  onChange={(e) => setCycleYear(Number(e.target.value))}
                  disabled={hasActiveRun}
                  className="rounded-md border border-gray px-3 py-2 text-sm focus:border-legacy-green focus:outline-none focus:ring-1 focus:ring-legacy-green"
                >
                  {yearOptions.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>

              {/* Drop zone */}
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(true);
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => !hasActiveRun && fileInputRef.current?.click()}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (!hasActiveRun) fileInputRef.current?.click();
                  }
                }}
                role="button"
                tabIndex={0}
                aria-label="Upload xlsx files"
                className={cn(
                  "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors cursor-pointer",
                  hasActiveRun
                    ? "border-gray/50 bg-gray/10 cursor-not-allowed opacity-50"
                    : dragOver
                      ? "border-vitality-green bg-sage/30"
                      : "border-gray hover:border-growth-green hover:bg-sage/10",
                )}
              >
                <Upload className="mb-3 h-8 w-8 text-raw-umber" />
                <p className="text-sm font-medium">
                  Drag & drop .xlsx files here, or click to browse
                </p>
                <p className="mt-1 text-xs text-raw-umber">
                  Max 50MB per file, 200MB total
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx"
                  multiple
                  onChange={(e) => {
                    if (e.target.files) addFiles(e.target.files);
                    e.target.value = "";
                  }}
                  className="hidden"
                  disabled={hasActiveRun}
                />
              </div>

              {/* File list */}
              {files.length > 0 && (
                <div className="mt-4 space-y-2">
                  {files.map((f) => (
                    <div
                      key={f.name}
                      className="flex items-center justify-between rounded-md border border-gray px-3 py-2"
                    >
                      <div className="flex items-center gap-2">
                        <FileSpreadsheet className="h-4 w-4 text-growth-green" />
                        <span className="text-sm">{f.name}</span>
                        <span className="text-xs text-raw-umber">
                          {formatBytes(f.size)}
                        </span>
                      </div>
                      <button
                        onClick={() => removeFile(f.name)}
                        className="text-xs text-raw-umber hover:text-red-600 transition-colors"
                        aria-label={`Remove ${f.name}`}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {error && (
                <p role="alert" className="mt-3 text-sm text-red-600">
                  {error}
                </p>
              )}

              {/* Upload button */}
              <button
                onClick={handleUpload}
                disabled={files.length === 0 || uploading || hasActiveRun}
                className={cn(
                  "mt-4 w-full rounded-md px-4 py-2.5 text-sm font-medium text-white transition-colors",
                  files.length === 0 || uploading || hasActiveRun
                    ? "bg-gray cursor-not-allowed"
                    : "bg-legacy-green hover:bg-legacy-green/90",
                )}
              >
                {uploading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Uploading...
                  </span>
                ) : (
                  `Upload & Validate (${files.length} file${files.length !== 1 ? "s" : ""})`
                )}
              </button>
            </CardContent>
          </Card>
        </div>

        {/* Required files checklist */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Expected Files</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-xs text-raw-umber">
                Required files are marked with an asterisk. File types are auto-detected after upload.
              </p>
              <ul className="space-y-1.5">
                {AMCAS_FILE_TYPES.map((ft) => {
                  const isRequired = REQUIRED_FILE_TYPES.includes(ft);
                  return (
                    <li key={ft} className="flex items-center gap-2 text-sm">
                      {isRequired ? (
                        <span className="text-red-500 text-xs">*</span>
                      ) : (
                        <span className="text-xs text-transparent">*</span>
                      )}
                      <span>{ft.replace(/_/g, " ")}</span>
                    </li>
                  );
                })}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Session history */}
      {sessions.length > 0 && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Upload History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Date</th>
                    <th className="text-left py-2 px-3">Cycle Year</th>
                    <th className="text-left py-2 px-3">Status</th>
                    <th className="text-right py-2 px-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((s) => (
                    <tr key={s.id} className="border-b">
                      <td className="py-2 px-3">{formatDate(s.created_at)}</td>
                      <td className="py-2 px-3">{s.cycle_year}</td>
                      <td className="py-2 px-3">
                        <Badge color={SESSION_STATUS_COLORS[s.status]}>
                          {s.status}
                        </Badge>
                      </td>
                      <td className="py-2 px-3 text-right">
                        {(s.status === "uploaded" || s.status === "validated") && (
                          <button
                            onClick={() => router.push(`/ingest/${s.id}/preview`)}
                            className="text-xs text-legacy-green hover:underline"
                          >
                            Preview
                          </button>
                        )}
                        {(s.status === "processing" || s.status === "approved" || s.status === "complete" || s.status === "failed") && (
                          <button
                            onClick={() => router.push(`/ingest/${s.id}/status`)}
                            className="text-xs text-legacy-green hover:underline"
                          >
                            Status
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
