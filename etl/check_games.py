import pandas as pd

# Check 2021-2025 attendance from Pro-Football-Reference
for year in range(2021, 2026):
    df = pd.read_csv(f"data/raw/games_{year}.csv")
    print(f"Loaded {len(df)} rows for {year} games")
    print("Columns:", list(df.columns))

    expected = {"week", "season", "home_team"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for {year}: {missing}")

