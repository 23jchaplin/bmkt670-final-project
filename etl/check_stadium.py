import pandas as pd

df = pd.read_csv("data/manual/nfl-stadiums.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"name", "teams", "capacity"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")