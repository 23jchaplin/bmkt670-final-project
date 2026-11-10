from dotenv import load_dotenv
load_dotenv()  # reads the .env file and loads the keys
import os
import psycopg2
from openai import OpenAI

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "packers_attendance"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
}

client = OpenAI()  # reads OPENAI_API_KEY automatically

PROMPT_TEMPLATE = """You are writing for a stadium operations manager. In 2–3 plain sentences, 
summarize this attendance prediction. Use only the facts below and do not add information. Comment on if
the prediction makes sense given the key features.

Key features:
- Days since last home game: {days_since_last_home_game}
- Win percentage before game: {win_pct_before_game}
- Temperature (C): {temp_c}
- Precipitation (mm): {percip_mm}
- Kickoff afternoon: {kickoff_afternoon}
- Kickoff early morning: {kickoff_early_morning}
- Kickoff prime time: {kickoff_prime_time}
- Kickoff late: {kickoff_late}

Predicted attendance: {predicted}
Actual attendance: {actual}
Absolute error: {error}
"""

connection = psycopg2.connect(**DB_CONFIG)
cursor = connection.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS ai_summaries (
        game_id TEXT PRIMARY KEY,
        summary TEXT NOT NULL,
        written_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
)
cursor.execute(
    """
    SELECT
        p.game_id,
        p.actual,
        p.predicted,
        ABS(p.actual - p.predicted) AS error,
        m.days_since_last_home_game,
        m.win_pct_before_game,
        m.temp_c,
        m.percip_mm,
        m.kickoff_afternoon,
        m.kickoff_early_evening,
        m.kickoff_prime_time,
        m.kickoff_late
    FROM predictions AS p
    JOIN ml_feature AS m ON m.game_id = p.game_id
    WHERE p.split = 'test'
    ORDER BY p.game_id
    """
)
rows = cursor.fetchall()

for row in rows:
    (
        game_id,
        actual,
        predicted,
        error,
        days_since_last_home_game,
        win_pct_before_game,
        temp_c,
        percip_mm,
        kickoff_afternoon,
        kickoff_early_evening,
        kickoff_prime_time,
        kickoff_late,
    ) = row
    response = client.responses.create(
        model="gpt-5.6-sol",
        max_output_tokens=200,
        input=PROMPT_TEMPLATE.format(
            days_since_last_home_game=days_since_last_home_game,
            win_pct_before_game=win_pct_before_game,
            temp_c=temp_c,
            percip_mm=percip_mm,
            kickoff_afternoon=kickoff_afternoon,
            kickoff_early_morning=kickoff_early_evening,
            kickoff_prime_time=kickoff_prime_time,
            kickoff_late=kickoff_late,
            predicted=predicted,
            actual=actual,
            error=error,
        ),
    )
    cursor.execute(
        """
        INSERT INTO ai_summaries (game_id, summary)
        VALUES (%s, %s)
        ON CONFLICT (game_id) DO UPDATE
        SET summary = EXCLUDED.summary, written_at = CURRENT_TIMESTAMP
        """,
        (game_id, response.output_text.strip()),
    )

connection.commit()
cursor.close()
connection.close()
print(f"Saved {len(rows)} attendance summaries.")
