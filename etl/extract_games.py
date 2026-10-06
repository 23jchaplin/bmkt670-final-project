import requests
import pandas as pd

# Get 2025 games
r_2025 = requests.get(
    "https://api.nfldata.org/v1/games",
    params={"limit": 500, "team": "GB", "season": 2025}
)
r_2025.raise_for_status()

data_2025 = r_2025.json()["data"]
games_2025 = pd.DataFrame(data_2025)

# Save raw 2025 data unchanged
games_2025.to_csv("data/raw/games_2025_raw.csv", index=False)
print(f"Downloaded {len(games_2025)} rows for 2025")


# Get 2026 games
r_2026 = requests.get(
    "https://api.nfldata.org/v1/games",
    params={"limit": 500, "team": "GB", "season": 2026}
)
r_2026.raise_for_status()

data_2026 = r_2026.json()["data"]
games_2026 = pd.DataFrame(data_2026)

# Save raw 2026 data unchanged
games_2026.to_csv("data/raw/games_2026_raw.csv", index=False)
print(f"Downloaded {len(games_2026)} rows for 2026")
