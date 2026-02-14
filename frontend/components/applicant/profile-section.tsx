"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { ApplicantProfile } from "@/lib/types";

const PARENT_ED_LABELS: Record<number, string> = {
  0: "Less than HS",
  1: "HS Graduate",
  2: "Some College",
  3: "Associate's",
  4: "Bachelor's",
  5: "Master's",
  6: "Doctorate",
};

interface ProfileSectionProps {
  profile: ApplicantProfile;
}

export function ProfileSection({ profile }: ProfileSectionProps) {
  const indicators = [
    { label: "First Generation", active: profile.first_generation },
    { label: "Pell Grant", active: profile.pell_grant },
    { label: "Disadvantaged", active: profile.disadvantaged },
    { label: "Fee Assistance", active: profile.fee_assistance },
    { label: "Med Underserved Area", active: profile.childhood_med_underserved },
    { label: "Military Service", active: profile.military_service },
    { label: "Paid Work Before 18", active: profile.paid_employment_bf_18 },
    { label: "Family Contribution", active: profile.contribution_to_family },
    { label: "Employed Undergrad", active: profile.employed_undergrad },
  ];
  const activeIndicators = indicators.filter((i) => i.active);

  return (
    <div className="space-y-6">
      {/* Socioeconomic Indicators */}
      {activeIndicators.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Socioeconomic Indicators</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {activeIndicators.map((ind) => (
                <Badge key={ind.label} color="#694FA0" className="text-sm px-3 py-1">
                  {ind.label}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Demographics & Background */}
      <Card>
        <CardHeader><CardTitle>Demographics & Background</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <InfoCell label="Age" value={profile.age} />
            <InfoCell label="Gender" value={profile.gender} />
            <InfoCell label="Citizenship" value={profile.citizenship} />
            <InfoCell label="Languages" value={profile.num_languages || null} />
            <InfoCell label="Dependents" value={profile.num_dependents || null} />
            <InfoCell label="Siblings" value={profile.num_siblings} />
            <InfoCell
              label="Parent Education"
              value={
                profile.parent_max_education_ordinal != null
                  ? PARENT_ED_LABELS[profile.parent_max_education_ordinal] ?? `Level ${profile.parent_max_education_ordinal}`
                  : null
              }
            />
            {profile.military_service_desc && (
              <InfoCell label="Military Branch" value={profile.military_service_desc} />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Academic Info */}
      <Card>
        <CardHeader><CardTitle>Academic Background</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <InfoCell label="Undergrad School" value={profile.primary_undergrad_school} className="col-span-2 sm:col-span-3" />
            <InfoCell label="Major" value={profile.primary_major} />
            <InfoCell label="Highest Degree" value={profile.highest_degree} />
            <InfoCell label="Schools Attended" value={profile.num_schools} />
            <InfoCell label="Courses" value={profile.num_courses} />
            <InfoCell label="Credit Hours" value={profile.total_credit_hours != null ? profile.total_credit_hours.toFixed(0) : null} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InfoCell({
  label,
  value,
  className,
}: {
  label: string;
  value: string | number | null | undefined;
  className?: string;
}) {
  return (
    <div className={className}>
      <p className="text-xs text-raw-umber">{label}</p>
      <p className="text-sm font-medium">{value ?? <span className="text-wash-gray">&mdash;</span>}</p>
    </div>
  );
}
