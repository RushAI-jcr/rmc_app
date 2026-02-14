"""Fairness report endpoint."""

from fastapi import APIRouter, Depends, Request

from api.config import PROCESSED_DIR
from api.db.models import User
from api.dependencies import require_admin

router = APIRouter(prefix="/api/fairness", tags=["fairness"])


@router.get("/report")
def fairness_report(
    request: Request,
    current_user: User = Depends(require_admin),
) -> dict:
    """Get the fairness audit report."""
    import pandas as pd

    path = PROCESSED_DIR / "fairness_report.csv"
    if not path.exists():
        return {"status": "not_available", "report": []}

    df = pd.read_csv(path)
    records = df.to_dict(orient="records")

    return {"status": "ok", "report": records}
