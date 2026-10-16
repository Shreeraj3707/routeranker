"""
Loads ML artifacts (scaler, encoders, models) once at startup.
"""

import os
import joblib
import numpy as np
import pandas as pd


class ModelBundle:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.xgb = None
        self.rf = None
        self.kmeans = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return

        def _p(name):
            return os.path.join(self.model_dir, name)

        self.scaler = joblib.load(_p("scaler.pkl"))
        self.label_encoder = joblib.load(_p("label_encoder.pkl"))
        self.feature_columns = joblib.load(_p("feature_columns.pkl"))
        self.xgb = joblib.load(_p("xgb.pkl"))
        self.rf = joblib.load(_p("rf.pkl"))
        self.kmeans = joblib.load(_p("kmeans.pkl"))

        self._loaded = True
        print(f"[ModelBundle] loaded {len(self.feature_columns)} features")

    def predict(self, features_dict: dict):
        """Accepts a dict, returns (performance, cluster, suggestions)."""
        # Ensure every feature column is present, default 0 if missing
        row = {col: features_dict.get(col, 0) for col in self.feature_columns}
        X = pd.DataFrame([row])[self.feature_columns]
        X_scaled = self.scaler.transform(X)

        perf_idx = self.xgb.predict(X_scaled)[0]
        performance = self.label_encoder.inverse_transform([perf_idx])[0]
        cluster = int(self.kmeans.predict(X_scaled)[0])
        suggestions = _suggest(performance, cluster)
        return performance, cluster, suggestions


def _suggest(performance: str, cluster: int):
    if performance == "overcrowded":
        s = [
            "Increase trip frequency during peak hours (7–10 AM, 5–8 PM)",
            "Deploy higher-capacity buses on this route",
            "Consider splitting route at the highest-demand midpoint",
        ]
    elif performance == "underutilized":
        s = [
            "Reduce trip frequency during off-peak hours",
            "Evaluate merging with a nearby overlapping route",
            "Replace with smaller / mini-bus vehicles",
        ]
    else:
        s = ["Maintain current schedule; monitor quarterly"]
    s.append(f"Cluster {cluster}: benchmark against cluster peers")
    return s


bundle = ModelBundle()