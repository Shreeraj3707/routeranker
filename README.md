\# RouteRanker — AI-Powered Public Transit Route Optimization



End-to-end ML pipeline that analyzes GTFS transit data to identify inefficient

bus routes and recommend schedule optimizations. Built and validated on

Bengaluru BMTC (4,416 routes).



\## Quick Start (Windows CMD)



&#x20;   python -m venv routeranker\_env

&#x20;   routeranker\_env\\Scripts\\activate

&#x20;   pip install -r requirements.txt



&#x20;   python src\\data\_loader.py

&#x20;   python src\\feature\_engineering.py

&#x20;   python src\\eda.py

&#x20;   python src\\preprocessing.py

&#x20;   python src\\clustering.py

&#x20;   python src\\classification.py

&#x20;   python src\\inference.py



&#x20;   streamlit run app.py



\## Results



| Metric | Value |

|---|---|

| Routes analyzed | 4,416 |

| Clustering silhouette | 0.796 |

| Overcrowded routes | 184 |

| Underutilized routes | 1,198 |

| Balanced routes | 3,034 |

| End-to-end runtime | < 5 min |



\## Layout



&#x20;   data/raw/<city>/         # GTFS .txt files

&#x20;   data/processed/          # features, splits, recommendations, simulation

&#x20;   models/                  # scaler, encoder, kmeans, xgb, rf

&#x20;   src/                     # pipeline scripts

&#x20;   docs/                    # report, architecture, presentation, eda charts

&#x20;   app.py                   # Streamlit dashboard

&#x20;   Dockerfile

&#x20;   requirements.txt



\## Documentation



\- `docs/final\_report.md` — full technical report

\- `docs/architecture.md` — system architecture and data flow

\- `docs/presentation.md` — stakeholder presentation outline

\- `docs/eda/` — generated charts



\## Data



Bengaluru BMTC GTFS. The pipeline works with any standard GTFS feed —

swap files in `data/raw/<city>/` and update the `CITY` constant in

`src/data\_loader.py` and `src/feature\_engineering.py`.



\## Tech Stack



Python 3.10+ · pandas · NumPy · scikit-learn · XGBoost · Plotly ·

Folium · Streamlit

