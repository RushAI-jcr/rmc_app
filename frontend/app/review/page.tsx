"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FlagIncorrect } from "@/components/applicant/flag-incorrect";
import { getReviewQueue } from "@/lib/api";
import type { ReviewQueueItem } from "@/lib/types";
import { TIER_COLORS } from "@/lib/types";

export default function ReviewPage() {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReviewQueue()
      .then(setQueue)
      .catch((e) => setError(e.message));
  }, []);

  const current = queue[currentIdx];
  const reviewed = queue.filter((q) => q.decision !== null).length;

  const handleComplete = (decision: string) => {
    const updated = [...queue];
    updated[currentIdx] = { ...current, decision };
    setQueue(updated);
    // Auto-advance to next unreviewed
    if (currentIdx < queue.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  };

  if (error) return <p className="text-rose">{error}</p>;
  if (!queue.length) return <p className="text-wash-gray">Loading review queue...</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Guided Review</h2>
          <p className="text-sm text-raw-umber mt-1">
            AI has identified {queue.length} high-priority candidates (Tier 2 & 3).
            Your expert review confirms or adjusts each recommendation before interview invitations.
          </p>
        </div>
        <span className="text-sm text-raw-umber">
          {reviewed} of {queue.length} reviewed | Viewing {currentIdx + 1} of {queue.length}
        </span>
      </div>

      {current && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                <a href={`/applicants/${current.amcas_id}`} className="hover:underline">
                  Applicant {current.amcas_id}
                </a>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge color={TIER_COLORS[current.tier]}>{current.tier_label}</Badge>
                {current.priority_reason !== "Standard review" && (
                  <span className="text-xs bg-purple/20 text-purple px-2 py-0.5 rounded font-medium">
                    {current.priority_reason}
                  </span>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div>
                <p className="text-sm text-raw-umber">AI Score</p>
                <p className="text-xl font-bold">{current.predicted_score.toFixed(1)}/25</p>
              </div>
              <div>
                <p className="text-sm text-raw-umber">Confidence</p>
                <p className="text-xl font-bold">{(current.confidence * 100).toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-sm text-raw-umber">Model Agreement</p>
                <p className={`text-xl font-bold ${current.clf_reg_agree ? "text-growth-green" : "text-purple"}`}>
                  {current.clf_reg_agree ? "Yes" : "No"}
                </p>
              </div>
            </div>

            {current.decision && (
              <div className={`mb-4 p-3 rounded-lg ${current.decision === "confirm" ? "bg-sage" : "bg-rose/30"}`}>
                <p className={`text-sm ${current.decision === "confirm" ? "text-raw-umber" : "text-raw-umber"}`}>
                  {current.decision === "confirm" ? "Score confirmed" : `Flagged: ${current.flag_reason || "\u2014"}`}
                </p>
              </div>
            )}

            {!current.decision && (
              <FlagIncorrect amcasId={current.amcas_id} onComplete={handleComplete} />
            )}
          </CardContent>
        </Card>
      )}

      <div className="flex justify-between">
        <button
          onClick={() => setCurrentIdx((i) => Math.max(0, i - 1))}
          disabled={currentIdx === 0}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          Previous
        </button>
        <button
          onClick={() => setCurrentIdx((i) => Math.min(queue.length - 1, i + 1))}
          disabled={currentIdx >= queue.length - 1}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          Next
        </button>
      </div>
    </div>
  );
}
