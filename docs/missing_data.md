| Table | Column | % missing | Decision | Why |
| :---- | :---- | :--------- | :-- | :------- |
| fact_game | attendance | 2.32% | Leave as NULL; retain the row | Attendance is missing for Divisional game. An overall median may not represent playoff attendance accurately. Keep the remaining game information; no rows are dropped.