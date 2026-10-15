# Field sources: Packers attendance project

| Table | Field | Comes from | How | Used for |
| :---- | :---- | :--------- | :-- | :------- |
| dim_team | team_id | NFL Data API | Team abbreviation from `home_team` or `away_team`, such as GB or ATL | Key: links games to opponents |
| dim_team | team_name | Pro-Football-Reference | `Opp` column in outcomes_2025 | Readable opponent name for the ML table and dashboard |
| dim_date | date_id | Pro-Football-Reference | 	Game date, converted to a date type | Key: links each game to its date |
| dim_date | season | Pro-Football-Reference or a rule | Jan and Feb games belong to the previous year's season | Feature; also splits data by time for modeling |
| dim_date | day_of_week | Pro-Football-Reference | `Day` column in outcomes_2025| Feature |
| dim_date | is_holiday | Calculated in Python | pandas U.S. federal holiday calendar | Feature |
| fact_game | game_id | NFL Data API | Use the supplied `game_id` | Key: one unique ID per game |
| fact_game | date_id | Pro-Football-Reference | Game date | Key: links to dim_date |
| fact_game | home_team_id | NFL Data API | Value in `home_team` | Key: links to dim_team and identifies Packers home games |
| fact_game | opponent_id | NFL Data API | Use `away_team` after filtering to Packers home games | Key: links the visiting opponent to dim_team |
| fact_game | kickoff_time | Pro-Football-Reference outcomes | Convert the `time` column from ET to UTC. | Feature representing kickoff time in UTC |
| fact_game | week | NFL Data API | Value in `week` | Feature; also matches games to weekly attendance |
| fact_game | game_type | NFL Data API | Value in `game_type`, such as REG or WC | Identifies regular-season and playoff games |
| fact_game | home_score | Pro-Football-Reference outcomes | Value in `Tm`; this is the Packers’ score | 	Builds the win-percentage feature (next week) |
| fact_game | opp_score | Pro-Football-Reference outcomes | Value in `ScoreOpp`; this is the Packers’ score | 	Builds the win-percentage feature (next week) |
| fact_game | attendance | Pro-Football-Reference attendance | Weekly attendance table: Packers row, matched to each game by week | Training the model: past attendance it learns from and is tested against |
| fact_weather | weather_id | created by postgres | Autonumbered | Key: primary key |
| fact_weather | game_id | matched in pyhton | The weather hour closest to kickoff | Key: links to fact_game |
| fact_weather | temp_c | Meteostat Python Library | Numeric value in `temp` | Weather feature |
| fact_weather | wind_speed_kmh | Meteostat Python Library | Numeric value in `wspd` | Weather feature |
| fact_weather | percip_mm | Meteostat Python Library | Numeric value in `prcp` | Weather feature |
| fact_weather | relative_humidity | Meteostat Python Library | Numeric value in `rhum` | Weather feature |
| ml_feature | game_id | Joined | Copy fact_game.game_id after selecting GB home games at Lambeau Field, REG or playoffs. | Primary/foreign key; identifier, excluded from model inputs. |
| ml_feature | date_id | Joined | Copy fact_game.date_id. | Date metadata; chronological ordering, excluded from model inputs. |
| ml_feature | season | Joined | Copy dim_date.season through fact_game.date_id. | Split metadata, excluded from model inputs. |
| ml_feature | attendance | Joined | Copy fact_game.attendance; retain NULL for missing actual attendance. | Target; never include in model input features. |
| ml_feature | week | Joined | Copy fact_game.week from the pregame schedule. | Numeric feature. |
| ml_feature | is_holiday | Calculated in Python | Convert joined dim_date.is_holiday to integer 0 or 1. | Encoded binary calendar feature. |
| ml_feature | is_postseason | Calculated in Python | Encode game_type REG as 0 and WC, DIV, CON, SB as 1; reject unknown types and exclude preseason. | Encoded binary game-type feature. |
| ml_feature | day_monday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for monday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | day_tuesday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for tuesday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | day_wednesday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for wednesday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | day_thursday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for thursday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | day_friday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for friday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | day_saturday | Calculated in Python | Encode joined dim_date.day_of_week as 1 for saturday, otherwise 0. Sunday is the all-zero reference category. | Encoded categorical weekday feature. |
| ml_feature | prior_3_home_avg_attendance | Calculated in Python | Sort selected home games by date; attendance.shift(1).rolling(3, min_periods=1).mean(). Average known values in the previous three games, across seasons; NULL if none are known. | Derived feature; recent home attendance available before kickoff. |
| ml_feature | days_since_last_home_game | Calculated in Python | Day of current game - day of last game | numeric feature |
| ml_feature | win_pct_before_game | Calculated in Python | takes number of wins before game divided by number of total cames | numeric feature |
| ml_feature | split | Calculated in Python | Season 2021-2023 = train; 2024 = validate; 2025 = test. Use NFL season, including January/February postseason games. | Time-based partition label, excluded from model inputs. |

Source fields used but not stored:
- Week 1–Week 18 headings — attendance: supply the week number when reshaping the attendance data.
- Bye — attendance: identifies weeks without a game; these entries are excluded.
- Season supplies the season needed to match attendance to API games.
- Date and opponent name — outcomes: match the kickoff-time record to the correct API game.