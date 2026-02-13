"""Pydantic models for the ingest (upload + pipeline) API."""

from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    cycle_year: int
    files_received: int
    detected_types: dict[str, str]
    status: str


class ValidationIssue(BaseModel):
    severity: str  # "error" | "warning" | "info"
    file_type: str | None = None
    message: str
    detail: str | None = None


class ValidationResult(BaseModel):
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    info: list[str]


class FilePreview(BaseModel):
    filename: str
    detected_type: str | None = None
    row_count: int
    column_count: int
    columns: list[str]
    sample_rows: list[dict]


class PreviewData(BaseModel):
    session_id: str
    cycle_year: int
    status: str
    files: list[FilePreview]
    validation: ValidationResult | None = None
    total_applicants: int | None = None


class SessionSummary(BaseModel):
    id: str
    cycle_year: int
    status: str
    created_at: datetime
    uploaded_by: str | None = None
    applicant_count: int | None = None


class PipelineRunResponse(BaseModel):
    run_id: str
    status: str
