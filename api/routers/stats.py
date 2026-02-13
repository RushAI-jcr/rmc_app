"""Stats overview endpoint."""

from fastapi import APIRouter, Request

from api.config import PROCESSED_DIR

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview")
def stats_overview(request: Request, config: str = "A_Structured") -> dict:
    """Dashboard overview stats."""
    from api.services.triage_service import get_triage_summary
    from api.services.prediction_service import build_prediction_table

    store = request.app.state.store
    summary = get_triage_summary(config, store)
    predictions = build_prediction_table(config, store)

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
