"""
classification.py
Train XGBoost + RandomForest to predict route performance class.
"""

import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

os.makedirs("models", exist_ok=True)
os.makedirs("docs/eda", exist_ok=True)

X_tr = np.load("data/processed/X_train.npy")
X_te = np.load("data/processed/X_test.npy")
y_tr = np.load("data/processed/y_train.npy")
y_te = np.load("data/processed/y_test.npy")
le = joblib.load("models/label_encoder.pkl")

print(f"Train: {X_tr.shape}, Test: {X_te.shape}")
print(f"Classes: {list(le.classes_)}")

n_classes = len(le.classes_)

# --------- XGBoost ---------
xgb = XGBClassifier(
    n_estimators=200, max_depth=5, learning_rate=0.1,
    use_label_encoder=False, eval_metric="mlogloss", random_state=42,
)
xgb.fit(X_tr, y_tr)
xgb_pred = xgb.predict(X_te)

# --------- RandomForest ---------
rf = RandomForestClassifier(
    n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"
)
rf.fit(X_tr, y_tr)
rf_pred = rf.predict(X_te)

for name, pred in [("XGBoost", xgb_pred), ("RandomForest", rf_pred)]:
    print(f"\n=== {name} ===")
    print("Accuracy:", round(accuracy_score(y_te, pred), 3))
    print(classification_report(y_te, pred,
                                labels=np.arange(n_classes),
                                target_names=le.classes_,
                                zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_te, pred, labels=np.arange(n_classes)))

joblib.dump(xgb, "models/xgb.pkl")
joblib.dump(rf, "models/rf.pkl")
print("\nSaved models/xgb.pkl and models/rf.pkl")