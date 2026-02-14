"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RubricScorecardView } from "@/components/applicant/rubric-scorecard";
import { FlagIncorrect } from "@/components/applicant/flag-incorrect";
import { ProfileSection } from "@/components/applicant/profile-section";
import { ExperienceSection } from "@/components/applicant/experience-section";
import { EssaySection } from "@/components/applicant/essay-section";
import { ShapChart } from "@/components/charts/shap-chart";
import { getApplicant } from "@/lib/api";
import type { ApplicantDetail } from "@/lib/types";
import { BUCKET_LABELS, TIER_COLORS } from "@/lib/types";

type TabKey = "ai" | "profile" | "experiences" | "essays";

const TABS: { key: TabKey; label: string }[] = [
  { key: "ai", label: "AI Assessment" },
  { key: "profile", label: "Profile" },
  { key: "experiences", label: "Experiences" },
  { key: "essays", label: "Essays" },
];

export default function ScorecardPage() {
  const params = useParams();
  const amcasId = Number(params.id);
  const [detail, setDetail] = useState<ApplicantDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [decided, setDecided] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("ai");

  useEffect(() => {
    getApplicant(amcasId)
      .then(setDetail)
      .catch((e) => setError(e.message));
  }, [amcasId]);

  if (error) return <p className="text-rose">{error}</p>;
  if (!detail) return <p className="text-wash-gray">Loading scorecard...</p>;

  return (
    <div>
      {/* ── Header ── */}
      <div className="flex items-center gap-4 mb-4">
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

      {/* Score summary bar */}
      <div className="flex items-center gap-6 mb-2 text-sm text-raw-umber">
        <span>
          Score: <strong className="text-lg">{detail.predicted_score.toFixed(1)}</strong>/25
        </span>
        <span>
          Confidence: <strong className="text-lg">{(detail.confidence * 100).toFixed(0)}%</strong>
        </span>
        {detail.actual_score !== null && (
          <span>
            Reviewer: <strong>{detail.actual_score.toFixed(1)}</strong>/25
          </span>
        )}
        <span className={detail.clf_reg_agree ? "text-growth-green" : "text-purple"}>
          {detail.clf_reg_agree ? "Models agree" : "Models disagree"}
        </span>
      </div>

      {/* Score gauge */}
      <div className="mb-6">
        <div className="relative h-4 bg-gray rounded-full overflow-hidden">
          <div className="absolute h-full" style={{ width: "25%", backgroundColor: "#A59F9F" }} />
          <div className="absolute h-full" style={{ left: "25%", width: "25%", backgroundColor: "#694FA0" }} />
          <div className="absolute h-full" style={{ left: "50%", width: "25%", backgroundColor: "#00A66C" }} />
          <div className="absolute h-full" style={{ left: "75%", width: "25%", backgroundColor: "#54ADD3" }} />
          <div
            className="absolute top-0 h-full w-1 bg-black"
            style={{ left: `${(detail.predicted_score / 25) * 100}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-wash-gray mt-1">
          <span>Will Not Interview</span>
          <span>Committee</span>
          <span>Strong</span>
          <span>Priority</span>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-1 mb-6 border-b border-gray">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.key
                ? "bg-white border border-gray border-b-white text-purple -mb-px"
                : "text-raw-umber hover:text-purple hover:bg-sage/20"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Tab Content ── */}
      <div className="mb-6">
        {activeTab === "ai" && <AiAssessmentTab detail={detail} />}
        {activeTab === "profile" && (
          detail.profile
            ? <ProfileSection profile={detail.profile} />
            : <EmptyState message="No profile data available." />
        )}
        {activeTab === "experiences" && (
          <ExperienceSection
            hours={detail.experience_hours}
            items={detail.experience_items}
            flags={detail.experience_flags}
          />
        )}
        {activeTab === "essays" && (
          <EssaySection
            personalStatement={detail.personal_statement}
            secondaryEssays={detail.secondary_essays}
          />
        )}
      </div>

      {/* ── Review Footer ── */}
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

/* ── AI Assessment Tab ── */
function AiAssessmentTab({ detail }: { detail: ApplicantDetail }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left: SHAP + Class Probabilities */}
      <div className="space-y-6">
        {detail.shap_drivers.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Score Drivers</CardTitle></CardHeader>
            <CardContent>
              <p className="text-xs text-raw-umber mb-3">
                Top features influencing this applicant&apos;s predicted score
              </p>
              <ShapChart drivers={detail.shap_drivers} />
            </CardContent>
          </Card>
        )}

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

        {detail.shap_drivers.length === 0 && detail.class_probabilities.length === 0 && (
          <EmptyState message="SHAP analysis not available for this applicant (only computed for test-set applicants)." />
        )}
      </div>

      {/* Right: Rubric Scorecard */}
      <div>
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
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <Card>
      <CardContent>
        <p className="text-sm text-wash-gray italic py-4">{message}</p>
      </CardContent>
    </Card>
  );
}
