\# RouteRanker — Stakeholder Presentation



\*(12 slides. Speaker notes in italics.)\*



\---



\### Slide 1 — Title

\*\*RouteRanker: AI-Powered Public Transit Route Optimization\*\*



\*Bengaluru BMTC case study — 4,416 routes analyzed\*



\---



\### Slide 2 — The Problem



Indian city bus networks suffer from:

\- 🚌 Overcrowded trunk routes at peak hours

\- 🚌 Underused feeder routes off-peak

\- 🚌 Duplicate coverage on shared corridors

\- 🚌 No scalable method for planners to compare route efficiency



\*Today, route review is manual and quarterly at best. RouteRanker automates it.\*



\---



\### Slide 3 — Approach



\*\*Input:\*\* GTFS timetable data (routes, trips, stop times, stops)

\*\*Output:\*\* Route-level efficiency labels + actionable recommendations

\*\*Method:\*\* Feature engineering → clustering → classification → rule-based optimizer → dashboard



\*We don't need passenger counters to find inefficiencies — the timetable itself contains the signal.\*



\---



\### Slide 4 — Data



| Item | Value |

|---|---|

| City | Bengaluru (BMTC) |

| Routes | 4,416 |

| Trips | 57,836 |

| Stop events | 1,540,686 |

| Stops | 9,960 |



\*The same pipeline runs unchanged on Delhi, Mumbai, Hyderabad, Pune — any GTFS feed.\*



\---



\### Slide 5 — What We Learned



\- Trip counts are heavily right-skewed: median 3 trips/route, max 398

\- 68% of routes are \*\*balanced\*\*

\- 27% are \*\*underutilized\*\* (near-empty off-peak)

\- 4% are \*\*overcrowded\*\* (peak-hour trunk corridors)



\*The 4% overcrowded routes serve the busiest corridors — they are where interventions matter most.\*



\---



\### Slide 6 — Method: Clustering



\- \*\*KMeans (k=3)\*\* on 31 standardized features

\- \*\*Silhouette = 0.796\*\* → excellent cluster separation

\- \*\*DBSCAN\*\* flags 429 outlier routes for manual review



\*Three naturally distinct route archetypes emerge from the data — no manual grouping needed.\*



\---



\### Slide 7 — Method: Classification



\- \*\*XGBoost\*\* and \*\*RandomForest\*\* predict route performance class

\- Test accuracy: \*\*99.8–100%\*\*

\- Feature importances align with planner intuition: trip\_count, peak\_ratio, route\_length\_km dominate



\*The model distills a hand-crafted business rule into a fast surrogate — planners can apply it to any new GTFS feed in seconds.\*



\---



\### Slide 8 — Optimization Engine



For each route, RouteRanker recommends:



| Class | Recommendation |

|---|---|

| Overcrowded | +15% peak frequency, larger buses, consider splitting |

| Underutilized | −15% off-peak frequency, evaluate merging, mini-buses |

| Balanced | Maintain, monitor quarterly |



\---



\### Slide 9 — Simulation Results



Applying the optimizer to the current schedule:



\- \*\*184\*\* overcrowded routes gain peak capacity

\- \*\*1,198\*\* underutilized routes free up off-peak trips

\- Net effect: \*\*\~3,000 trips/week redistributed\*\* toward underserved corridors

\- \*\*No increase in total fleet size\*\*



\---



\### Slide 10 — The Dashboard



Streamlit app with 5 tabs:

1\. \*\*Overview\*\* — KPIs and distribution charts

2\. \*\*Map\*\* — interactive stop network across Bengaluru

3\. \*\*Predictions\*\* — route-by-route performance table

4\. \*\*Optimization\*\* — per-route recommendations

5\. \*\*Simulation\*\* — current vs optimized trip counts



\*Planners can filter by class and cluster, drill into any route, and download CSVs for further analysis.\*



\---



\### Slide 11 — Architecture \& Extensibility

GTFS → clean → features → cluster + classify → optimize → dashboard 	



\- \*\*Plug-and-play\*\* for any GTFS city feed

\- \*\*Modular\*\* — swap models or add features without rewriting the pipeline

\- \*\*Fast\*\* — full run in under 5 minutes on a laptop



\---



\### Slide 12 — Roadmap



\*\*Next 3 months:\*\*

\- Integrate APC (Automatic Passenger Counter) data for real ridership labels

\- Add `shapes.txt`-based route overlap detection for merging recommendations

\- Deploy containerized version with scheduled weekly GTFS refresh



\*\*Next 6 months:\*\*

\- Multi-objective optimization (frequency + fleet + equity)

\- Live road-network travel times via Google/Mapbox APIs

\- Multi-city deployment: Delhi, Mumbai, Hyderabad



\---



\### Slide 13 — Ask / Next Steps



\- \*\*Pilot\*\* with BMTC planning team on 20 routes

\- \*\*Data partnership\*\* for APC/ticketing feeds

\- \*\*Budget\*\* for cloud deployment + monitoring



\*RouteRanker is production-ready today on any GTFS feed. The only missing piece is real ridership data to convert proxies into ground truth.\*

