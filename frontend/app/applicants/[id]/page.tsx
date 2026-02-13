"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RubricScorecardView } from "@/components/applicant/rubric-scorecard";
import { FlagIncorrect } from "@/components/applicant/flag-incorrect";
import { getApplicant } from "@/lib/api";
import type { ApplicantDetail } from "@/lib/types";
import { BUCKET_LABELS, TIER_COLORS } from "@/lib/types";

export default function ScorecardPage() {
  const params = useParams();
  const amcasId = Number(params.id);
  const [detail, setDetail] = useState<ApplicantDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [decided, setDecided] = useState<string | null>(null);

  useEffect(() => {
    getApplicant(amcasId)
      .then(setDetail)
      .catch((e) => setError(e.message));
  }, [amcasId]);

  if (error) return <p className="text-rose">{error}</p>;
  if (!detail) return <p className="text-wash-gray">Loading scorecard...</p>;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <h2 className="text-2xl font-bold">Applicant {detail.amcas_id}</h2>
        <Badge color={detail.tier_color} className="text-base px-3 py-1">
          {detail.tier_label}
        </Badge>
        {detail.flag && (
          <span className="text-sm bg-rose text-raw-umber px-2 py-1 rounded">
            Flagged: {detail.flag.reason}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left column: Score summary + gauge */}
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Score Summary</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-raw-umber">AI Score</p>
                  <p className="text-3xl font-bold">
                    {detail.predicted_score.toFixed(1)}
                    <span className="text-lg text-wash-gray">/25</span>
                  </p>
                </div>
                <div>
                  <p className="text-sm text-raw-umber">Confidence</p>
                  <p className="text-3xl font-bold">{(detail.confidence * 100).toFixed(0)}%</p>
                </div>
                {detail.actual_score !== null && (
                  <div>
                    <p className="text-sm text-raw-umber">Reviewer Score</p>
                    <p className="text-lg font-medium">{detail.actual_score.toFixed(1)}/25</p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-raw-umber">Model Agreement</p>
                  <p className={`text-lg font-medium ${detail.clf_reg_agree ? "text-growth-green" : "text-purple"}`}>
                    {detail.clf_reg_agree ? "Models agree" : "Models disagree"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Score gauge */}
          <Card>
            <CardHeader><CardTitle>Score Position</CardTitle></CardHeader>
            <CardContent>
              <div className="relative h-6 bg-gray rounded-full overflow-hidden">
                <div className="absolute h-full" style={{ width: "25%", backgroundColor: "#A59F9F" }} />
                <div className="absolute h-full" style={{ left: "25%", width: "25%", backgroundColor: "#694FA0" }} />
                <div className="absolute h-full" style={{ left: "50%", width: "25%", backgroundColor: "#00A66C" }} />
                <div className="absolute h-full" style={{ left: "75%", width: "25%", backgroundColor: "#54ADD3" }} />
                <div
                  className="absolute top-0 h-full w-1 bg-black"
                  style={{ left: `${(detail.predicted_score / 25) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-raw-umber mt-1">
                <span>0</span>
                <span>6.25</span>
                <span>12.5</span>
                <span>18.75</span>
                <span>25</span>
              </div>
              <div className="flex justify-between text-xs text-wash-gray mt-0.5">
                <span>Will Not Interview</span>
                <span>Committee</span>
                <span>Strong</span>
                <span>Priority</span>
                <span></span>
              </div>
            </CardContent>
          </Card>

          {/* Class probabilities */}
          {detail.class_probabilities.length > 0 && (
            <Card>
              <CardHeader><CardTitle>Classification Confidence</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {detail.class_probabilities.map((prob, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{BUCKET_LABELS[i]}</span>
                        <span>{(prob * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray rounded-full h-3">
                        <div
                          className="h-3 rounded-full"
                          style={{
                            width: `${prob * 100}%`,
                            backgroundColor: TIER_COLORS[i],
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right column: Rubric scorecard */}
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Rubric Scorecard</CardTitle></CardHeader>
            <CardContent>
              {detail.rubric_scorecard ? (
                <RubricScorecardView scorecard={detail.rubric_scorecard} />
              ) : (
                <p className="text-sm text-wash-gray italic">No rubric data available.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Feedback section */}
      <Card>
        <CardHeader><CardTitle>Review Feedback</CardTitle></CardHeader>
        <CardContent>
          {decided ? (
            <div className={`p-3 rounded-lg ${decided === "confirm" ? "bg-sage text-raw-umber" : "bg-rose/30 text-raw-umber"}`}>
              <p className="text-sm font-medium">
                {decided === "confirm" ? "Score confirmed." : "Flagged as incorrect. Thank you for your feedback."}
              </p>
            </div>
          ) : (
            <FlagIncorrect amcasId={detail.amcas_id} onComplete={setDecided} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
