"""
One-time migration: load route_recommendations.csv into the DB.
Run:  python scripts\migrate_csv_to_db.py
"""

import ast
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import engine, SessionLocal, Base
from backend.orm_models import Route, Prediction, Recommendation

CSV = "data/processed/route_recommendations.csv"


def main():
    print(f"Reading {CSV} ...")
    df = pd.read_csv(CSV)
    print(f"  {len(df)} rows")

    print("Creating tables ...")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        for _, row in df.iterrows():
            rid = str(row["route_id"])

            route = session.get(Route, rid)
            if route is None:
                route = Route(route_id=rid)
                session.add(route)

            for col in ["trip_count", "unique_stops", "avg_duration_sec",
                        "peak_ratio", "route_length_km"]:
                if col in row and pd.notna(row[col]):
                    setattr(route, col, float(row[col]))

            existing = (session.query(Prediction)
                        .filter(Prediction.route_id == rid).first())
            if existing is None:
                session.add(Prediction(
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
                session.add(Recommendation(
                    route_id=rid, suggestion=str(s), priority=i + 1,
                ))

        session.commit()
        print("Committed.")
    except Exception as e:
        session.rollback()
        print("ERROR:", e)
        raise
    finally:
        session.close()

    session = SessionLocal()
    n_routes = session.query(Route).count()
    n_preds = session.query(Prediction).count()
    n_recs = session.query(Recommendation).count()
    print(f"DB now has: {n_routes} routes, {n_preds} predictions, {n_recs} recommendations")
    session.close()


if __name__ == "__main__":
    main()	