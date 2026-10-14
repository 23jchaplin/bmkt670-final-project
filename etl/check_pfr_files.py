import pandas as pd

# Check 2021-2025 attendance from Pro-Football-Reference
for year in range(2021, 2026):
    df = pd.read_csv(f"data/manual/attendance_{year}.csv")
    print(f"Loaded {len(df)} rows for {year} attendance")
    print("Columns:", list(df.columns))

    expected = {"Stadium", "Total", "Week 1"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for {year}: {missing}")


# Check 2021-2025 game outcomes from Pro-Football-Reference
for year in range(2021, 2026):
    df = pd.read_csv(f"data/manual/outcomes_{year}.csv")
    print(f"Loaded {len(df)} rows for {year} outcomes")
    print("Columns:", list(df.columns))

    expected = {"Date", "time", "Won", "Day"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for {year}: {missing}")