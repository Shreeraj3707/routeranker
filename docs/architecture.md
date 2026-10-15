\# RouteRanker — System Architecture



\## Component Diagram

┌────────────────────────────────────────────────────────────────────┐

│ DATA INGESTION │

│ GTFS zip → data/raw/<city>/{routes,trips,stop\_times,stops, │

│ calendar}.txt │

│ src/data\_loader.py — clean, dedupe, parse times │

└──────────────────────────────┬─────────────────────────────────────┘

│

▼

┌────────────────────────────────────────────────────────────────────┐

│ FEATURE ENGINEERING │

│ src/feature\_engineering.py │

│ → trip\_count, unique\_stops, avg\_duration\_sec, │

│ trips\_hour\_00..23, peak\_ratio, weekday\_score, route\_length\_km │

│ Output: data/processed/route\_features.csv │

└──────────────────────────────┬─────────────────────────────────────┘

│

┌────────────────┴────────────────┐

▼ ▼

┌──────────────────────────┐ ┌───────────────────────────────────┐

│ EXPLORATORY ANALYSIS │ │ PREPROCESSING │

│ src/eda.py │ │ src/preprocessing.py │

│ - hourly curve │ │ - StandardScaler │

│ - correlation heatmap │ │ - LabelEncoder │

│ - label assignment │ │ - 80/20 train/test split │

│ Output: docs/eda/\* │ │ Output: models/scaler.pkl, │

└──────────────────────────┘ │ X\_.npy, y\_.npy │

└──────────────┬────────────────────┘

│

┌────────────────┴───────────────┐

▼ ▼

┌──────────────────────────┐ ┌────────────────────────┐

│ CLUSTERING │ │ CLASSIFICATION │

│ src/clustering.py │ │ src/classification.py │

│ - KMeans (k=3) │ │ - XGBoost │

│ - DBSCAN (outliers) │ │ - RandomForest │

│ Output: kmeans.pkl, │ │ Output: xgb.pkl, │

│ route\_clusters │ │ rf.pkl │

└──────────────┬───────────┘ └──────────┬─────────────┘

│ │

└─────────────┬─────────────┘

▼

┌────────────────────────────────────────────────────────────────────┐

│ INFERENCE │

│ src/inference.py │

│ - Predict performance class per route │

│ - Attach cluster label │

│ - Generate rule-based suggestions │

│ - Simulate optimized trip counts │

│ Output: route\_recommendations.csv, simulation.csv │

└──────────────────────────────┬─────────────────────────────────────┘

│

▼

┌────────────────────────────────────────────────────────────────────┐

│ STREAMLIT DASHBOARD │

│ app.py │

│ Tabs: Overview | Map | Predictions | Optimization | Simulation │

│ Sidebar filters: performance classes, clusters │

└────────────────────────────────────────────────────────────────────┘



\## Data Contracts



| Stage | Input | Output |

|---|---|---|

| data\_loader | raw GTFS .txt | cleaned DataFrames with `arrival\_sec` |

| feature\_engineering | cleaned DataFrames | 1 row per route × \~30 columns |

| eda | route\_features.csv | charts + rough\_label column |

| preprocessing | route\_features\_labeled.csv | X\_\*.npy, y\_\*.npy, scaler.pkl, encoder.pkl |

| clustering | X\_scaled.npy | kmeans.pkl, route\_clusters.csv |

| classification | X\_train/test.npy | xgb.pkl, rf.pkl |

| inference | all models + features | recommendations + simulation csv |

| app | all csv/pkl | Streamlit UI |



\## Runtime



| Stage | BMTC (4,416 routes) |

|---|---|

| data\_loader | \~90 seconds |

| feature\_engineering | \~90 seconds |

| eda | \~5 seconds |

| preprocessing | \~3 seconds |

| clustering | \~15 seconds |

| classification | \~30 seconds |

| inference | \~5 seconds |

| \*\*Total\*\* | \*\*\~4 minutes\*\* |



\## Extension Points



\- \*\*New city\*\* → drop GTFS files in `data/raw/<city>/`, change one `CITY`

&#x20; constant in `data\_loader.py` and `feature\_engineering.py`.

\- \*\*New feature\*\* → add a column in `build\_route\_features()`; downstream

&#x20; scripts pick it up automatically.

\- \*\*New model\*\* → implement in a new `src/<model>.py` that reads `X\_\*.npy`,

&#x20; writes a `.pkl`. Register in `inference.py`.

\- \*\*New dashboard tab\*\* → add a `with tabN:` block in `app.py`.

