from pathlib import Path
import os

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv


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

# Foreign keys require this load order.
TABLES = (
    "dim_team",
    "dim_date",
    "fact_game",
    "fact_weather",
    "ml_feature",
)

connection = psycopg2.connect(**DB_CONFIG)

cursor = connection.cursor()
cursor.execute(
    sql.SQL("TRUNCATE TABLE {} CASCADE").format(
        sql.SQL(", ").join(sql.Identifier(table) for table in TABLES)
    )
)
cursor.close()

for table_name in TABLES:
    csv_path = CLEAN_DIR / f"{table_name}.csv"
    frame = pd.read_csv(csv_path)
    columns = list(frame.columns)
    values = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in frame.itertuples(index=False, name=None)
    ]
    insert = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    cursor = connection.cursor()
    execute_values(cursor, insert, values)
    cursor.close()
    print(f"Loaded {len(frame)} rows into {table_name}.")

connection.commit()
connection.close()
