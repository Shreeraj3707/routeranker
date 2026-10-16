"""
CRUD helpers — database queries for routes, predictions, recommendations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.orm_models import Route, Prediction, Recommendation


def list_routes(db: Session,
                performance: Optional[str] = None,
                cluster: Optional[int] = None,
                limit: int = 100,
                offset: int = 0):
    """Return (total, rows) where rows are dicts with route + prediction."""
    query = (db.query(Route, Prediction)
             .join(Prediction, Prediction.route_id == Route.route_id))

    if performance:
        query = query.filter(Prediction.performance == performance)
    if cluster is not None:
        query = query.filter(Prediction.cluster == cluster)

    total = query.count()
    rows = query.offset(offset).limit(limit).all()

    return total, [
        {
            "route_id": r.route_id,
            "route_short_name": r.route_short_name,
            "route_long_name": r.route_long_name,
            "trip_count": r.trip_count,
            "unique_stops": r.unique_stops,
            "avg_duration_sec": r.avg_duration_sec,
            "peak_ratio": r.peak_ratio,
            "route_length_km": r.route_length_km,
            "performance": p.performance,
            "cluster": p.cluster,
        }
        for r, p in rows
    ]


def get_route(db: Session, route_id: str):
    route = db.get(Route, str(route_id))
    if route is None:
        return None

    pred = (db.query(Prediction)
            .filter(Prediction.route_id == str(route_id))
            .order_by(Prediction.predicted_at.desc())
            .first())

    recs = (db.query(Recommendation)
            .filter(Recommendation.route_id == str(route_id))
            .order_by(Recommendation.priority)
            .all())

    return {
        "route_id": route.route_id,
        "route_short_name": route.route_short_name,
        "route_long_name": route.route_long_name,
        "trip_count": route.trip_count,
        "unique_stops": route.unique_stops,
        "avg_duration_sec": route.avg_duration_sec,
        "peak_ratio": route.peak_ratio,
        "route_length_km": route.route_length_km,
        "performance": pred.performance if pred else None,
        "cluster": pred.cluster if pred else None,
        "suggestions": [r.suggestion for r in recs],
    }


def summary_stats(db: Session):
    """Counts per performance class — for dashboard KPIs."""
    rows = (db.query(Prediction.performance,
                     __import__("sqlalchemy").func.count(Prediction.id))
            .group_by(Prediction.performance).all())
    return {perf: cnt for perf, cnt in rows}