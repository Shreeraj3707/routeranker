"""
Admin-only operations — data seeding for the initial Postgres load.
"""

import ast
import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.orm_models import Route, Prediction, Recommendation

router = APIRouter(prefix="/admin", tags=["admin"])

CSV = "data/processed/route_recommendations.csv"


@router.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    if not os.path.exists(CSV):
        raise HTTPException(500, f"{CSV} not found on server")

    if db.query(Route).count() > 0:
        return {"status": "already seeded",
                "routes": db.query(Route).count()}

    df = pd.read_csv(CSV)
    for _, row in df.iterrows():
        rid = str(row["route_id"])

        route = Route(route_id=rid)
        for col in ["trip_count", "unique_stops", "avg_duration_sec",
                    "peak_ratio", "route_length_km"]:
            if col in row and pd.notna(row[col]):
                setattr(route, col, float(row[col]))
        db.add(route)

        db.add(Prediction(
            route_id=rid,
            performance=str(row.get("performance", "unknown")),
            cluster=int(row.get("cluster", 0)),
        ))

        sug_raw = row.get("suggestions", "[]")
        if isinstance(sug_raw, str):
            try:
                sug_list = ast.literal_eval(sug_raw)
            except Exception:
                sug_list = [sug_raw]
        else:
            sug_list = list(sug_raw)

        for i, s in enumerate(sug_list):
            db.add(Recommendation(route_id=rid,
                                  suggestion=str(s), priority=i + 1))

    db.commit()

    return {
        "status": "seeded",
        "routes": db.query(Route).count(),
        "predictions": db.query(Prediction).count(),
        "recommendations": db.query(Recommendation).count(),
    }
