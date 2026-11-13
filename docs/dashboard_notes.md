# Dashboard Purpose
This dashboard is designed for the Green Bay Packers’ game-day operations manager. It supports staffing and resource planning by showing historical attendance, evaluating prediction accuracy, and estimating attendance for upcoming home games.
## Purpose of Each Page
### Page 1: What happened?
How has home-game attendance varied across seasons and days of the week? A season filter allows users to explore attendance patterns. Charts show attendance by season and weekday, while metrics display the number of home games, average attendance, and stadium capacity.

### Page 2: How good are the predictions?
How accurately does the model predict attendance compared with the baseline? Metrics compare the baseline and model MAE for the 2024 validation set and the model MAE for the 2025 test set. A predicted-versus-actual chart shows overall accuracy, and a table highlights the largest errors. Errors above 1.5 times the reference MAE are flagged as larger than usual; those above twice the reference MAE are flagged as unusual.

### Page 3: What should we do?
How can attendance predictions inform game-day planning? This page provides two recommendations, one limitation, and an interactive prediction tool using known pregame inputs. Three AI-generated summaries explain predictions for selected 2025 games.

## AI Feature and Summary Checks
**Prompt:** You are writing for a stadium operations manager. In 2–3 plain sentences, summarize this attendance prediction.
Translate values into natural language: do not mention feature names, binary flags, or raw 0/1 values. Connect the game context to the attendance outlook with cautious language such as "supported," "pointed to," or "likely helped." Do not claim that a feature caused attendance, and do not invent facts. If a value is missing or neutral, leave it out.

| Game | AI summary | What I found |
| :--- | ---: | :--- |
| 2025_01_DET_GB | The model predicted 77,935 fans for the Sunday game against the Detroit Lions, 696 above the actual attendance of 77,239. The long 245-day gap since the prior home game likely helped support the strong attendance outlook, despite the Packers entering with no wins. |	Attendance figures and the 696-fan overprediction match. Sunday and season-opener details also match. |
| 2025_10_PHI_GB | Attendance was predicted at 78,047 fans, just 207 below the actual crowd of 78,254. The Monday matchup against the Philadelphia Eagles, eight days after the prior home game, and the Packers’ 69% win rate likely supported the strong turnout. |	Figures and the 207-fan underprediction match, as does Monday. |
| 2025_06_CIN_GB | Attendance was predicted at about 78,232 fans, just 45 below the actual crowd of 78,277. The Sunday matchup against the Cincinnati Bengals, a 31-day gap since the prior home game, and the Packers’ 62% win rate likely supported the strong turnout. | Attendance figures, the 45-fan underprediction, Sunday, and the gap match. The win rate should be reported as 62.5%. |

**Estimated cost per run:** Eight summaries at approximately 300 tokens each total 2,400 tokens, plus any prompt tokens excluded from that estimate. The preliminary estimate is under $0.01 per run, but this requires confirmation using the selected model’s input and output prices.

### One Thing I’d Add With More Time
I would add a prediction range based on observed model errors. Showing a likely attendance range alongside the point estimate would help the operations manager plan staffing while accounting for uncertainty.