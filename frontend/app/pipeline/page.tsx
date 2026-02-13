"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { runTriage, getTriageSummary } from "@/lib/api";
import type { TriageSummary } from "@/lib/types";
import { TierChart } from "@/components/charts/tier-chart";

const stages = [
  { name: "Data Ingestion", desc: "Load xlsx files, normalize columns, join tables" },
  { name: "Feature Engineering", desc: "Extract structured + engineered + rubric features" },
  { name: "Model Training", desc: "Train classifiers + regressors, compute SHAP" },
];

export default function PipelinePage() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<{ status: string; total_processed: number; tier_distribution: Record<string, number> } | null>(null);
  const [summary, setSummary] = useState<TriageSummary | null>(null);
  const [config, setConfig] = useState("A_Structured");
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await runTriage(config);
      setResult(res);
      const sum = await getTriageSummary(config);
      setSummary(sum);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to run triage");
      setRunning(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Pipeline</h2>

      <div className="grid grid-cols-3 gap-4 mb-8">
        {stages.map((stage, i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle>
                <span className="inline-flex items-center justify-center w-6 h-6 bg-cerulean-blue/20 text-cerulean-blue rounded-full text-xs mr-2">
                  {i + 1}
                </span>
                {stage.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-raw-umber">{stage.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mb-8">
        <CardHeader><CardTitle>Run Triage</CardTitle></CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          <div className="flex items-center gap-4">
            <select
              value={config}
              onChange={(e) => setConfig(e.target.value)}
              className="border border-gray rounded-lg px-3 py-2 text-sm"
            >
              <option value="A_Structured">Plan A: Structured Only</option>
              <option value="D_Struct+Rubric">Plan B: Structured + Rubric</option>
            </select>
            <button
              onClick={handleRun}
              disabled={running}
              className="px-6 py-2 bg-legacy-green text-white rounded-lg text-sm font-semibold hover:bg-growth-green disabled:opacity-50"
            >
              {running ? "Running..." : "Run Triage"}
            </button>
          </div>
          {result && (
            <div className="mt-4 p-4 bg-sage rounded-lg">
              <p className="text-sm text-raw-umber">
                Status: {result.status} | Processed: {result.total_processed} applicants
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {summary && (
        <Card>
          <CardHeader><CardTitle>Triage Results</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div>
                <p className="text-sm text-raw-umber">Total Applicants</p>
                <p className="text-2xl font-bold">{summary.total_applicants}</p>
              </div>
              <div>
                <p className="text-sm text-raw-umber">Avg Confidence</p>
                <p className="text-2xl font-bold">{(summary.avg_confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-raw-umber">Agreement Rate</p>
                <p className="text-2xl font-bold">{(summary.agreement_rate * 100).toFixed(1)}%</p>
              </div>
            </div>
            <TierChart tierCounts={summary.tier_counts} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
