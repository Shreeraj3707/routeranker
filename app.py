"""
app.py — RouteRanker Streamlit dashboard
Talks to the FastAPI backend at API_URL.
"""

import os
import ast
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ---------- Config ----------
API_URL = os.getenv("API_URL", "https://routeranker-api.onrender.com")
STOPS_CSV = "data/processed/stops_slim.csv"

st.set_page_config(page_title="RouteRanker", layout="wide")


# ---------- Session helpers ----------
def _init_state():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None


def api_get(path, params=None):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return requests.get(f"{API_URL}{path}", headers=headers, params=params, timeout=60)


def api_post(path, json_body):
    headers = {"Content-Type": "application/json"}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return requests.post(f"{API_URL}{path}", headers=headers, json=json_body, timeout=60)


_init_state()


# ---------- Login screen ----------
if st.session_state.token is None:
    st.title("🚌 RouteRanker — Sign in")
    st.caption("AI-Powered Public Transit Route Optimization")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in", type="primary"):
            r = api_post("/auth/login", {"email": email, "password": password})
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error(f"Login failed: {r.text}")

    with tab_signup:
        email2 = st.text_input("Email", key="signup_email")
        password2 = st.text_input("Password (min 6 chars)", type="password", key="signup_password")
        if st.button("Create account"):
            r = api_post("/auth/signup", {"email": email2, "password": password2})
            if r.status_code == 201:
                data = r.json()
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error(f"Signup failed: {r.text}")

    st.stop()


# ---------- Logged in ----------
user = st.session_state.user
st.sidebar.success(f"Signed in as **{user['email']}**")
if st.sidebar.button("Log out"):
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

# Load data from API
with st.spinner("Loading routes from API..."):
    r = api_get("/routes", params={"limit": 10000})
    if r.status_code != 200:
        st.error(f"Failed to load routes: {r.status_code} {r.text}")
        st.stop()
    routes_data = r.json()["routes"]

df = pd.DataFrame(routes_data)

# KPIs
st.title("🚌 RouteRanker — AI Transit Route Optimizer")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total routes", len(df))
c2.metric("Overcrowded", int((df["performance"] == "overcrowded").sum()))
c3.metric("Underutilized", int((df["performance"] == "underutilized").sum()))
c4.metric("Balanced", int((df["performance"] == "balanced").sum()))

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🗺️ Map", "⚙️ Optimization", "📈 Simulation"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Performance distribution")
        fig = px.histogram(df, x="performance", color="performance")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("Routes per cluster")
        fig2 = px.bar(df["cluster"].value_counts().sort_index(),
                      labels={"value": "routes", "index": "cluster"})
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Bengaluru stop network")
    if os.path.exists(STOPS_CSV):
        stops = pd.read_csv(STOPS_CSV)
        m = folium.Map(location=[stops["stop_lat"].mean(), stops["stop_lon"].mean()],
                       zoom_start=11)
        for _, s in stops.sample(min(1500, len(stops)), random_state=42).iterrows():
            folium.CircleMarker([s["stop_lat"], s["stop_lon"]],
                                radius=2, color="blue", fill=True,
                                fill_opacity=0.6).add_to(m)
        st_folium(m, width=1100, height=550)
    else:
        st.info("stops_slim.csv not found locally.")

with tab3:
    st.subheader("Route recommendations")
    rid = st.selectbox("Choose a route", df["route_id"].tolist())
    r2 = api_get(f"/routes/{rid}")
    if r2.status_code == 200:
        row = r2.json()
        st.markdown(f"**Performance:** `{row['performance']}` | **Cluster:** `{row['cluster']}`")
        for s in row.get("suggestions", []):
            st.markdown(f"- {s}")
    else:
        st.error(f"Could not load route: {r2.status_code}")

with tab4:
    st.subheader("Current vs optimized trip counts")
    sim = df.copy()
    sim["optimized_trip_count"] = (
        sim["trip_count"] *
        sim["performance"].map({"overcrowded": 1.15, "underutilized": 0.85}).fillna(1.0)
    ).round()
    fig3 = px.bar(
        sim.head(30).melt(id_vars=["route_id", "performance"],
                          value_vars=["trip_count", "optimized_trip_count"],
                          var_name="scenario", value_name="trips"),
        x="route_id", y="trips", color="scenario", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)