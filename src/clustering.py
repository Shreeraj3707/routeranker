"""
clustering.py
KMeans to segment routes + DBSCAN to flag outlier routes.
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

X = np.load("data/processed/X_scaled.npy")
route_ids = np.load("data/processed/route_ids.npy", allow_pickle=True)
feat_cols = joblib.load("models/feature_columns.pkl")

os.makedirs("docs/eda", exist_ok=True)
os.makedirs("models", exist_ok=True)

n_samples = X.shape[0]
print(f"Samples: {n_samples}, Features: {X.shape[1]}")

# -------- Elbow plot --------
inertias = []
ks = list(range(2, min(10, n_samples)))
for k in ks:
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
    inertias.append(km.inertia_)

plt.figure(figsize=(7, 4))
plt.plot(ks, inertias, marker="o")
plt.xlabel("k")
plt.ylabel("Inertia")
plt.title("KMeans Elbow Curve")
plt.tight_layout()
plt.savefig("docs/eda/kmeans_elbow.png", dpi=120)
plt.close()
print("Saved docs/eda/kmeans_elbow.png")

# -------- Fit final KMeans --------
k_final = min(3, n_samples - 1)   # safe default for tiny feeds
if k_final < 2:
    print("Not enough samples for clustering.")
    raise SystemExit

kmeans = KMeans(n_clusters=k_final, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)

try:
    sil = silhouette_score(X, labels)
    print(f"KMeans k={k_final}, silhouette={sil:.3f}")
except Exception as e:
    print("Silhouette failed:", e)

joblib.dump(kmeans, "models/kmeans.pkl")
print("Saved models/kmeans.pkl")

# -------- DBSCAN for outliers --------
db = DBSCAN(eps=1.5, min_samples=2).fit(X)
db_labels = db.labels_
n_outliers = int((db_labels == -1).sum())
print(f"DBSCAN outliers: {n_outliers}")

# -------- Save cluster assignments --------
df = pd.DataFrame({
    "route_id": route_ids,
    "cluster": labels,
    "dbscan_label": db_labels,
    "is_outlier": db_labels == -1,
})
df.to_csv("data/processed/route_clusters.csv", index=False)
print("Saved data/processed/route_clusters.csv")
print(df.head())