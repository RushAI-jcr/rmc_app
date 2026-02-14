"use client";

import { useState } from "react";
import type { RubricScorecard, RubricDimension } from "@/lib/types";

function ScoreBar({ score, maxScore }: { score: number; maxScore: number }) {
  const pct = maxScore > 0 ? (score / maxScore) * 100 : 0;
  const color =
    score === 0
      ? "#EAEAEA"
      : score >= 4
        ? "#00A66C"
        : score >= 3
          ? "#694FA0"
          : "#A59F9F";

  return (
    <div className="flex items-center gap-2">
      <div className="w-32 bg-gray rounded-full h-2.5">
        <div
          className="h-2.5 rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-sm font-medium w-8 text-right">
        {score > 0 ? score.toFixed(0) : "\u2014"}
      </span>
    </div>
  );
}

function DimensionRow({ dim }: { dim: RubricDimension }) {
  const [expanded, setExpanded] = useState(false);
  const hasDetail = dim.detail && (dim.detail.evidence_extracted || dim.detail.reasoning);

  return (
    <div>
      <div
        className={`flex items-center justify-between ${hasDetail ? "cursor-pointer hover:bg-sage/20 -mx-1 px-1 rounded" : ""}`}
        onClick={() => hasDetail && setExpanded(!expanded)}
      >
        <span className="text-sm text-raw-umber flex-1 flex items-center gap-1">
          {dim.name}
          {hasDetail && (
            <span className="text-xs text-wash-gray">{expanded ? "▲" : "▼"}</span>
          )}
        </span>
        <ScoreBar score={dim.score} maxScore={dim.max_score} />
      </div>
      {expanded && dim.detail && (
        <div className="ml-2 mt-1.5 mb-2 pl-3 border-l-2 border-sage space-y-1.5">
          {dim.detail.evidence_extracted && (
            <blockquote className="text-xs text-raw-umber italic bg-sage/20 rounded p-2 leading-relaxed">
              {dim.detail.evidence_extracted.length > 400
                ? dim.detail.evidence_extracted.slice(0, 400) + "..."
                : dim.detail.evidence_extracted}
            </blockquote>
          )}
          {dim.detail.reasoning && (
            <p className="text-xs text-wash-gray leading-relaxed">{dim.detail.reasoning}</p>
          )}
        </div>
      )}
    </div>
  );
}

export function RubricScorecardView({ scorecard }: { scorecard: RubricScorecard }) {
  if (!scorecard.has_rubric) {
    return (
      <p className="text-sm text-wash-gray italic">No rubric scores available for this applicant.</p>
    );
  }

  return (
    <div className="space-y-5">
      {scorecard.groups.map((group) => (
        <div key={group.label}>
          <h4 className="text-sm font-semibold text-raw-umber mb-2">{group.label}</h4>
          <div className="space-y-1.5">
            {group.dimensions.map((dim) => (
              <DimensionRow key={dim.name} dim={dim} />
            ))}
          </div>
        </div>
      ))}
      <p className="text-xs text-wash-gray mt-2">Scale: 1&ndash;4 (&mdash; = not scored)</p>
    </div>
  );
}
