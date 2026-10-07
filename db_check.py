import os
import warnings
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv(".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "packers_attendance"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),  # no default - it comes from .env
}

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

conn = psycopg2.connect(**DB_CONFIG)
df = pd.read_sql("SELECT * FROM dim_date;", conn)
print(df)
df = pd.read_sql("SELECT * FROM dim_stadium;", conn)
print(df)
df = pd.read_sql("SELECT * FROM dim_team;", conn)
print(df)
df = pd.read_sql("SELECT * FROM fact_game;", conn)
print(df)
conn.close()