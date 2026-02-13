"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { ShapDriver } from "@/lib/types";

interface ShapChartProps {
  drivers: ShapDriver[];
}

export function ShapChart({ drivers }: ShapChartProps) {
  const data = drivers.map((d) => ({
    name: d.display_name,
    value: d.value,
    color: d.direction === "positive" ? "#10b981" : "#ef4444",
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={90} fontSize={12} />
        <Tooltip />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
