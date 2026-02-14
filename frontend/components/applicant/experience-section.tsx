"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { HoursChart } from "@/components/charts/hours-chart";
import type { ExperienceHoursSummary, ExperienceItem, ExperienceFlags } from "@/lib/types";

interface ExperienceSectionProps {
  hours: ExperienceHoursSummary | null;
  items: ExperienceItem[];
  flags: ExperienceFlags | null;
}

const FLAG_LABELS: Record<string, string> = {
  has_direct_patient_care: "Patient Care",
  has_volunteering: "Volunteering",
  has_community_service: "Community Service",
  has_shadowing: "Shadowing",
  has_clinical_experience: "Clinical Experience",
  has_leadership: "Leadership",
  has_research: "Research",
  has_military_service: "Military",
  has_honors: "Honors/Awards",
};

export function ExperienceSection({ hours, items, flags }: ExperienceSectionProps) {
  return (
    <div className="space-y-6">
      {/* Experience Flags */}
      {flags && (
        <Card>
          <CardHeader><CardTitle>Experience Types</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Object.entries(FLAG_LABELS).map(([key, label]) => {
                const active = flags[key as keyof ExperienceFlags];
                return (
                  <Badge
                    key={key}
                    color={active ? "#00A66C" : "#A59F9F"}
                    className={`text-sm px-3 py-1 ${!active ? "opacity-40" : ""}`}
                  >
                    {label}
                  </Badge>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Hours Breakdown Chart */}
      {hours && (
        <Card>
          <CardHeader>
            <CardTitle>Hours Breakdown</CardTitle>
            <p className="text-xs text-raw-umber mt-1">
              Total: {hours.total.toLocaleString()} hrs
              {hours.clinical_total > 0 && ` | Clinical: ${hours.clinical_total.toLocaleString()} hrs`}
              {hours.total_volunteer > 0 && ` | Volunteer: ${hours.total_volunteer.toLocaleString()} hrs`}
            </p>
          </CardHeader>
          <CardContent>
            <HoursChart hours={hours} />
          </CardContent>
        </Card>
      )}

      {/* Individual Experience Items */}
      {items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Experiences ({items.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ExperienceItemsList items={items} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ExperienceItemsList({ items }: { items: ExperienceItem[] }) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const toggle = (idx: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto">
      {items.map((item, idx) => (
        <div
          key={idx}
          className="border border-gray rounded-lg p-3 hover:bg-sage/20 cursor-pointer"
          onClick={() => toggle(idx)}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{item.exp_name || "Unnamed"}</p>
              <p className="text-xs text-raw-umber">{item.exp_type || "Unknown type"}</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {item.hours != null && (
                <span className="text-xs text-raw-umber">{item.hours.toLocaleString()} hrs</span>
              )}
              <span className="text-xs text-wash-gray">{expanded.has(idx) ? "▲" : "▼"}</span>
            </div>
          </div>
          {expanded.has(idx) && item.description && (
            <p className="text-sm text-raw-umber mt-2 whitespace-pre-wrap">{item.description}</p>
          )}
        </div>
      ))}
    </div>
  );
}
