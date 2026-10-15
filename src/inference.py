"""
inference.py
Predict performance for every route, generate optimization suggestions,
and simulate improved loads.
"""

import os
import numpy as np
import pandas as pd
import joblib

MODEL_DIR = "models"
OUT_DIR = "data/processed"

scaler = joblib.load(f"{MODEL_DIR}/scaler.pkl")
le = joblib.load(f"{MODEL_DIR}/label_encoder.pkl")
feat_cols = joblib.load(f"{MODEL_DIR}/feature_columns.pkl")
xgb = joblib.load(f"{MODEL_DIR}/xgb.pkl")
kmeans = joblib.load(f"{MODEL_DIR}/kmeans.pkl")

# Load original feature table (unscaled)
df = pd.read_csv(f"{OUT_DIR}/route_features_labeled.csv")

# Build matrix in exact column order
X = df[feat_cols].fillna(df[feat_cols].median())
X_scaled = scaler.transform(X)

# Predict
y_pred = xgb.predict(X_scaled)
df["performance"] = le.inverse_transform(y_pred)
df["cluster"] = kmeans.predict(X_scaled)


def suggest(row):
    s = []
    perf = row["performance"]
    if perf == "overcrowded":
        s.append("Increase trip frequency during peak hours (7–10 AM, 5–8 PM)")
        s.append("Deploy higher-capacity buses")
        s.append("Consider splitting route at highest-demand midpoint")
    elif perf == "underutilized":
        s.append("Reduce trip frequency during off-peak hours")
        s.append("Evaluate merging with overlapping route")
        s.append("Replace with smaller / mini-bus vehicles")
    else:
        s.append("Maintain current schedule; monitor quarterly")
    s.append(f"Cluster {int(row['cluster'])}: benchmark against cluster peers")
    return s


df["suggestions"] = df.apply(suggest, axis=1)

# Save recommendations
df.to_csv(f"{OUT_DIR}/route_recommendations.csv", index=False)
print("Saved route_recommendations.csv")
print(df[["route_id", "performance", "cluster"]].head())

# ---------- Simulated optimized load ----------
sim = df.copy()
cluster_mean = sim.groupby("cluster")["trip_count"].transform("mean")
multiplier = np.where(sim["performance"] == "overcrowded", 1.15,
             np.where(sim["performance"] == "underutilized", 0.85, 1.0))
sim["optimized_trip_count"] = (cluster_mean * multiplier).round().astype(int)
sim["load_delta"] = sim["optimized_trip_count"] - sim["trip_count"]

sim[["route_id", "trip_count", "optimized_trip_count", "load_delta",
     "performance", "cluster"]].to_csv(f"{OUT_DIR}/simulation.csv", index=False)
print("\nSaved simulation.csv")
print(sim[["route_id", "trip_count", "optimized_trip_count", "load_delta"]].head())