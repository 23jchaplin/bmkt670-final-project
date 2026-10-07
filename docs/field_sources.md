# Field sources: Packers attendance project

| Table | Field | Comes from | How | Used for |
| :---- | :---- | :--------- | :-- | :------- |
| dim_team | team_id | NFL Data API | Team abbreviation from `home_team` or `away_team`, such as GB or ATL | Key: links games to opponents |
| dim_team | team_name | Pro-Football-Reference | `Opp` column in outcomes_2025 | Readable opponent name for the ML table and dashboard |
| dim_date | date_id | Pro-Football-Reference | 	Game date, converted to a date type | Key: links each game to its date |
| dim_date | season | Pro-Football-Reference or a rule | Jan and Feb games belong to the previous year's season | Feature; also splits data by time for modeling |
| dim_date | day_of_week | Pro-Football-Reference | `Day` column in outcomes_2025| Feature |
| dim_date | is_holiday | Calculated in Python | pandas U.S. federal holiday calendar | Feature |
| dim_stadium | stadium_id | NFL Stadium Database | Use the stadium’s `slug`, such as `lambeau-field` | Key: links games to stadium information |
| dim_stadium | stadium_name | NFL Stadium Database | Value in `name` | Readable stadium name for the dashboard |
| dim_stadium | city | NFL Stadium Database | Value in `city` | Stadium location shown on the dashboard |
| dim_stadium | state_code | NFL Stadium Database | Value in `state_code` | Stadium location shown on the dashboard |
| dim_stadium | capacity | NFL Stadium Database | Numeric value in `capacity` | Feature; input for calculating capacity percentage |
| dim_stadium | opened | NFL Stadium Database | Opening year in `opened` | Input for calculating stadium age |
| fact_game | game_id | NFL Data API | Use the supplied `game_id` | Key: one unique ID per game |
| fact_game | date_id | Pro-Football-Reference | Game date | Key: links to dim_date |
| fact_game | home_team_id | NFL Data API | Value in `home_team` | Key: links to dim_team and identifies Packers home games |
| fact_game | opponent_id | NFL Data API | Use `away_team` after filtering to Packers home games | Key: links the visiting opponent to dim_team |
| fact_game | stadium_id | NFL Stadium Database | Stadium name | Key: links to dim_stadium |
| fact_game | kickoff_time | Pro-Football-Reference outcomes |  `time` column | Feature representing kickoff time |
| fact_game | week | NFL Data API | Value in `week` | Feature; also matches games to weekly attendance |
| fact_game | game_type | NFL Data API | Value in `game_type`, such as REG or WC | Identifies regular-season and playoff games |
| fact_game | home_score | Pro-Football-Reference outcomes | Value in `Tm`; this is the Packers’ score | 	Builds the win-percentage feature (next week) |
| fact_game | opp_score | Pro-Football-Reference outcomes | Value in `Opp`; this is the Packers’ score | 	Builds the win-percentage feature (next week) |
| fact_game | attendance | Pro-Football-Reference attendance | Weekly attendance table: Packers row, matched to each game by week | Training the model: past attendance it learns from and is tested against |
| fact_game | roof | NFL Data API | Value in `roof` | Stadium condition; helps interpret missing weather values if enclosed |
| fact_game | surface | NFL Data API | Value in `surface` | playing-surface feature |
| fact_game | temp | NFL Data API | Numeric value in `temp` | Weather feature |
| fact_game | wind | NFL Data API | Numeric value in `wind` | Weather feature |

Source fields used but not stored:
- Tm — attendance: selects the Green Bay Packers row.
- Week 1–Week 18 headings — attendance: supply the week number when reshaping the attendance data.
- Bye — attendance: identifies weeks without a game; these entries are excluded.
- Season supplies the season needed to match attendance to API games.
- Date and opponent name — outcomes: match the kickoff-time record to the correct API game.