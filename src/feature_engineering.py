"""
feature_engineering.py
Builds per-route features from cleaned GTFS DataFrames.
Vectorized — fast on large feeds (BMTC-scale).
"""

import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2))
         * np.sin(dlon / 2) ** 2)
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def _route_lengths_km(gtfs):
    """Average trip length in km per route — VECTORIZED."""
    st = gtfs['stop_times'].merge(
        gtfs['trips'][['trip_id', 'route_id']], on='trip_id', how='left'
    )
    st = st.merge(
        gtfs['stops'][['stop_id', 'stop_lat', 'stop_lon']], on='stop_id', how='left'
    )
    st = st.dropna(subset=['stop_lat', 'stop_lon']).copy()
    st = st.sort_values(['trip_id', 'stop_sequence'])

    # Shift lat/lon within each trip to get "next stop" coordinates
    st['next_lat'] = st.groupby('trip_id')['stop_lat'].shift(-1)
    st['next_lon'] = st.groupby('trip_id')['stop_lon'].shift(-1)

    # Vectorized haversine for all consecutive pairs at once
    valid = st['next_lat'].notna()
    dist = np.zeros(len(st))
    if valid.any():
        dist[valid.values] = haversine_km(
            st.loc[valid, 'stop_lat'].values,
            st.loc[valid, 'stop_lon'].values,
            st.loc[valid, 'next_lat'].values,
            st.loc[valid, 'next_lon'].values,
        )
    st['seg_km'] = dist

    trip_len = st.groupby('trip_id')['seg_km'].sum().rename('trip_length_km')
    trip_route = st.groupby('trip_id')['route_id'].first()

    merged = pd.concat([trip_len, trip_route], axis=1)
    avg_len = merged.groupby('route_id')['trip_length_km'].mean().rename('route_length_km')
    return avg_len.reset_index()


def build_route_features(gtfs):
    """Return one row per route with engineered features."""

    routes = gtfs['routes']
    trips = gtfs['trips']
    st = gtfs['stop_times']
    cal = gtfs['calendar']

    print("  -> merging stop_times with trips ...")
    st_trip = st.merge(trips[['trip_id', 'route_id', 'service_id']],
                       on='trip_id', how='left')

    print("  -> trip_count ...")
    trip_count = trips.groupby('route_id').size().rename('trip_count')

    print("  -> unique_stops ...")
    unique_stops = st_trip.groupby('route_id')['stop_id'].nunique().rename('unique_stops')

    print("  -> avg trip duration ...")
    dur = st_trip.groupby(['route_id', 'trip_id'])['arrival_sec'].agg(['min', 'max'])
    dur['duration_sec'] = dur['max'] - dur['min']
    avg_dur = dur.groupby('route_id')['duration_sec'].mean().rename('avg_duration_sec')

    print("  -> hourly histogram ...")
    st_trip = st_trip.copy()
    st_trip['hour'] = (st_trip['arrival_sec'] // 3600) % 24
    hourly = (st_trip.groupby(['route_id', 'hour']).size()
              .unstack(fill_value=0))
    hourly.columns = [f"trips_hour_{int(h):02d}" for h in hourly.columns]

    print("  -> peak ratio ...")
    peak_hours = [7, 8, 9, 17, 18, 19]
    peak_cols = [f"trips_hour_{h:02d}" for h in peak_hours if f"trips_hour_{h:02d}" in hourly.columns]
    peak = hourly[peak_cols].sum(axis=1) if peak_cols else pd.Series(0, index=hourly.index)
    total = hourly.sum(axis=1)
    offpeak = total - peak
    peak_ratio = (peak / offpeak.replace(0, np.nan)).fillna(0).rename('peak_ratio')

    print("  -> weekday score ...")
    day_cols = ['monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday']
    day_cols = [c for c in day_cols if c in cal.columns]
    cal_map = cal.set_index('service_id')[day_cols].sum(axis=1).rename('weekday_score')
    trips_cal = trips.merge(cal_map, left_on='service_id',
                            right_index=True, how='left')
    weekday_score = (trips_cal.groupby('route_id')['weekday_score']
                     .mean().rename('weekday_score'))

    print("  -> route lengths (vectorized) ...")
    route_len = _route_lengths_km(gtfs).set_index('route_id')

    print("  -> combining ...")
    features = pd.concat([
        trip_count,
        unique_stops,
        avg_dur,
        hourly,
        peak_ratio,
        weekday_score,
        route_len,
    ], axis=1).reset_index()

    # Attach route metadata — use only columns present in this feed
    meta_cols = [c for c in ['route_id', 'route_short_name', 'route_long_name', 'route_type']
                 if c in routes.columns]
    features = features.merge(routes[meta_cols], on='route_id', how='left')

    num_cols = features.select_dtypes(include=[np.number]).columns
    features[num_cols] = features[num_cols].fillna(features[num_cols].median())

    return features


if __name__ == "__main__":
    from data_loader import load_gtfs, clean_gtfs

    CITY = "data/raw/bengaluru"
    print(f"Loading {CITY} ...")
    g = clean_gtfs(load_gtfs(CITY))
    print(f"  routes: {g['routes'].shape}, trips: {g['trips'].shape}, "
          f"stop_times: {g['stop_times'].shape}, stops: {g['stops'].shape}")

    feats = build_route_features(g)
    print(f"\nFeature table shape: {feats.shape}")
    print("Columns:", list(feats.columns))

    out = "data/processed/route_features.csv"
    feats.to_csv(out, index=False)
    print(f"Saved -> {out}")