# Data Analytics Final Project

## Business Question
How many fans will attend an upcoming Green Bay Packers home game against the Atlanta Falcons at Lambeau Field?

## Target Variable
Game Attendance

## Prediction Unit
One row in my ML feature table = one game

## Data Sources
| Source | What it provides | Access |
| --- | --- | --- |
| [2021 - 2025 NFL Attendance Data - Pro-Football-Reference.com](https://www.pro-football-reference.com/years/2025/attendance.htm) | 2025 NFL attendance | Downloaded to CSV 9/22 by clicking the "Share & Export" dropdown and selecting "Get table as CSV" |
| [NFL Stadiums Database](https://www.worldplacesexplained.com/data/nfl-stadiums-database) | Stadium, team, city, capacity, surface | Downloaded to CSV 9/22 by selecting the "Download CSV" button |
| [NFL Data API](https://nfldata.org/) | Date, temp, wind, stadium, roof type, teams, and scores | Free API |
| [2021 - 2025 Outcomes - Pro-Football-Reference.com](https://www.pro-football-reference.com/teeams/gnb/2025.htm) | Day, date and time, outcome of packers games | Downloaded to CSV 9/22 by clicking the "Share & Export" dropdown and selecting "Get table as CSV" Removed Bye week|

## How to Run
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Pull the data: run each script in etl/ (e.g., python etl/extract_games.py)  
4. Build the database: run sql/schema.sql in pgAdmin or psql
5. Run transform.py to combine and align the source datasets, select Packers home games played at Lambeau Field, and prepare the cleaned tables. It preserves unknown attendance as missing, calculates days_since_last_home_game and win_pct_before_game, encodes calendar and game-type features, and assigns the training, validation, and test splits.
6. Run your loading script to load the cleaned tables into Postgres.
7. Confirm it worked: python db_check.py (should print all table names)
8. Run the modeling script: model/model.py. This script reads ml_feature from Postgres, separates the data using the existing splits, and excludes rows with missing attendance from model fitting and evaluation. It creates training-data charts in docs/figures/, calculates the baseline, compares regression models using validation MAE, evaluates the selected random forest on the test data, and reports its top features. Then saves it to sql table predictions.

## AI Usage

Used ChatGPT-6.1 Sol for:
 - Understanding the data: Explaining fields such as spread_line, total_line, and div_game.
 - Creating the data dictionary: Mapping database fields to their sources and explaining each field’s purpose.
 - Designing the database: Organizing dimension and fact tables and creating sql/schema.sql with data types, primary keys, and foreign keys.
 - Troubleshooting: Interpreting the missing-table error in db_check.py and identifying steps to check the database and create the tables.
 - Helped write and revise Python code for feature engineering, including days since the previous home game, weekday encoding, and holiday and postseason indicators.
 - Helped create charts using training data and describe the patterns shown.
 - Helped adapt regression models to predict attendance and compare their validation scores.
 - Provided guidance on handling missing attendance and feature values.
 - Helped write code to evaluate the selected model on test data and identify its most important features.
 - Helped design a predictions table and code for saving model results to Postgres.
 - Helped revise project documentation, including the explanation of model selection, results, and limitations.
