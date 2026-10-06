# Field sources: Packers attendance project


| Table | Field | Comes from | How | Used for |
| :---- | :---- | :--------- | :-- | :------- |
| dim_team | team_id | Created by Postgres | Auto-numbered with `GENERATED ALWAYS AS IDENTITY`. | Primary key; links games to home and away teams. |
| dim_team | team_code | NFL Data API | Collect distinct abbreviations from `home_team` and `away_team`. | Unique lookup key for matching source games to teams. |
| dim_team | team_name | Created | Maintain a checked abbreviation-to-full-name lookup, such as `GB` → Green Bay Packers and `ATL` → Atlanta Falcons. | Dashboard: readable team and opponent names; matches attendance team names to codes. |
| dim_date | date_id | Created by Postgres | Auto-numbered with `GENERATED ALWAYS AS IDENTITY`. | Primary key; links games to their date records. |
| dim_date | game_date | NFL Data API | Convert `gameday` to a date. | Dashboard: game date; orders past games for historical features. |
| dim_date | season | NFL Data API | Copy `season`; use the supplied NFL season rather than the calendar year of the date. | Feature; time-based training/test splits; attendance matching. |
| dim_date | week | NFL Data API | Convert `week` to an integer. | Feature; matches weekly attendance to the game. |
| dim_date | day_of_week | Calculated in Python | Calculate `pd.to_datetime(gameday).dt.day_name()`. | Feature; dashboard: scheduling and staffing context. |
| dim_stadium | stadium_id | Created by Postgres | Auto-numbered with `GENERATED ALWAYS AS IDENTITY`. | Primary key; links games to stadiums. |
| dim_stadium | stadium_name | NFL Stadiums Database | Copy `name`; use an explicit alias lookup when other sources use different stadium names. | Dashboard: venue name; lookup for linking game venues. |
| dim_stadium | city | NFL Stadiums Database | Copy `city`. | Dashboard: venue location. |
| dim_stadium | state | NFL Stadiums Database | Copy `state`. | Dashboard: venue location. |
| dim_stadium | capacity | NFL Stadiums Database | Convert `capacity` to an integer after removing any thousands separators. | Input to occupancy calculation: attendance ÷ capacity; dashboard capacity. |
| dim_stadium | roof_type | NFL Stadiums Database | Copy `roof` as the stadium's general roof type. | Input to weather-related features; dashboard venue conditions. |
| dim_stadium | surface | NFL Stadiums Database | Copy `surface`. | Dashboard: playing surface. |
| fact_game | game_id | NFL Data API | Copy `game_id` as text. | Primary key; uniquely identifies each game and prevents duplicate game records. |
| fact_game | date_id | Joined | Match API `gameday`, `season`, and `week` to `dim_date`; retrieve `date_id`. | Foreign key: links to `dim_date`. |
| fact_game | home_team_id | Joined | Match API `home_team` to `dim_team.team_code`; retrieve `team_id`. | Foreign key: home team; filters Packers home games. |
| fact_game | away_team_id | Joined | Match API `away_team` to `dim_team.team_code`; retrieve `team_id`. | Foreign key: away team; opponent feature and dashboard name. |
| fact_game | stadium_id | Joined | Match API `stadium` to `dim_stadium.stadium_name` using checked aliases; retrieve `stadium_id`. | Foreign key: venue; links capacity and filters Lambeau Field games. |
| fact_game | game_time | NFL Data API | Parse `gametime` as a time; document the source timezone and use it consistently. | Input to kickoff-hour feature; dashboard: kickoff time. |
| fact_game | game_type | NFL Data API | Copy `game_type`. | Feature; distinguishes game types and restricts attendance matching to supported games. |
| fact_game | home_score | NFL Data API | Convert `home_score` to an integer; preserve missing values for unplayed games. | Input to prior-game wins and team performance features. |
| fact_game | away_score | NFL Data API | Convert `away_score` to an integer; preserve missing values for unplayed games. | Input to prior-game wins and opponent performance features. |
| fact_game | overtime | NFL Data API | Convert `overtime` to a Boolean; preserve unknown values as NULL. | Dashboard: historical game results. |
| fact_game | game_roof | NFL Data API | Copy `roof` for the particular game, separately from the stadium's general roof type. | Input to weather exposure features; dashboard game conditions. |
| fact_game | temp | NFL Data API | Convert `temp` to numeric; retain the source units and document them before loading. Preserve missing readings as NULL. | Input to weather features; historical dashboard conditions. |
| fact_game | wind | NFL Data API | Convert `wind` to numeric; retain the source units and document them before loading. Preserve missing readings as NULL. | Input to weather features; historical dashboard conditions. |
| fact_game | spread_line | NFL Data API | Convert `spread_line` to numeric; preserve missing values. | Potential feature: expected competitiveness, using a line available before prediction. |
| fact_game | total_line | NFL Data API | Convert `total_line` to numeric; preserve missing values. | Potential feature: expected combined scoring, using a line available before prediction. |
| fact_game | div_game | NFL Data API | Convert `div_game` to a Boolean. | Feature: division matchup; dashboard rivalry context. |
| fact_game | attendance | Pro-Football-Reference | Reshape `Week 1`–`Week 18` into week/attendance rows. Assign season from the source file, map `Tm` to the home team's code, and match by season, week, and home team for regular-season games. Check `Stadium` against the game venue. Convert attendance to integer; retain missing values as NULL. | Training/testing target: past attendance; dashboard: actual attendance and occupancy. |

## Source fields used but not stored as separate columns

| Source | Source field | Use without separate storage |
| :----- | :----------- | :--------------------------- |
| Pro-Football-Reference | `Tm` | Match the attendance row's team name to `dim_team.team_code` using the checked team lookup. |
| Pro-Football-Reference | `Week 1`–`Week 18` column headings | Extract the week number when reshaping the attendance file; match it to `dim_date.week`. The cell value becomes `fact_game.attendance`. |

The attendance file's season (2025 or 2026) comes from its filename/source year and is used to match games; it is represented by `dim_date.season`.

