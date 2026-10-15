import pandas as pd
import os

CITY_PATH = "data/raw/delhi"

files = ['routes', 'trips', 'stop_times', 'stops', 'calendar']
gtfs = {}
for f in files:
    path = os.path.join(CITY_PATH, f"{f}.txt")
    gtfs[f] = pd.read_csv(path)
    print(f"{f:12s} -> shape {gtfs[f].shape}")

print("\n--- routes.txt preview ---")
print(gtfs['routes'].head())

print("\n--- stops.txt preview ---")
print(gtfs['stops'].head())

print("\n--- stop_times.txt preview ---")
print(gtfs['stop_times'].head())

print("\n--- calendar.txt preview ---")
print(gtfs['calendar'].head()) 