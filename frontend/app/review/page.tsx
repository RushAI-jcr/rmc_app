"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FlagIncorrect } from "@/components/applicant/flag-incorrect";
import { RubricScorecardView } from "@/components/applicant/rubric-scorecard";
import { getReviewQueue, getNextUnreviewed, getReviewDetail } from "@/lib/api";
import type { ReviewQueueItem, RubricScorecard } from "@/lib/types";
import { TIER_COLORS } from "@/lib/types";

export default function ReviewPage() {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [rubric, setRubric] = useState<RubricScorecard | null>(null);
  const [rubricLoading, setRubricLoading] = useState(false);
  const [changingDecision, setChangingDecision] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Load queue and auto-resume to first unreviewed
  useEffect(() => {
    Promise.all([getReviewQueue(), getNextUnreviewed()])
      .then(([q, next]) => {
        setQueue(q);
        if (next) {
          const idx = q.findIndex((item) => item.amcas_id === next.amcas_id);
          if (idx >= 0) setCurrentIdx(idx);
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  const current = queue[currentIdx];
  const reviewed = queue.filter((q) => q.decision !== null).length;
  const allDone = queue.length > 0 && reviewed === queue.length;

  // Fetch rubric scorecard when current applicant changes
  useEffect(() => {
    if (!current) return;
    setRubric(null);
    setRubricLoading(true);
    setChangingDecision(false);
    getReviewDetail(current.amcas_id)
      .then((data) => setRubric(data.rubric_scorecard ?? null))
      .catch(() => setRubric(null))
      .finally(() => setRubricLoading(false));
  }, [current?.amcas_id]); // eslint-disable-line react-hooks/exhaustive-deps

  const goTo = useCallback(
    (idx: number) => setCurrentIdx(Math.max(0, Math.min(queue.length - 1, idx))),
    [queue.length],
  );

  const advanceToNextUnreviewed = useCallback(() => {
    // Find next unreviewed after current
    for (let i = currentIdx + 1; i < queue.length; i++) {
      if (queue[i].decision === null) {
        setCurrentIdx(i);
        return;
      }
    }
    // Wrap around from beginning
    for (let i = 0; i < currentIdx; i++) {
      if (queue[i].decision === null) {
        setCurrentIdx(i);
        return;
      }
    }
    // All reviewed — stay on current
    if (currentIdx < queue.length - 1) {
      setCurrentIdx(currentIdx + 1);
    }
  }, [currentIdx, queue]);

  const handleComplete = useCallback(
    (decision: string) => {
      const updated = [...queue];
      updated[currentIdx] = { ...queue[currentIdx], decision };
      setQueue(updated);
      setChangingDecision(false);
      // Auto-advance to next unreviewed
      const nextUnreviewed = updated.findIndex(
        (item, i) => i > currentIdx && item.decision === null,
      );
      if (nextUnreviewed >= 0) {
        setCurrentIdx(nextUnreviewed);
      } else {
        // Check from beginning
        const wrapped = updated.findIndex((item) => item.decision === null);
        if (wrapped >= 0) {
          setCurrentIdx(wrapped);
        }
      }
    },
    [currentIdx, queue],
  );

  // Keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Don't intercept if user is typing in an input/textarea
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      switch (e.key) {
        case "ArrowLeft":
        case "k":
          e.preventDefault();
          goTo(currentIdx - 1);
          break;
        case "ArrowRight":
        case "j":
          e.preventDefault();
          goTo(currentIdx + 1);
          break;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIdx, goTo]);

  if (error) return <p className="text-rose">{error}</p>;
  if (!queue.length) return <p className="text-wash-gray">Loading review queue...</p>;

  // Completion state
  if (allDone) {
    const flagged = queue.filter((q) => q.decision === "flag").length;
    const confirmed = queue.filter((q) => q.decision === "confirm").length;
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">Guided Review</h2>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-4xl mb-4">&#10003;</div>
            <h3 className="text-xl font-bold mb-2">Review Complete</h3>
            <p className="text-raw-umber mb-6">
              All {queue.length} candidates have been reviewed.
            </p>
            <div className="flex justify-center gap-8 text-sm">
              <div>
                <p className="text-2xl font-bold text-growth-green">{confirmed}</p>
                <p className="text-raw-umber">Confirmed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple">{flagged}</p>
                <p className="text-raw-umber">Flagged</p>
              </div>
            </div>
            <button
              onClick={() => setCurrentIdx(0)}
              className="mt-8 px-4 py-2 border border-gray rounded-lg text-sm hover:bg-sage/10"
            >
              Browse All Decisions
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div ref={containerRef}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Guided Review</h2>
          <p className="text-sm text-raw-umber mt-1">
            Review {queue.length} high-priority candidates. Your expert judgment confirms or adjusts each AI recommendation.
          </p>
        </div>
        <div className="text-right">
          <span className="text-sm text-raw-umber">
            {reviewed} of {queue.length} reviewed
          </span>
          {/* Progress bar */}
          <div className="w-40 bg-gray rounded-full h-2 mt-1">
            <div
              className="h-2 rounded-full bg-legacy-green transition-all"
              style={{ width: `${(reviewed / queue.length) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {current && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-xs text-wash-gray">{currentIdx + 1}/{queue.length}</span>
                <CardTitle>
                  <a href={`/applicants/${current.amcas_id}`} className="hover:underline">
                    Applicant {current.amcas_id}
                  </a>
                </CardTitle>
              </div>
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

            {/* Inline rubric scorecard */}
            {rubricLoading && (
              <p className="text-sm text-wash-gray mb-4">Loading rubric...</p>
            )}
            {!rubricLoading && rubric && (
              <div className="mb-6 border border-gray rounded-lg p-4">
                <h4 className="text-sm font-semibold text-raw-umber mb-3">Rubric Scorecard</h4>
                <RubricScorecardView scorecard={rubric} />
              </div>
            )}

            {/* Decision state: already reviewed */}
            {current.decision && !changingDecision && (
              <div className={`mb-4 p-3 rounded-lg flex items-center justify-between ${current.decision === "confirm" ? "bg-sage" : "bg-rose/30"}`}>
                <div>
                  <p className="text-sm text-raw-umber">
                    {current.decision === "confirm" ? "Score confirmed" : `Flagged: ${current.flag_reason || "\u2014"}`}
                  </p>
                  {current.reviewer_username && (
                    <p className="text-xs text-wash-gray mt-0.5">
                      Reviewed by {current.reviewer_username}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setChangingDecision(true)}
                  className="text-xs text-purple hover:underline"
                >
                  Change decision
                </button>
              </div>
            )}

            {/* Decision input: unreviewed or changing */}
            {(!current.decision || changingDecision) && (
              <FlagIncorrect amcasId={current.amcas_id} onComplete={handleComplete} />
            )}
          </CardContent>
        </Card>
      )}

      <div className="flex items-center justify-between">
        <button
          onClick={() => goTo(currentIdx - 1)}
          disabled={currentIdx === 0}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          &larr; Previous
        </button>
        <p className="text-xs text-wash-gray">
          Arrow keys or J/K to navigate
        </p>
        <button
          onClick={() => goTo(currentIdx + 1)}
          disabled={currentIdx >= queue.length - 1}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          Next &rarr;
        </button>
      </div>
    </div>
  );
}
