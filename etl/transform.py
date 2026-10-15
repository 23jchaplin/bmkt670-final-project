from pathlib import Path
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

RAW_DIR = Path("data/raw")
MANUAL_DIR = Path("data/manual")
CLEAN_DIR = Path("data/clean")


def read_yearly_files(folder, pattern, required=None):
    """Combine yearly CSVs; manual-file seasons come from their filenames."""
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found matching {folder / pattern}")
    frames = []
    for file in files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        if required is not None:
            missing = set(required) - set(df.columns)
            if missing:
                raise ValueError(f"{file.name}: missing columns {sorted(missing)}")
        if "season" not in df.columns:
            df["season"] = int(file.stem.rsplit("_", 1)[1])
        frames.append(df)
        print(f"Loaded {file.name}: {len(df)} rows")
    return pd.concat(frames, ignore_index=True)


# Combine yearly files into one dataset per source, then read hourly weather.
games = read_yearly_files(RAW_DIR, "games_*.csv")
# Dropping unwanted columns from games
games = games.drop(columns=['gametime', 'total_line', 'div_game', 'spread_line', 'boxscore_url', 'roof', 'stadium', 'surface'])



attendance = read_yearly_files(MANUAL_DIR, "attendance_*.csv")
attendance = attendance.loc[attendance["Tm"].notna()].copy()

outcomes = read_yearly_files(MANUAL_DIR, "outcomes_*.csv")
# Dropping unwanted columns from outcomes
outcomes = outcomes.drop(columns=[ 'Rec', '1stD', 'TotYd', 'PassY', 'RushY', 'TO', '1stD', 'TotYd', 'PassY', 'RushY', 'TO', 'Offense', 'Defense', 'Sp. Tms'])


weather = pd.read_csv(RAW_DIR / "weather_hourly_raw.csv")
weather = weather.drop(columns=['tsun', 'cldc', 'coco', 'snwd', 'wdir', 'wpgt'])

weather.to_csv(CLEAN_DIR / "weather_hourly_raw.csv", index=False)

# Align team names, dates, and timestamps; reshape weekly attendance.
TEAM_NAMES = {
    "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
    "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs", "LA": "Los Angeles Rams", "LAC": "Los Angeles Chargers",
    "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
    "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
    "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans", "WAS": "Washington Commanders",
}
TEAM_IDS = {name.casefold(): team_id for team_id, name in TEAM_NAMES.items()}
TEAM_IDS.update({team_id.casefold(): team_id for team_id in TEAM_NAMES})
TEAM_IDS.update({
    "washington football team": "WAS", "washington redskins": "WAS", "oakland raiders": "LV",
    "san diego chargers": "LAC", "st. louis rams": "LA", "st louis rams": "LA",
    "lar": "LA", "jac": "JAX", "wsh": "WAS",
})


def align_team_ids(series):
    names = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True).str.casefold()
    ids = names.map(TEAM_IDS).astype("string")
    if ids.isna().any():
        raise ValueError(f"Missing or unrecognized teams: {series[ids.isna()].unique().tolist()}")
    return ids


games["home_team_id"] = align_team_ids(games["home_team"])
games["opponent_id"] = align_team_ids(games["away_team"])
games["week"] = pd.to_numeric(games["week"], errors="raise").astype(int)
attendance["team_id"] = align_team_ids(attendance["Tm"])
outcomes["opponent_id"] = align_team_ids(outcomes["Opp"])

# Convert game and outcome dates to normalized datetime objects.
games["date_id"] = pd.to_datetime(games["gameday"], format="mixed", errors="raise").dt.normalize()
outcomes["date_id"] = pd.to_datetime(outcomes["Date"], format="mixed", errors="raise").dt.normalize()
if games["date_id"].isna().any() or outcomes["date_id"].isna().any():
    raise ValueError("Game and outcome dates cannot be missing.")

# Keep the ET label; use timezone-aware UTC timestamps for weather matching.
outcomes["kickoff_time"] = outcomes["time"].astype("string").str.strip()
clock = outcomes["kickoff_time"].str.upper().str.extract(r"^\s*(\d{1,2}:\d{2}\s*[AP]M)\s+ET\s*$", expand=False)
if clock.isna().any():
    raise ValueError(f"Missing or unexpected kickoff times: {outcomes.loc[clock.isna(), 'time'].unique()}")
clock = clock.str.replace(r"\s+", "", regex=True)
kickoff_text = outcomes["date_id"].dt.strftime("%Y-%m-%d") + " " + clock
kickoff_local = pd.to_datetime(kickoff_text, format="%Y-%m-%d %I:%M%p", errors="raise")
outcomes["kickoff_utc"] = kickoff_local.dt.tz_localize("America/New_York").dt.tz_convert("UTC")
weather["weather_hour_utc"] = pd.to_datetime(weather["time"], format="mixed", utc=True, errors="raise")
if weather["weather_hour_utc"].isna().any() or weather["weather_hour_utc"].duplicated().any():
    raise ValueError("Weather timestamps must be present and unique.")
if weather["weather_hour_utc"].ne(weather["weather_hour_utc"].dt.floor("h")).any():
    raise ValueError("Expected weather readings exactly on the hour.")
print(games.head())
print(outcomes.head())
print(attendance.head())
print(weather.head())

# Transform attendance data from wide to long format.
week_columns = attendance.columns[attendance.columns.str.fullmatch(r"Week\s+\d+")].tolist()
if not week_columns:
    raise ValueError("No weekly attendance columns were found.")
