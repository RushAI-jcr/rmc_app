"""Fairness report endpoint."""

from fastapi import APIRouter, Request

from api.config import PROCESSED_DIR

router = APIRouter(prefix="/api/fairness", tags=["fairness"])


@router.get("/report")
def fairness_report(request: Request) -> dict:
    """Get the fairness audit report."""
    import pandas as pd

    path = PROCESSED_DIR / "fairness_report.csv"
    if not path.exists():
        return {"status": "not_available", "report": []}

    df = pd.read_csv(path)
    records = df.to_dict(orient="records")

    return {"status": "ok", "report": records}
