"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { getFairnessReport } from "@/lib/api";
import type { FairnessRow } from "@/lib/types";

export default function FairnessPage() {
  const [report, setReport] = useState<FairnessRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFairnessReport()
      .then((data) => setReport(data.report))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2">Fairness Audit</h2>
      <p className="text-sm text-raw-umber mb-6">
        The AI does not use gender, age, race, or citizenship in its recommendations. These protected attributes are tracked for post-hoc fairness monitoring only.
      </p>
      {error && <p className="text-rose mb-4">{error}</p>}
      {!report.length && <p className="text-wash-gray">Loading fairness report...</p>}
      {report.length > 0 && renderReport()}
    </div>
  );

  function renderReport() {
    const diData = report
    .filter((r) => r.min_disparate_impact !== null)
    .map((r) => ({
      name: r.attribute,
      value: r.min_disparate_impact!,
      color: r.passes_80pct_rule ? "#00A66C" : "#FDE0DF",
    }));

  const dpdData = report
    .filter((r) => r.demographic_parity_diff !== null)
    .map((r) => ({
      name: r.attribute,
      value: Math.abs(r.demographic_parity_diff!),
      color: Math.abs(r.demographic_parity_diff!) < 0.1 ? "#00A66C" : Math.abs(r.demographic_parity_diff!) < 0.2 ? "#694FA0" : "#FDE0DF",
    }));

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Fairness Monitor</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader><CardTitle>Disparate Impact Ratio</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={diData} layout="vertical" margin={{ left: 120 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 1.1]} />
                <YAxis type="category" dataKey="name" width={110} fontSize={12} />
                <Tooltip />
                <ReferenceLine x={0.8} stroke="#5F5858" strokeDasharray="5 5" label="80% Rule" />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {diData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Demographic Parity Difference</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dpdData} layout="vertical" margin={{ left: 120 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={110} fontSize={12} />
                <Tooltip />
                <ReferenceLine x={0.1} stroke="#5F5858" strokeDasharray="5 5" label="0.1 threshold" />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {dpdData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Detailed Report</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-sage/30">
                  <th className="text-left py-2 px-3">Attribute</th>
                  <th className="text-right py-2 px-3">Groups</th>
                  <th className="text-right py-2 px-3">DI Ratio</th>
                  <th className="text-center py-2 px-3">80% Rule</th>
                  <th className="text-right py-2 px-3">DPD</th>
                  <th className="text-right py-2 px-3">EOD</th>
                  <th className="text-right py-2 px-3">Acc Diff</th>
                </tr>
              </thead>
              <tbody>
                {report.map((row) => (
                  <tr key={row.attribute} className="border-b">
                    <td className="py-2 px-3">{row.attribute}</td>
                    <td className="text-right py-2 px-3">{row.n_groups}</td>
                    <td className="text-right py-2 px-3">{row.min_disparate_impact?.toFixed(3) ?? "-"}</td>
                    <td className="text-center py-2 px-3">
                      {row.passes_80pct_rule !== null ? (
                        row.passes_80pct_rule ? (
                          <span className="text-growth-green font-medium">PASS</span>
                        ) : (
                          <span className="text-rose font-medium">FAIL</span>
                        )
                      ) : "-"}
                    </td>
                    <td className="text-right py-2 px-3">{row.demographic_parity_diff?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3">{row.equalized_odds_diff?.toFixed(3) ?? "-"}</td>
                    <td className="text-right py-2 px-3">{row.accuracy_difference?.toFixed(3) ?? "-"}</td>
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
}
