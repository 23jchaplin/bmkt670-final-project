| Table | Column | % missing | Decision | Why |
| :---- | :---- | :--------- | :-- | :------- |
| fact_game | attendance | 2.32% | Leave as NULL; retain the row | Attendance is missing for Divisional game. An overall median may not represent playoff attendance accurately. Keep the remaining game information; no rows are dropped.
| ml_feature | attendance | 2.32% | Leave as NULL; retain the row | Attendance is missing for Divisional game. An overall median may not represent playoff attendance accurately. Keep the remaining game information; no rows are dropped.
| ml_feature | days_since_last_game | 2.32% | Fill with 0 | The first game is null as there is no previous date to calculate from |
| ml_feature | win_pct_before_game | 2.32% | Fill with 0 | First game of 2025 season, no prevoius game to calculate from |