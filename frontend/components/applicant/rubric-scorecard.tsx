"use client";

import type { RubricScorecard } from "@/lib/types";

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
              <div key={dim.name} className="flex items-center justify-between">
                <span className="text-sm text-raw-umber flex-1">{dim.name}</span>
                <ScoreBar score={dim.score} maxScore={dim.max_score} />
              </div>
            ))}
          </div>
        </div>
      ))}
      <p className="text-xs text-wash-gray mt-2">Scale: 1-5 (&mdash; = not scored)</p>
    </div>
  );
}
