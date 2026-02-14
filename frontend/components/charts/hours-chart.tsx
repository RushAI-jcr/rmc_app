"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { ExperienceHoursSummary } from "@/lib/types";

const COLORS = [
  "#694FA0", // purple
  "#00A66C", // growth-green
  "#7FA886", // sage
  "#5FEEA2", // legacy-green
  "#54ADD3", // blue
  "#A59F9F", // gray
  "#E8B4B0", // rose
  "#C4A040", // amber
];

interface HoursChartProps {
  hours: ExperienceHoursSummary;
}

export function HoursChart({ hours }: HoursChartProps) {
  const data = [
    { name: "Research", value: hours.research },
    { name: "Med Volunteer", value: hours.volunteer_med },
    { name: "Non-Med Volunteer", value: hours.volunteer_non_med },
    { name: "Med Employment", value: hours.employ_med },
    { name: "Shadowing", value: hours.shadowing },
    { name: "Community Svc", value: hours.community_service },
    { name: "Healthcare", value: hours.healthcare },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return <p className="text-sm text-wash-gray italic">No experience hours recorded.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(160, data.length * 32)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 110, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={100} fontSize={12} />
        <Tooltip formatter={(v) => [`${Number(v).toLocaleString()} hrs`, "Hours"]} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
