"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getStats } from "@/lib/api";
import type { BakeoffRow } from "@/lib/types";

export default function ComparePage() {
  const [bakeoff, setBakeoff] = useState<BakeoffRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats("A_Structured")
      .then((data) => setBakeoff(data.bakeoff))
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="text-rose">{error}</p>;
  if (!bakeoff.length) return <p className="text-wash-gray">Loading comparison...</p>;

  const classifiers = bakeoff.filter((r) => r.model.startsWith("clf_"));
  const regressors = bakeoff.filter((r) => r.model.startsWith("reg_"));

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Model Comparison</h2>

      <Card className="mb-8">
        <CardHeader><CardTitle>Classification Models (4-Bucket)</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">Config</th>
                  <th className="text-left py-2 px-3">Model</th>
                  <th className="text-right py-2 px-3">Accuracy</th>
                  <th className="text-right py-2 px-3">Weighted F1</th>
                  <th className="text-right py-2 px-3">Cohen&apos;s Kappa</th>
                </tr>
              </thead>
              <tbody>
                {classifiers.map((row, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2 px-3">{row.config}</td>
                    <td className="py-2 px-3">{row.model.replace("clf_", "")}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.accuracy?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.weighted_f1?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.cohen_kappa?.toFixed(3) ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Regression Models (0-25 Score)</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">Config</th>
                  <th className="text-left py-2 px-3">Model</th>
                  <th className="text-right py-2 px-3">MAE</th>
                  <th className="text-right py-2 px-3">R2</th>
                  <th className="text-right py-2 px-3">RMSE</th>
                </tr>
              </thead>
              <tbody>
                {regressors.map((row, i) => (
                  <tr key={i} className="border-b">
                    <td className="py-2 px-3">{row.config}</td>
                    <td className="py-2 px-3">{row.model.replace("reg_", "")}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.mae?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.r2?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3 font-mono">{row.rmse?.toFixed(3) ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
