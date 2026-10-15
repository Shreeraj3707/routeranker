"""
data_loader.py
Loads GTFS files for a given city and performs basic cleaning.
"""

import os
import pandas as pd


def load_gtfs(city_path):
    """Load the 5 core GTFS files into a dict of DataFrames."""
    files = ['routes', 'trips', 'stop_times', 'stops', 'calendar']
    gtfs = {}
    for f in files:
        path = os.path.join(city_path, f"{f}.txt")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required file: {path}")
        gtfs[f] = pd.read_csv(path)
    return gtfs


def clean_gtfs(gtfs):
    """Basic cleaning: drop duplicates, handle missing critical IDs,
    parse arrival/departure times into seconds since midnight."""

    # --- routes.txt ---
    gtfs['routes'] = gtfs['routes'].drop_duplicates()
    gtfs['routes'] = gtfs['routes'].dropna(subset=['route_id'])

    # --- trips.txt ---
    gtfs['trips'] = gtfs['trips'].drop_duplicates()
    gtfs['trips'] = gtfs['trips'].dropna(subset=['route_id', 'trip_id'])

    # --- stops.txt ---
    gtfs['stops'] = gtfs['stops'].drop_duplicates()
    gtfs['stops'] = gtfs['stops'].dropna(subset=['stop_id'])

    # --- calendar.txt ---
    gtfs['calendar'] = gtfs['calendar'].drop_duplicates()

    # --- stop_times.txt ---
    st = gtfs['stop_times'].drop_duplicates()
    st = st.dropna(subset=['trip_id', 'stop_id', 'arrival_time'])

    def parse_time(t):
        """Convert HH:MM:SS (may exceed 24h) to seconds since midnight."""
        try:
            h, m, s = map(int, str(t).split(':'))
            return h * 3600 + m * 60 + s
        except Exception:
            return None

    st['arrival_sec'] = st['arrival_time'].apply(parse_time)
    st = st.dropna(subset=['arrival_sec'])
    st['arrival_sec'] = st['arrival_sec'].astype(int)

    gtfs['stop_times'] = st

    return gtfs


if __name__ == "__main__":
    CITY = "data/raw/bengaluru"
    print(f"Loading GTFS from {CITY} ...")
    g = load_gtfs(CITY)
    print("Before cleaning:")
    for k, v in g.items():
        print(f"  {k:12s} shape={v.shape}")

    g = clean_gtfs(g)
    print("\nAfter cleaning:")
    for k, v in g.items():
        print(f"  {k:12s} shape={v.shape}")

    print("\nstop_times after time parsing:")
    print(g['stop_times'][['trip_id', 'arrival_time', 'arrival_sec', 'stop_id']].head())
