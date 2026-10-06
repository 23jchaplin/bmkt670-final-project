import pandas as pd

df = pd.read_csv("data/manual/attendance_2025.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"Stadium", "Total", "Week 1"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = pd.read_csv("data/manual/attendance_2026.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"Stadium", "Total", "Week 1"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")