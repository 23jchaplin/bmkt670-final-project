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
| [2025 NFL Attendance Data - Pro-Football-Reference.com](https://www.pro-football-reference.com/years/2025/attendance.htm) | 2025 NFL attendance | Downloaded to CSV 9/22 by clicking the "Share & Export" dropdown and selecting "Get table as CSV" |
| [NFL Stadiums Database](https://www.worldplacesexplained.com/data/nfl-stadiums-database) | Stadium, team, city, capacity, surface | Downloaded to CSV 9/22 by selecting the "Download CSV" button |
| [NFL Data API](https://nfldata.org/) | Date, temp, wind, stadium, roof type, teams, and scores | Free API |
| [2026 NFL Attendance Data - Pro-Football-Reference.com](https://www.pro-football-reference.com/years/2026/attendance.htm) | 2026 NFL attendance | Downloaded to CSV 10/6 by clicking the "Share & Export" dropdown and selecting "Get table as CSV" |

## How to Run
1. Create and activate a virtual environment
2. Install packages: pip install -r requirements.txt
3. Pull the data: run each script in etl/ (e.g., python etl/extract_games.py)  
4. Build the database: run sql/schema.sql in pgAdmin or psql
5. Confirm it worked: python db_check.py (should print all table names)

## AI Usage
