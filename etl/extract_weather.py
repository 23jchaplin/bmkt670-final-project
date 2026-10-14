from datetime import date
import meteostat as ms
import pandas as pd

# Specify location
POINT = ms.Point(44.5013, -88.0623, 195)

# Get nearby weather stations
stations = ms.stations.nearby(POINT, limit=4)

# Get hourly data for each football season
dfs = []

for year in range(2021, 2026):
    START = date(year, 9, 1)
    END = date(year + 1, 3, 1)

    # Get hourly data & perform interpolation
    ts = ms.hourly(stations, START, END)
    df = ms.interpolate(ts, POINT).fetch()

    dfs.append(df)
    print(f"Downloaded {len(df)} rows for {year} season")

# Combine all seasons
df = pd.concat(dfs)

# Save to CSV
df.to_csv("data/raw/weather_hourly_raw.csv", index=True)

print(f"Downloaded {len(df)} total rows")