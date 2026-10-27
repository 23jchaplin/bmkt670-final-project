DROP TABLE IF EXISTS fact_game CASCADE;
DROP TABLE IF EXISTS fact_weather CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS ml_feature;
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

-- One row represents one Green Bay Packers home game.
CREATE TABLE fact_game (
    game_id TEXT PRIMARY KEY,
    date_id DATE NOT NULL REFERENCES dim_date (date_id),
    home_team_id TEXT NOT NULL REFERENCES dim_team (team_id),
    opponent_id TEXT NOT NULL REFERENCES dim_team (team_id),
    -- Store the kickoff instant in UTC.
    kickoff_time TIMESTAMPTZ,
    week INTEGER NOT NULL CHECK (week > 0),
    game_type TEXT NOT NULL,
    home_score INTEGER CHECK (home_score >= 0),
    opp_score INTEGER CHECK (opp_score >= 0),
    attendance INTEGER CHECK (attendance >= 0),
    CHECK (home_team_id <> opponent_id)
);


-- One row represents the weather selected for one game's kickoff.
CREATE TABLE fact_weather (
    weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id TEXT NOT NULL UNIQUE REFERENCES fact_game (game_id),
    temp_c NUMERIC,
    wind_speed_kmh NUMERIC CHECK (wind_speed_kmh >= 0),
    percip_mm NUMERIC CHECK (percip_mm >= 0),
    relative_humidity NUMERIC CHECK (relative_humidity BETWEEN 0 AND 100)
);

-- One row per game predicted by the selected model.
CREATE TABLE predictions (
    game_id TEXT PRIMARY KEY REFERENCES fact_game (game_id),
    split TEXT NOT NULL CHECK (split IN ('train', 'validate', 'test')),
    actual INTEGER CHECK (actual >= 0),
    predicted DOUBLE PRECISION NOT NULL,
    error DOUBLE PRECISION GENERATED ALWAYS AS (actual - predicted) STORED,
    model_name TEXT NOT NULL
);

-- One row per Packers home game at Lambeau Field (regular season and playoffs).
-- Predict attendance before kickoff. IDs, date, season, and split are metadata.
CREATE TABLE ml_feature (
    game_id TEXT PRIMARY KEY REFERENCES fact_game (game_id),
    date_id DATE NOT NULL REFERENCES dim_date (date_id),
    season INTEGER NOT NULL CHECK (season BETWEEN 2021 AND 2025),
    attendance INTEGER CHECK (attendance >= 0),
    kickoff_time TIMESTAMPTZ,
    kickoff_afternoon SMALLINT NOT NULL CHECK (kickoff_afternoon IN (0, 1)),
    kickoff_early_evening SMALLINT NOT NULL CHECK (kickoff_early_evening IN (0, 1)),
    kickoff_prime_time SMALLINT NOT NULL CHECK (kickoff_prime_time IN (0, 1)),
    kickoff_late SMALLINT NOT NULL CHECK (kickoff_late IN (0, 1)),
    temp_c NUMERIC,
    wind_speed_kmh NUMERIC CHECK (wind_speed_kmh >= 0),
    percip_mm NUMERIC CHECK (percip_mm >= 0),
    relative_humidity NUMERIC CHECK (relative_humidity BETWEEN 0 AND 100),
    week INTEGER NOT NULL CHECK (week > 0),
    is_holiday SMALLINT NOT NULL CHECK (is_holiday IN (0, 1)),
    is_postseason SMALLINT NOT NULL CHECK (is_postseason IN (0, 1)),
    day_monday SMALLINT NOT NULL CHECK (day_monday IN (0, 1)),
    day_tuesday SMALLINT NOT NULL CHECK (day_tuesday IN (0, 1)),
    day_wednesday SMALLINT NOT NULL CHECK (day_wednesday IN (0, 1)),
    day_thursday SMALLINT NOT NULL CHECK (day_thursday IN (0, 1)),
    day_friday SMALLINT NOT NULL CHECK (day_friday IN (0, 1)),
    day_saturday SMALLINT NOT NULL CHECK (day_saturday IN (0, 1)),
    days_since_last_home_game INTEGER CHECK (days_since_last_home_game >= 0),
    split TEXT NOT NULL CHECK (split IN ('train', 'validate', 'test')),
    win_pct_before_game NUMERIC CHECK (win_pct_before_game BETWEEN 0 AND 1),
    CHECK (day_monday + day_tuesday + day_wednesday + day_thursday + day_friday + day_saturday <= 1),
    CHECK (
        (season BETWEEN 2021 AND 2023 AND split = 'train')
        OR (season = 2024 AND split = 'validate')
        OR (season = 2025 AND split = 'test')
    )
);