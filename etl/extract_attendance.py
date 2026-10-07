import pandas as pd

# Extract 2025 attendance for pro-football reference
df = pd.read_csv("data/manual/attendance_2025.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"Stadium", "Total", "Week 1"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# Extract 2026 attendance for pro-football reference
df = pd.read_csv("data/manual/attendance_2026.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"Stadium", "Total", "Week 1"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# Extract 2025 games from pro-football reference
df = pd.read_csv("data/manual/outcomes_2025.csv")
print(f"Loaded {len(df)} rows")
print("Columns:", list(df.columns))

expected = {"Date", "time", "Won", "Day"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")
