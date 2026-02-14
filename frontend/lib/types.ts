export interface ApplicantSummary {
  amcas_id: number;
  rank: number | null;
  tier: number;
  tier_label: string;
  tier_color: string;
  predicted_score: number;
  predicted_bucket: number;
  confidence: number;
  clf_reg_agree: boolean;
  app_year: number | null;
}

export interface ShapDriver {
  feature: string;
  display_name: string;
  value: number;
  direction: "positive" | "negative";
}

export interface RubricDimension {
  name: string;
  score: number;
  max_score: number;
}

export interface RubricGroup {
  label: string;
  dimensions: RubricDimension[];
}

export interface RubricScorecard {
  groups: RubricGroup[];
  has_rubric: boolean;
}

export interface FlagInfo {
  reason: string;
  notes: string;
  flagged_at: string | null;
}

export interface ApplicantDetail {
  amcas_id: number;
  tier: number;
  tier_label: string;
  tier_color: string;
  predicted_score: number;
  predicted_bucket: number;
  confidence: number;
  clf_reg_agree: boolean;
  actual_score: number | null;
  actual_bucket: number | null;
  class_probabilities: number[];
  shap_drivers: ShapDriver[];
  rubric_scorecard: RubricScorecard | null;
  app_year: number | null;
  flag: FlagInfo | null;
}

export interface TriageSummary {
  total_applicants: number;
  tier_counts: Record<string, number>;
  avg_confidence: number;
  agreement_rate: number;
  config_name: string;
}

export interface ReviewQueueItem {
  amcas_id: number;
  tier: number;
  tier_label: string;
  predicted_score: number;
  confidence: number;
  clf_reg_agree: boolean;
  priority_reason: string;
  decision: string | null;
  notes: string | null;
  flag_reason: string | null;
  reviewer_username: string | null;
}

export interface StatsOverview {
  summary: TriageSummary;
  total_applicants_all_years: number;
  test_applicants: number;
  models_loaded: string[];
  bakeoff: BakeoffRow[];
}

export interface BakeoffRow {
  config: string;
  model: string;
  accuracy?: number;
  weighted_f1?: number;
  cohen_kappa?: number;
  mae?: number;
  r2?: number;
  rmse?: number;
}

export interface FairnessRow {
  attribute: string;
  n_groups: number;
  min_disparate_impact: number | null;
  passes_80pct_rule: boolean | null;
  demographic_parity_diff: number | null;
  equalized_odds_diff: number | null;
  accuracy_difference: number | null;
  accuracy_ratio: number | null;
}

export const TIER_COLORS: Record<number, string> = {
  0: "#A59F9F",
  1: "#694FA0",
  2: "#00A66C",
  3: "#54ADD3",
};

export const TIER_LABELS: Record<number, string> = {
  0: "Will Not Likely Interview",
  1: "Committee Review",
  2: "Strong Candidate",
  3: "Priority Interview",
};

export const BUCKET_LABELS = ["Lacking", "Adequate", "Significant", "Exceptional"];

export const FLAG_REASONS = [
  "Undervalued volunteer/community work",
  "Undervalued clinical experience",
  "Missed grit/adversity indicators",
  "Overvalued — application weaker than score suggests",
  "Other",
];

// -- Ingestion types --

export interface UploadResponse {
  session_id: string;
  cycle_year: number;
  files_received: number;
  detected_types: Record<string, string>;
  status: string;
}

export interface ValidationIssue {
  severity: "error" | "warning" | "info";
  file_type: string | null;
  message: string;
  detail: string | null;
}

export interface ValidationResult {
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  info: string[];
}

export interface FilePreview {
  filename: string;
  detected_type: string | null;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_rows: Record<string, unknown>[];
}

export interface PreviewData {
  session_id: string;
  cycle_year: number;
  status: string;
  files: FilePreview[];
  validation: ValidationResult | null;
  total_applicants: number | null;
}

export interface SessionSummary {
  id: string;
  cycle_year: number;
  status: string;
  created_at: string;
  uploaded_by: string | null;
  applicant_count: number | null;
}

export interface PipelineRunResponse {
  run_id: string;
  status: string;
}

export interface PipelineRunStatus {
  id: string;
  upload_session_id: string;
  status: "pending" | "running" | "complete" | "failed";
  current_step: string | null;
  progress_pct: number;
  started_at: string | null;
  completed_at: string | null;
  result_summary: Record<string, unknown> | null;
  error_log: string | null;
}

export interface UserInfo {
  id: string;
  username: string;
  role: string;
}

export const AMCAS_FILE_TYPES = [
  "applicants",
  "experiences",
  "personal_statement",
  "secondary_application",
  "gpa_trend",
  "language",
  "parents",
  "schools_2024",
  "schools_2022_2023",
  "military",
  "siblings",
  "academic_records",
] as const;

export type AmcasFileType = (typeof AMCAS_FILE_TYPES)[number];

export const REQUIRED_FILE_TYPES: AmcasFileType[] = ["applicants", "experiences"];

export const SESSION_STATUS_COLORS: Record<string, string> = {
  uploaded: "#54ADD3",
  validated: "#00A66C",
  approved: "#694FA0",
  processing: "#694FA0",
  complete: "#5FEEA2",
  failed: "#FDE0DF",
};
