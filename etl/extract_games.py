import requests
import pandas as pd

# Get 2021-2025 games
for year in range(2021, 2026):
    r = requests.get(
        "https://api.nfldata.org/v1/games",
        params={"limit": 500, "team": "GB", "season": year}
    )
    r.raise_for_status()

    data = r.json()["data"]
    games = pd.DataFrame(data)

    # Save raw data unchanged
    games.to_csv(f"data/raw/games_{year}_raw.csv", index=False)
    print(f"Downloaded {len(games)} rows for {year}")