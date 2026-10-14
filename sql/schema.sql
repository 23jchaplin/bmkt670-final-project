DROP TABLE IF EXISTS fact_game CASCADE;
DROP TABLE IF EXISTS fact_weather CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;

-- One row represents one NFL team.
CREATE TABLE dim_team (
    team_id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL
);

-- One row represents one game date and its calendar attributes.
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    season INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_holiday BOOLEAN NOT NULL
);

-- One row represents the weather selected for one game's kickoff.
CREATE TABLE fact_weather (
    weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game (game_id),
    temp NUMERIC,
    wind NUMERIC CHECK (wind >= 0),
    percip_mm NUMERIC CHECK (percip_mm >= 0),
    relative_humidity NUMERIC CHECK (relative_humidity BETWEEN 0 AND 100)
);

-- One row represents one Green Bay Packers home game.
CREATE TABLE fact_game (
    game_id TEXT PRIMARY KEY,
    date_id DATE NOT NULL REFERENCES dim_date (date_id),
    home_team_id TEXT NOT NULL REFERENCES dim_team (team_id),
    opponent_id TEXT NOT NULL REFERENCES dim_team (team_id),
    stadium_id TEXT NOT NULL REFERENCES dim_stadium (stadium_id),
    -- Preserve the source's time-zone label
    kickoff_time TEXT,
    week INTEGER NOT NULL CHECK (week > 0),
    game_type TEXT NOT NULL,
    home_score INTEGER CHECK (home_score >= 0),
    opp_score INTEGER CHECK (opp_score >= 0),
    attendance INTEGER CHECK (attendance >= 0),
    CHECK (home_team_id <> opponent_id)
);