attendance_long = attendance.melt(
    id_vars=["season", "team_id"], value_vars=week_columns, var_name="week", value_name="attendance"
)
attendance_long["week"] = attendance_long["week"].str.extract(r"(\d+)", expand=False).astype(int)
values = attendance_long["attendance"].astype("string").str.replace(",", "", regex=False).str.strip()
values = values.replace({
    "": pd.NA,
    "-": pd.NA,
    "--": pd.NA,
    "—": pd.NA,
    "N/A": pd.NA,
    "Bye": pd.NA,
})

attendance_long["attendance"] = pd.to_numeric(values, errors="raise").astype("Int64")

packers_attendance = attendance_long.loc[
    attendance_long["team_id"].eq("GB") & attendance_long["attendance"].notna(),
    ["season", "week", "attendance"],
]


# Calculate prior win percentage using all Packers outcomes before filtering home games.
outcomes = outcomes.sort_values(["season", "date_id"]).reset_index(drop=True)
result = outcomes["Won"].astype("string").str.strip().str.upper().replace("", pd.NA)
unknown = result.notna() & ~result.isin(["W", "L", "T"])

outcomes["win_credit"] = result.map({"W": 1.0, "L": 0.0, "T": 0.5}).fillna(0.0)
outcomes["completed"] = result.isin(["W", "L", "T"]).astype(int)
wins_before = outcomes.groupby("season")["win_credit"].cumsum() - outcomes["win_credit"]
games_before = outcomes.groupby("season")["completed"].cumsum() - outcomes["completed"]
outcomes["win_pct_before_game"] = wins_before / games_before.replace(0, float("nan"))

is_home = games["home_team_id"].eq("GB")
is_away = games["opponent_id"].eq("GB")
print(f"Kept {int(is_home.sum())} and excluded {int(is_away.sum())} Packers away games.")

#Filter out all games that are not Packers home games.
games = games[games["home_team_id"] == "GB"]
home_games = games.loc[is_home].copy()
outcome_columns = ["season", "date_id", "opponent_id", "Day", "kickoff_time", "kickoff_utc", "win_pct_before_game"]
home_games = home_games.merge(
    outcomes[outcome_columns], on=["season", "date_id", "opponent_id"], how="left",
    validate="one_to_one", indicator=True
)

home_games = home_games.drop(columns="_merge")
home_games = home_games.merge(packers_attendance, on=["season", "week"], how="left", validate="one_to_one")

# Build the dimensions and facts
used_ids = pd.concat([games["home_team_id"], games["opponent_id"], attendance["team_id"], outcomes["opponent_id"]])
dim_team = pd.DataFrame({"team_id": used_ids.drop_duplicates().sort_values().to_numpy()})
dim_team["team_name"] = dim_team["team_id"].map(TEAM_NAMES)
dim_date = home_games[["date_id", "season", "Day"]].rename(columns={"Day": "day_of_week"}).copy()
if dim_date.groupby("date_id")["season"].nunique().gt(1).any():
    raise ValueError("A game date is assigned to multiple seasons.")
if dim_date["day_of_week"].ne(dim_date["date_id"].dt.strftime("%a")).any():
    raise ValueError("Outcome Day does not match the calendar date.")
dim_date = dim_date.drop_duplicates("date_id").sort_values("date_id").reset_index(drop=True)
holidays = USFederalHolidayCalendar().holidays(start=dim_date["date_id"].min(), end=dim_date["date_id"].max())
dim_date["is_holiday"] = dim_date["date_id"].isin(holidays)


fact_game = home_games.rename(columns={"away_score": "opp_score"})
fact_game = fact_game[
    ["game_id", "date_id", "home_team_id", "opponent_id", "kickoff_time", "week", "game_type",
     "home_score", "opp_score", "attendance"]
].copy()
weather_games = home_games[["game_id", "kickoff_utc"]].copy()
weather_games["weather_hour_utc"] = weather_games["kickoff_utc"].dt.floor("h")
weather_games = weather_games.merge(
    weather[["weather_hour_utc", "prcp","temp", "wspd", "rhum"]], on="weather_hour_utc", how="left",
    validate="many_to_one", indicator=True
)
missing_weather = int(weather_games["_merge"].eq("left_only").sum())
fact_weather = weather_games.rename(columns={"prcp": "percip_mm", "rhum": "relative_humidity", "temp": "temp_c", "wspd": "wind_speed_kmh"})
fact_weather = fact_weather[["game_id", "temp_c", "wind_speed_kmh", "percip_mm", "relative_humidity"]].copy()

# Check nulls, schema rules, and foreign keys BEFORE writing any clean CSV.
for column in ["week", "home_score", "opp_score", "attendance"]:
    fact_game[column] = pd.to_numeric(fact_game[column], errors="raise").astype("Int64")
for column in ["temp_c", "wind_speed_kmh", "percip_mm", "relative_humidity"]:
    fact_weather[column] = pd.to_numeric(fact_weather[column], errors="raise")

# Percentage of missing values in each column
missing_pct_date = dim_date.isna().mean() * 100
missing_pct_team = dim_team.isna().mean() * 100
missing_pct_game = fact_game.isna().mean() * 100
missing_pct_weather = fact_weather.isna().mean() * 100
print("Missing percentage for dim_date:\n", missing_pct_date)
print("Missing percentage for dim_team:\n", missing_pct_team)
print("Missing percentage for fact_game:\n", missing_pct_game)
print("Missing percentage for fact_weather:\n", missing_pct_weather)

# Save tables to data/clean
dim_date.to_csv(CLEAN_DIR / "dim_date.csv", index=False)
dim_team.to_csv(CLEAN_DIR / "dim_team.csv", index=False)
fact_game.to_csv(CLEAN_DIR / "fact_game.csv", index=False)
fact_weather.to_csv(CLEAN_DIR / "fact_weather.csv", index=False)