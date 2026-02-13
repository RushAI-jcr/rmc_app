"use client";

import { useState } from "react";
import { FLAG_REASONS } from "@/lib/types";
import { submitDecision } from "@/lib/api";

interface FlagIncorrectProps {
  amcasId: number;
  onComplete: (decision: string) => void;
}

export function FlagIncorrect({ amcasId, onComplete }: FlagIncorrectProps) {
  const [showReasons, setShowReasons] = useState(false);
  const [selectedReason, setSelectedReason] = useState("");
  const [otherText, setOtherText] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = async () => {
    setSaving(true);
    setError(null);
    try {
      await submitDecision(amcasId, "confirm", "");
      onComplete("confirm");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save decision");
      setSaving(false);
    }
  };

  const handleFlag = async () => {
    if (!selectedReason) return;
    setSaving(true);
    setError(null);
    const notes = selectedReason === "Other" ? otherText : "";
    try {
      await submitDecision(amcasId, "flag", notes, selectedReason);
      onComplete("flag");
      setShowReasons(false);
      setSelectedReason("");
      setOtherText("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save flag");
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3">
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      <div className="flex gap-3">
        <button
          onClick={handleConfirm}
          disabled={saving}
          className="px-6 py-2.5 bg-legacy-green text-white rounded-lg text-sm font-semibold hover:bg-growth-green disabled:opacity-50"
        >
          Confirm Score
        </button>
        <button
          onClick={() => setShowReasons(!showReasons)}
          disabled={saving}
          className="px-6 py-2.5 bg-rose text-raw-umber rounded-lg text-sm font-semibold border border-rose hover:bg-rose/80 disabled:opacity-50"
        >
          Flag as Incorrect
        </button>
      </div>

      {showReasons && (
        <div className="border border-rose rounded-lg p-4 bg-rose/20 space-y-3">
          <p className="text-sm font-medium text-raw-umber">Why is this score incorrect?</p>
          <div className="space-y-2">
            {FLAG_REASONS.map((reason) => (
              <label key={reason} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="flag-reason"
                  value={reason}
                  checked={selectedReason === reason}
                  onChange={() => setSelectedReason(reason)}
                  className="text-legacy-green accent-legacy-green"
                />
                <span className="text-sm">{reason}</span>
              </label>
            ))}
          </div>

          {selectedReason === "Other" && (
            <textarea
              value={otherText}
              onChange={(e) => setOtherText(e.target.value)}
              placeholder="Please describe why the score is incorrect..."
              className="w-full border border-gray rounded-lg p-3 text-sm h-20"
            />
          )}

          <button
            onClick={handleFlag}
            disabled={saving || !selectedReason}
            className="px-5 py-2 bg-legacy-green text-white rounded-lg text-sm font-semibold hover:bg-growth-green disabled:opacity-50"
          >
            Submit Flag
          </button>
        </div>
      )}
    </div>
  );
}
