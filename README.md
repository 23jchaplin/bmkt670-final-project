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
| [Pro-Football-Reference](https://www.pro-football-reference.com/teams/gnb/) | Game-by-game logs: date, opponent, result, season, attendance | Exported 2025 games and attendence to CSV 9/23/2026 |
| [NFL Stadiums Database](https://www.worldplacesexplained.com/data/nfl-stadiums-database) | Stadium, team, city, capacity, surface | Exported to CSV 9/23/2026 |
| [NFL Data API](https://nfldata.org/) | Date, temp, wind, stadium, roof type, and scores for games | Free API |

## How to Run
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Pull the data: run each script in etl/ (e.g., python etl/extract_games.py)  
4. Build the database: run sql/schema.sql in pgAdmin or psql
5. Confirm it worked: python db_check.py (should print all table names)

## AI Usage
