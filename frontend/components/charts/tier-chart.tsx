"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { TIER_COLORS, TIER_LABELS } from "@/lib/types";

interface TierChartProps {
  tierCounts: Record<string, number>;
}

export function TierChart({ tierCounts }: TierChartProps) {
  const data = Object.entries(tierCounts).map(([label, count]) => {
    const tierIdx = Object.values(TIER_LABELS).indexOf(label);
    return {
      name: label,
      count,
      color: TIER_COLORS[tierIdx >= 0 ? tierIdx : 0],
    };
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" fontSize={12} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
