"""
eda.py
Exploratory Data Analysis on route_features.csv.
Generates charts saved to docs/eda/ for later reference.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

FEATURES = "data/processed/route_features.csv"
OUT = "docs/eda"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(FEATURES)
print("Loaded:", df.shape)
print("\nColumns:", list(df.columns))
print("\nSummary stats:")
print(df.describe().T.to_string())

# ---------- 1. Trips per hour ----------
hour_cols = [c for c in df.columns if c.startswith("trips_hour_")]
if hour_cols:
    hourly_avg = df[hour_cols].mean()
    plt.figure(figsize=(12, 5))
    hourly_avg.plot(kind="bar", color="steelblue")
    plt.title("Average Stop-Events per Hour (across routes)")
    plt.xlabel("Hour of day")
    plt.ylabel("Avg count")
    plt.tight_layout()
    plt.savefig(f"{OUT}/hourly_curve.png", dpi=120)
    plt.close()
    print(f"Saved {OUT}/hourly_curve.png")

# ---------- 2. Correlation heatmap ----------
num_df = df.select_dtypes(include=[np.number])
if num_df.shape[1] > 1:
    plt.figure(figsize=(12, 9))
    sns.heatmap(num_df.corr(), cmap="coolwarm", center=0, annot=False)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(f"{OUT}/corr_heatmap.png", dpi=120)
    plt.close()
    print(f"Saved {OUT}/corr_heatmap.png")

# ---------- 3. Route usage scatter ----------
fig = px.scatter(
    df, x="trip_count", y="unique_stops",
    size="avg_duration_sec" if "avg_duration_sec" in df.columns else None,
    color="peak_ratio" if "peak_ratio" in df.columns else None,
    hover_data=["route_id"],
    title="Route Usage Profile: Trip Count vs Unique Stops",
)
fig.write_html(f"{OUT}/scatter_usage.html")
print(f"Saved {OUT}/scatter_usage.html")

# ---------- 4. Distribution of key features ----------
key_features = [c for c in
                ["trip_count", "unique_stops", "avg_duration_sec",
                 "peak_ratio", "route_length_km"]
                if c in df.columns]

if key_features:
    fig, axes = plt.subplots(1, len(key_features),
                             figsize=(4 * len(key_features), 4))
    if len(key_features) == 1:
        axes = [axes]
    for ax, col in zip(axes, key_features):
        ax.hist(df[col].dropna(), bins=15, color="teal", edgecolor="black")
        ax.set_title(col)
    plt.tight_layout()
    plt.savefig(f"{OUT}/feature_distributions.png", dpi=120)
    plt.close()
    print(f"Saved {OUT}/feature_distributions.png")

# ---------- 5. Identify candidate inefficient routes ----------

# ---------- 5. Identify candidate inefficient routes ----------
# NOTE: labels are defined WITHOUT using trip_count or peak_ratio, so that
# those features can be used as legitimate predictors in classification.

if "trips_hour_08" in df.columns and "unique_stops" in df.columns and "avg_duration_sec" in df.columns:
    morning_hi = df["trips_hour_08"].quantile(0.75)
    morning_lo = df["trips_hour_08"].quantile(0.25)
    stops_hi = df["unique_stops"].quantile(0.75)
    stops_lo = df["unique_stops"].quantile(0.25)
    dur_lo = df["avg_duration_sec"].quantile(0.25)

    df["rough_label"] = np.where(
        (df["trips_hour_08"] >= morning_hi) & (df["unique_stops"] >= stops_hi),
        "overcrowded",
        np.where(
            (df["trips_hour_08"] <= morning_lo) & (df["avg_duration_sec"] <= dur_lo),
            "underutilized",
            "balanced"
        )
    )

    print("\nRough label counts:")
    print(df["rough_label"].value_counts())
    df.to_csv("data/processed/route_features_labeled.csv", index=False)
    print("Saved data/processed/route_features_labeled.csv")

print("\nEDA complete. Charts in docs/eda/")