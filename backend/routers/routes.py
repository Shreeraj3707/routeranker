"""
/ routes endpoints — list, detail, predictions.
"""

import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/routes", tags=["routes"])

RECS = "data/processed/route_recommendations.csv"
SIM = "data/processed/simulation.csv"


def _load_recs():
    if not os.path.exists(RECS):
        raise HTTPException(500, f"{RECS} not found")
    return pd.read_csv(RECS)


def _load_sim():
    if not os.path.exists(SIM):
        return None
    return pd.read_csv(SIM)


@router.get("")
def list_routes(
    performance: str | None = Query(None, description="balanced | overcrowded | underutilized"),
    cluster: int | None = Query(None, description="0, 1, 2 ..."),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    df = _load_recs()
    if performance:
        df = df[df["performance"] == performance]
    if cluster is not None:
        df = df[df["cluster"] == cluster]
    total = len(df)
    page = df.iloc[offset : offset + limit]
    return {"total": total, "offset": offset, "limit": limit,
            "routes": page.to_dict(orient="records")}


@router.get("/{route_id}")
def get_route(route_id: str):
    df = _load_recs()
    row = df[df["route_id"].astype(str) == str(route_id)]
    if row.empty:
        raise HTTPException(404, f"Route {route_id} not found")
    return row.iloc[0].to_dict()


@router.get("/{route_id}/simulation")
def get_simulation(route_id: str):
    sim = _load_sim()
    if sim is None:
        raise HTTPException(500, f"{SIM} not found")
    row = sim[sim["route_id"].astype(str) == str(route_id)]
    if row.empty:
        raise HTTPException(404, f"No simulation for {route_id}")
    return row.iloc[0].to_dict()