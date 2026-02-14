"""Stats overview endpoint."""

from fastapi import APIRouter, Depends, Request

from api.config import PROCESSED_DIR
from api.db.models import User
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def stats_overview(
    request: Request,
    config: str = "A_Structured",
    current_user: User = Depends(get_current_user),
) -> dict:
    """Dashboard overview stats."""
    from api.services.triage_service import get_triage_summary

    store = request.app.state.store
    summary = get_triage_summary(config, store)
    predictions = store.get_predictions(config)

    # Bakeoff comparison
    import pandas as pd
    bakeoff_path = PROCESSED_DIR / "bakeoff_comparison.csv"
    bakeoff = []
    if bakeoff_path.exists():
        bakeoff = pd.read_csv(bakeoff_path).to_dict(orient="records")

    return {
        "summary": summary,
        "total_applicants_all_years": len(store.master_data),
        "test_applicants": len(predictions),
        "models_loaded": list(store.model_results.keys()),
        "bakeoff": bakeoff,
    }
