"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { TierChart } from "@/components/charts/tier-chart";
import { getStats } from "@/lib/api";
import type { StatsOverview } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats("A_Structured")
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-rose mb-2">Failed to load dashboard</p>
        <p className="text-sm text-raw-umber">{error}</p>
        <p className="text-sm text-gray-400 mt-2">Make sure the API is running at localhost:8000</p>
      </div>
    );
  }

  if (!stats) {
    return <div className="text-center py-20 text-raw-umber">Loading dashboard...</div>;
  }

  const { summary } = stats;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <p className="text-sm text-raw-umber mb-6">
        AI ranks applicants by mission alignment. Focus your review on Tier 2 (Recommended) and Tier 3 (High Priority) candidates.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader><CardTitle>Total Applicants</CardTitle></CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{summary.total_applicants}</p>
            <p className="text-sm text-raw-umber">2024 test set</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Avg Confidence</CardTitle></CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{(summary.avg_confidence * 100).toFixed(1)}%</p>
            <p className="text-sm text-raw-umber">Model confidence</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Agreement Rate</CardTitle></CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{(summary.agreement_rate * 100).toFixed(1)}%</p>
            <p className="text-sm text-raw-umber">Clf/Reg agreement</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Models Loaded</CardTitle></CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.models_loaded.length}</p>
            <p className="text-sm text-raw-umber">{stats.models_loaded.join(", ")}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader><CardTitle>Tier Distribution</CardTitle></CardHeader>
        <CardContent>
          <TierChart tierCounts={summary.tier_counts} />
        </CardContent>
      </Card>

      {stats.bakeoff.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Model Bakeoff</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Config</th>
                    <th className="text-left py-2 px-3">Model</th>
                    <th className="text-right py-2 px-3">Accuracy</th>
                    <th className="text-right py-2 px-3">F1</th>
                    <th className="text-right py-2 px-3">Kappa</th>
                    <th className="text-right py-2 px-3">MAE</th>
                    <th className="text-right py-2 px-3">R2</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.bakeoff.map((row, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-2 px-3">{row.config}</td>
                      <td className="py-2 px-3">{row.model}</td>
                      <td className="text-right py-2 px-3">{row.accuracy?.toFixed(3) ?? "-"}</td>
                      <td className="text-right py-2 px-3">{row.weighted_f1?.toFixed(3) ?? "-"}</td>
                      <td className="text-right py-2 px-3">{row.cohen_kappa?.toFixed(3) ?? "-"}</td>
                      <td className="text-right py-2 px-3">{row.mae?.toFixed(3) ?? "-"}</td>
                      <td className="text-right py-2 px-3">{row.r2?.toFixed(3) ?? "-"}</td>
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
