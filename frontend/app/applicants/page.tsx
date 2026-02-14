"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { getApplicants } from "@/lib/api";
import type { ApplicantSummary } from "@/lib/types";

export default function ApplicantsPage() {
  const router = useRouter();
  const [applicants, setApplicants] = useState<ApplicantSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [tierFilter, setTierFilter] = useState<number | undefined>(undefined);
  const [showAllTiers, setShowAllTiers] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getApplicants({ page, search: search || undefined, tier: tierFilter, page_size: 50 })
      .then((data) => {
        let results = data.results;
        // Default: only show Tier 2+3 unless "Show all tiers" is on or a specific tier is selected
        if (!showAllTiers && tierFilter === undefined) {
          results = results.filter((a) => a.tier >= 2);
        }
        setApplicants(results);
        setTotal(showAllTiers || tierFilter !== undefined ? data.total : results.length);
      })
      .catch((e) => setError(e.message));
  }, [page, search, tierFilter, showAllTiers]);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2">Applicant Review</h2>
      {!showAllTiers && tierFilter === undefined && (
        <p className="text-sm text-raw-umber mb-4">
          Showing Tier 2 (Recommended for Review) and Tier 3 (High Priority) only.
          AI has narrowed {total} applicants to the strongest mission-aligned candidates for your expert review.
        </p>
      )}

      <div className="flex gap-4 mb-4 flex-wrap items-center">
        <input
          type="text"
          placeholder="Search AMCAS ID..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="border border-gray rounded-lg px-3 py-2 text-sm w-64"
        />

        {showAllTiers && (
          <select
            value={tierFilter ?? ""}
            onChange={(e) => { setTierFilter(e.target.value ? Number(e.target.value) : undefined); setPage(1); }}
            className="border border-gray rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All Tiers</option>
            <option value="3">Tier 3: Priority Interview</option>
            <option value="2">Tier 2: Strong Candidate</option>
            <option value="1">Tier 1: Committee Review</option>
            <option value="0">Tier 0: Will Not Likely Interview</option>
          </select>
        )}

        <span className="text-sm text-raw-umber">{total} applicants</span>

        <label className="flex items-center gap-2 ml-auto cursor-pointer text-sm text-raw-umber">
          <input
            type="checkbox"
            checked={showAllTiers}
            onChange={(e) => { setShowAllTiers(e.target.checked); setTierFilter(undefined); setPage(1); }}
            className="rounded accent-legacy-green"
          />
          Show all tiers
        </label>
      </div>

      {error && <p className="text-rose mb-4">{error}</p>}

      <div className="bg-white rounded-lg border border-gray shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-sage/30">
              <th className="text-left py-3 px-4">Rank</th>
              <th className="text-left py-3 px-4">AMCAS ID</th>
              <th className="text-left py-3 px-4">Tier</th>
              <th className="text-right py-3 px-4">Score</th>
              <th className="text-right py-3 px-4">Confidence</th>
              <th className="text-center py-3 px-4">Agreement</th>
            </tr>
          </thead>
          <tbody>
            {applicants.map((a) => (
              <tr
                key={a.amcas_id}
                className="border-b hover:bg-sage/10 cursor-pointer"
                onClick={() => router.push(`/applicants/${a.amcas_id}`)}
              >
                <td className="py-3 px-4">{a.rank}</td>
                <td className="py-3 px-4 font-mono">{a.amcas_id}</td>
                <td className="py-3 px-4">
                  <Badge color={a.tier_color}>{a.tier_label}</Badge>
                </td>
                <td className="text-right py-3 px-4">{a.predicted_score.toFixed(1)}</td>
                <td className="text-right py-3 px-4">{(a.confidence * 100).toFixed(0)}%</td>
                <td className="text-center py-3 px-4">
                  {a.clf_reg_agree ? (
                    <span className="text-growth-green">Yes</span>
                  ) : (
                    <span className="text-purple">No</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          Previous
        </button>
        <span className="text-sm text-raw-umber">Page {page}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={applicants.length < 50}
          className="px-4 py-2 border border-gray rounded-lg text-sm disabled:opacity-50 hover:bg-sage/10"
        >
          Next
        </button>
      </div>
    </div>
  );
}
