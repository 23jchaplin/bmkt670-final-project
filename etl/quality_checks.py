import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = PROJECT_ROOT / "data" / "clean"
load_dotenv(PROJECT_ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "packers_attendance"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
}

TABLES = ("dim_team", "dim_date", "fact_game", "fact_weather")
MISSING_LIMIT = 5.0
results = []

connection = psycopg2.connect(**DB_CONFIG)
connection.set_session(readonly=True, isolation_level="REPEATABLE READ")
cursor = connection.cursor()
cursor.execute("SET search_path TO public")

# 1. Row count checks: Compare the number of rows in the database with the clean CSV files
for table in TABLES:
    query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table))
    cursor.execute(query)
    count = cursor.fetchone()[0]
    passed = count > 0
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] {table} row count: {count}")

    path = CLEAN_DIR / f"{table}.csv"
    file = path.open(newline="", encoding="utf-8-sig")
    reader = csv.reader(file)
    header = next(reader, None)
    csv_count = sum(1 for row in reader if row)
    file.close()
    difference = count - csv_count
    passed = header is not None and difference == 0
    results.append(passed)
    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"{table} database minus clean CSV rows: {difference} "
        f"(DB={count}, CSV={csv_count})"
    )
# 2. Duplicate key checks: Ensure there are no duplicate or NULL values in primary key columns
duplicate_keys = (
    ("fact_game", "game_id"),
    ("fact_weather", "weather_id"),
    ("fact_weather", "game_id"),
)
for table, column in duplicate_keys:
    query = sql.SQL("SELECT COUNT(*) - COUNT(DISTINCT {}) FROM {}").format(
        sql.Identifier(column), sql.Identifier(table)
    )
    cursor.execute(query)
    number = cursor.fetchone()[0]
    passed = number == 0
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] Duplicate or NULL {table}.{column}: {number}")

# 3. Range checks: Ensure that values fall within expected ranges
range_queries = (
    (
        "Nonpositive known attendance or more than stadium capacity",
        "SELECT COUNT(*) FROM fact_game WHERE attendance NOT BETWEEN 0 and 81441",
    ),
    (
        "Invalid weather ranges",
        """
        SELECT COUNT(*) FROM fact_weather
        WHERE wind_speed_kmh < 0 OR percip_mm < 0
           OR relative_humidity NOT BETWEEN 0 AND 100
        """,
    ),
    (
        "Invalid game week or scores",
        """
        SELECT COUNT(*) FROM fact_game
        WHERE week <= 0 OR home_score < 0 OR opp_score < 0
        """,
    ),
)
for label, query in range_queries:
    cursor.execute(query)
    number = cursor.fetchone()[0]
    passed = number == 0
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] {label}: {number}")

# 4. Missing value checks: Ensure that the percentage of missing values in critical columns is below the threshold
missing_columns = (
    ("fact_game", "attendance"),
    ("fact_weather", "temp_c"),
    ("fact_weather", "wind_speed_kmh"),
    ("fact_weather", "percip_mm"),
    ("fact_weather", "relative_humidity"),
)
for table, column in missing_columns:
    query = sql.SQL("""
        SELECT COALESCE(
            100.0 * COUNT(*) FILTER (WHERE {} IS NULL) / NULLIF(COUNT(*), 0),
            100
        )
        FROM {}
    """).format(sql.Identifier(column), sql.Identifier(table))
    cursor.execute(query)
    number = cursor.fetchone()[0]
    passed = number < MISSING_LIMIT
    results.append(passed)
    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"Missing {table}.{column} percent (must be < {MISSING_LIMIT}): {number}"
    )

# 5. Foreign key checks: Ensure that all foreign key references are valid and not orphaned
foreign_keys = (
    ("fact_game", "date_id", "dim_date", "date_id"),
    ("fact_game", "home_team_id", "dim_team", "team_id"),
    ("fact_game", "opponent_id", "dim_team", "team_id"),
    ("fact_weather", "game_id", "fact_game", "game_id"),
)
for child, foreign_key, parent, primary_key in foreign_keys:
    query = sql.SQL("""
        SELECT COUNT(*)
        FROM {} AS child
        LEFT JOIN {} AS parent ON child.{} = parent.{}
        WHERE parent.{} IS NULL
    """).format(
        sql.Identifier(child),
        sql.Identifier(parent),
        sql.Identifier(foreign_key),
        sql.Identifier(primary_key),
        sql.Identifier(primary_key),
    )
    cursor.execute(query)
    number = cursor.fetchone()[0]
    passed = number == 0
    results.append(passed)
    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"Orphaned or NULL {child}.{foreign_key}: {number}"
    )

# 6. Checks every game is a Packers home game and the opponent is not also the packers and that no season/week combination has more than one game
cursor.execute("""
    SELECT COUNT(*)
    FROM fact_game
    WHERE home_team_id <> 'GB' OR opponent_id = 'GB'
""")
number = cursor.fetchone()[0]
passed = number == 0
results.append(passed)
print(
    f"[{'PASS' if passed else 'FAIL'}] "
    f"Games that are not Packers home games: {number}"
)

cursor.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT d.season, f.week
        FROM fact_game f JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.season, f.week
        HAVING COUNT(*) > 1
    ) AS duplicate_weeks
""")
number = cursor.fetchone()[0]
passed = number == 0
results.append(passed)
print(
    f"[{'PASS' if passed else 'FAIL'}] "
    f"Duplicate season/week game groups: {number}"
)

cursor.close()
connection.close()

failures = sum(not passed for passed in results)
print(f"[{'PASS' if failures == 0 else 'FAIL'}] Failed checks: {failures} of {len(results)}")
