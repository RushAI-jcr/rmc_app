"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { EssaySection as EssaySectionType } from "@/lib/types";

interface EssaySectionProps {
  personalStatement: string | null;
  secondaryEssays: EssaySectionType[];
}

export function EssaySection({ personalStatement, secondaryEssays }: EssaySectionProps) {
  if (!personalStatement && secondaryEssays.length === 0) {
    return (
      <Card>
        <CardContent>
          <p className="text-sm text-wash-gray italic">No essay data available for this applicant.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Personal Statement */}
      {personalStatement && (
        <Card>
          <CardHeader><CardTitle>Personal Statement</CardTitle></CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-raw-umber">
                {personalStatement}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Secondary Essays */}
      {secondaryEssays.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Secondary Essays</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {secondaryEssays.map((essay, idx) => (
                <EssayCard key={idx} essay={essay} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function EssayCard({ essay }: { essay: EssaySectionType }) {
  const [expanded, setExpanded] = useState(false);
  const isLong = essay.text.length > 500;
  const displayText = isLong && !expanded ? essay.text.slice(0, 500) + "..." : essay.text;

  return (
    <div className="border border-gray rounded-lg p-4">
      <h4 className="text-sm font-semibold text-raw-umber mb-2">{essay.prompt_name}</h4>
      <p className="text-sm leading-relaxed whitespace-pre-wrap text-raw-umber">{displayText}</p>
      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-purple font-medium mt-2 hover:underline"
        >
          {expanded ? "Show less" : "Read more"}
        </button>
      )}
    </div>
  );
}
