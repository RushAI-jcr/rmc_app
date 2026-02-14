"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { TierChart } from "@/components/charts/tier-chart";
import { getStats, getReviewProgress, getFlagSummary } from "@/lib/api";
import { useUser } from "@/components/auth-guard";
import type { StatsOverview } from "@/lib/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function DashboardPage() {
  const user = useUser();
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [progress, setProgress] = useState<{
    total_in_queue: number;
    reviewed_count: number;
    confirmed_count: number;
    flagged_count: number;
  } | null>(null);
  const [flagSummary, setFlagSummary] = useState<{
    total_flags: number;
    by_reason: Record<string, number>;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats("A_Structured")
      .then(setStats)
      .catch((e) => setError(e.message));
    getReviewProgress()
      .then(setProgress)
      .catch(() => {}); // non-critical
    getFlagSummary()
      .then(setFlagSummary)
      .catch(() => {}); // non-critical
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
  const isAdmin = user?.role === "admin";

  const flagChartData = flagSummary
    ? Object.entries(flagSummary.by_reason).map(([reason, count]) => ({
        reason,
        count,
      }))
    : [];

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

      {/* Review Progress card */}
      {progress && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>
              {isAdmin ? "Review Progress (All Reviewers)" : "Your Review Progress"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6 mb-4">
              <div>
                <p className="text-3xl font-bold">
                  {progress.reviewed_count}
                  <span className="text-lg font-normal text-raw-umber"> / {progress.total_in_queue}</span>
                </p>
                <p className="text-sm text-raw-umber">Applicants reviewed</p>
              </div>
              <div className="flex-1">
                <div className="w-full bg-gray rounded-full h-3">
                  <div
                    className="h-3 rounded-full bg-legacy-green transition-all"
                    style={{
                      width: `${progress.total_in_queue > 0 ? (progress.reviewed_count / progress.total_in_queue) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-8 text-sm">
              <div>
                <p className="text-xl font-bold text-growth-green">{progress.confirmed_count}</p>
                <p className="text-raw-umber">Confirmed</p>
              </div>
              <div>
                <p className="text-xl font-bold text-purple">{progress.flagged_count}</p>
                <p className="text-raw-umber">Flagged</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Flag Summary card */}
      {flagSummary && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>
              {isAdmin ? "Flag Summary (All Reviewers)" : "Your Flag Summary"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {flagChartData.length === 0 ? (
              <p className="text-sm text-raw-umber py-4">No flags submitted yet</p>
            ) : (
              <ResponsiveContainer width="100%" height={Math.max(150, flagChartData.length * 50)}>
                <BarChart
                  data={flagChartData}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <XAxis type="number" />
                  <YAxis dataKey="reason" type="category" width={180} fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#694FA0" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      )}

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
