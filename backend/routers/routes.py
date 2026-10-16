"""
/ routes endpoints — backed by the database, requires authentication.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import crud
from backend.auth import get_current_user
from backend.orm_models import User

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("")
def list_routes(
    performance: Optional[str] = Query(None,
        description="balanced | overcrowded | underutilized"),
    cluster: Optional[int] = Query(None, description="0, 1, 2 ..."),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),     # <-- auth required
):
    total, rows = crud.list_routes(db, performance, cluster, limit, offset)
    return {"total": total, "offset": offset, "limit": limit, "routes": rows}


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),     # <-- auth required
):
    return crud.summary_stats(db)


@router.get("/{route_id}")
def get_route(
    route_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),     # <-- auth required
):
    row = crud.get_route(db, route_id)
    if row is None:
        raise HTTPException(404, f"Route {route_id} not found")
    return row