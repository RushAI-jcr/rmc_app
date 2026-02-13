"""Triage endpoints: run pipeline and get summary."""

from fastapi import APIRouter, Request

from api.models.triage import TriageRunRequest, TriageRunResponse, TriageSummary
from api.services.triage_service import run_triage, get_triage_summary

router = APIRouter(prefix="/api/triage", tags=["triage"])


@router.post("/run")
def run_triage_endpoint(request: Request, body: TriageRunRequest) -> TriageRunResponse:
    """Run triage on the test set."""
    store = request.app.state.store
    result = run_triage(body.config_name, store)
    return TriageRunResponse(**result)


@router.get("/summary")
def triage_summary(request: Request, config: str = "A_Structured") -> TriageSummary:
    """Get triage summary stats."""
    store = request.app.state.store
    summary = get_triage_summary(config, store)
    return TriageSummary(**summary)
