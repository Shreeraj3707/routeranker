"""
app.py
RouteRanker — AI-Powered Public Transit Route Optimization
Streamlit dashboard for planners.
"""

import os
import ast
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="RouteRanker", layout="wide")

# ---------- Paths ----------
RECS = "data/processed/route_recommendations.csv"
SIM = "data/processed/simulation.csv"
STOPS = STOPS = "data/processed/stops_slim.csv"
FEATURES = "data/processed/route_features.csv"


@st.cache_data
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


df = load_csv(RECS)
sim_df = load_csv(SIM)
stops_df = load_csv(STOPS)
feat_df = load_csv(FEATURES)

st.title("🚌 RouteRanker — AI Transit Route Optimizer")
st.caption("Identify inefficiencies, predict route performance, and simulate optimizations.")

if df is None:
    st.error("Missing route_recommendations.csv — run src/inference.py first.")
    st.stop()

# ---------- Sidebar ----------
st.sidebar.header("Filters")
perf_options = sorted(df["performance"].unique().tolist())
perf_sel = st.sidebar.multiselect("Performance classes", perf_options, default=perf_options)

cluster_options = sorted(df["cluster"].unique().tolist())
cluster_sel = st.sidebar.multiselect("Clusters", cluster_options, default=cluster_options)

filtered = df[df["performance"].isin(perf_sel) & df["cluster"].isin(cluster_sel)]

# ---------- Top KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total routes", len(df))
c2.metric("Overcrowded", int((df["performance"] == "overcrowded").sum()))
c3.metric("Underutilized", int((df["performance"] == "underutilized").sum()))
c4.metric("Balanced", int((df["performance"] == "balanced").sum()))

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "🗺️ Map", "🤖 Predictions", "⚙️ Optimization", "📈 Simulation"]
)

# ---------- Tab 1: Overview ----------
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Performance distribution")
        fig = px.histogram(df, x="performance", color="performance",
                           category_orders={"performance": ["balanced", "overcrowded", "underutilized"]})
        st.plotly_chart(fig, width='stretch')

    with col_b:
        st.subheader("Routes per cluster")
        fig2 = px.bar(df["cluster"].value_counts().sort_index(),
                      labels={"value": "routes", "index": "cluster"},
                      title=None)
        st.plotly_chart(fig2, width='stretch')

    if feat_df is not None:
        st.subheader("Feature snapshot")
        st.dataframe(feat_df.describe().T, width='stretch')

# ---------- Tab 2: Map ----------
with tab2:
    st.subheader("Stop network")
    if stops_df is not None and "stop_lat" in stops_df.columns:
        center_lat = stops_df["stop_lat"].mean()
        center_lon = stops_df["stop_lon"].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        sample = stops_df.sample(min(1500, len(stops_df)), random_state=42)
        for _, s in sample.iterrows():
            folium.CircleMarker(
                [s["stop_lat"], s["stop_lon"]],
                radius=2, color="blue", fill=True, fill_opacity=0.6,
                popup=str(s.get("stop_name", "")),
            ).add_to(m)
        st_folium(m, width=1100, height=550)
    else:
        st.info("stops.txt not found or missing lat/lon.")

# ---------- Tab 3: Predictions ----------
with tab3:
    st.subheader("Model predictions")
    st.dataframe(
        filtered[["route_id", "performance", "cluster"]],
        width='stretch', height=400
    )
    st.download_button(
        "Download filtered predictions (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="predictions.csv", mime="text/csv",
    )

# ---------- Tab 4: Optimization ----------
with tab4:
    st.subheader("Optimization suggestions")
    options = filtered["route_id"].tolist() if len(filtered) else df["route_id"].tolist()
    route_id = st.selectbox("Choose a route", options)

    row = df[df["route_id"] == route_id].iloc[0]
    st.markdown(f"**Performance:** `{row['performance']}` &nbsp; | &nbsp; **Cluster:** `{row['cluster']}`")

    sug = row["suggestions"]
    if isinstance(sug, str):
        try:
            sug = ast.literal_eval(sug)
        except Exception:
            sug = [sug]

    st.markdown("### Recommendations")
    for s in sug:
        st.markdown(f"- {s}")

# ---------- Tab 5: Simulation ----------
with tab5:
    st.subheader("Current vs simulated trip counts")
    if sim_df is not None:
        fig3 = px.bar(
            sim_df.melt(id_vars=["route_id", "performance"],
                        value_vars=["trip_count", "optimized_trip_count"],
                        var_name="scenario", value_name="trips"),
            x="route_id", y="trips", color="scenario", barmode="group",
            hover_data=["performance"],
        )
        st.plotly_chart(fig3, width='stretch')

        st.subheader("Delta summary")
        st.dataframe(sim_df[["route_id", "trip_count",
                             "optimized_trip_count", "load_delta",
                             "performance"]],
                     width='stretch')

        csv = sim_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download simulation (CSV)", csv,
                           file_name="simulation.csv", mime="text/csv")
    else:
        st.info("Run src/inference.py to generate simulation.csv.")