-- One row represents one NFL team.
CREATE TABLE dim_team (
    team_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name TEXT NOT NULL
);

-- One row represents one NFL game date/week.
CREATE TABLE dim_date (
    date_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_date DATE NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_week TEXT NOT NULL
);

-- One row represents one NFL stadium.
CREATE TABLE dim_stadium (
    stadium_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stadium_name TEXT NOT NULL UNIQUE,
    city TEXT,
    state TEXT,
    capacity INTEGER,
    roof_type TEXT,
    surface TEXT
);

-- One row represents one NFL game.
CREATE TABLE fact_game (
    game_id TEXT PRIMARY KEY,

    date_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    stadium_id INTEGER,

    game_time TIME,
    game_type TEXT,

    home_score INTEGER,
    away_score INTEGER,
    overtime BOOLEAN,

    game_roof TEXT,
    temp NUMERIC,
    wind NUMERIC,

    spread_line NUMERIC,
    total_line NUMERIC,
    div_game BOOLEAN,

    attendance INTEGER,

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    FOREIGN KEY (home_team_id)
        REFERENCES dim_team(team_id),

    FOREIGN KEY (away_team_id)
        REFERENCES dim_team(team_id),

    FOREIGN KEY (stadium_id)
        REFERENCES dim_stadium(stadium_id)
);