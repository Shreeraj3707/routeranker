"""
preprocessing.py
Scales numeric features, encodes labels, and produces train/val splits.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

IN = "data/processed/route_features_labeled.csv"
OUT_DIR = "data/processed"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    df = pd.read_csv(IN)
    print("Loaded:", df.shape)

    # Drop non-numeric identifier columns before scaling
    drop_cols = ["route_id", "route_short_name", "route_long_name", "rough_label"]
    drop_cols = [c for c in drop_cols if c in df.columns]

    y_raw = df["rough_label"].values
    route_ids = df["route_id"].values

    X_df = df.drop(columns=drop_cols)
    X_df = X_df.select_dtypes(include=[np.number])
    X_df = X_df.fillna(X_df.median())

    print("Feature matrix:", X_df.shape)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_df)

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    print("Label classes:", list(le.classes_))

    # Save scaler and encoder
    joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")
    joblib.dump(le, f"{MODEL_DIR}/label_encoder.pkl")
    joblib.dump(list(X_df.columns), f"{MODEL_DIR}/feature_columns.pkl")
    print(f"Saved scaler + encoder + feature columns to {MODEL_DIR}/")

    # Save scaled feature matrix for downstream use
    np.save(f"{OUT_DIR}/X_scaled.npy", X_scaled)
    np.save(f"{OUT_DIR}/y.npy", y)
    np.save(f"{OUT_DIR}/route_ids.npy", route_ids)

    # Stratified split — only if every class has >= 2 samples
    classes, counts = np.unique(y, return_counts=True)
    min_count = counts.min()
    if min_count >= 2 and len(classes) > 1:
        strat = y
    else:
        strat = None
        print(f"Warning: min class count = {min_count}. Using non-stratified split.")

    X_tr, X_te, y_tr, y_te = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=strat
    )
    np.save(f"{OUT_DIR}/X_train.npy", X_tr)
    np.save(f"{OUT_DIR}/X_test.npy", X_te)
    np.save(f"{OUT_DIR}/y_train.npy", y_tr)
    np.save(f"{OUT_DIR}/y_test.npy", y_te)

    print(f"Train: {X_tr.shape}, Test: {X_te.shape}")
    print("Preprocessing complete.")


if __name__ == "__main__":
    main()