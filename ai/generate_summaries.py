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

PROMPT_TEMPLATE = """ You are writing for a stadium operations manager. In 2–3 plain sentences, summarize this attendance prediction.
Translate values into natural language: do not mention feature names, binary flags, or raw 0/1 values.
Connect the game context to the attendance outlook with cautious language such as "supported," "pointed to,"
or "likely helped." Do not claim that a feature caused attendance, and do not invent facts.
If a value is missing or neutral, leave it out. 

Game context:
- Opponent: {opponent}
- Rest since the prior home game: {days_since_last_home_game} days
- Packers' win percentage before the game: {win_pct_before_game}%
- Day of the week: {day_of_week}

Prediction result:
- Predicted attendance: {predicted} fans
- Actual attendance: {actual} fans
- Absolute miss: {error} fans
- Direction: {error_direction}
"""


def format_number(value):
    """Format database numeric values for a manager-facing sentence."""
    if value is None:
        return "not available"
    return f"{float(value):,.0f}"


def format_percent(value):
    if value is None:
        return "not available"
    return f"{float(value) * 100:.0f}"



def format_decimal(value):
    if value is None:
        return "not available"
    return f"{float(value):.1f}"


def format_day(flags):
    """Return the active weekday, treating all-zero weekday flags as Sunday."""
    labels = {
        "Monday": flags[0],
        "Tuesday": flags[1],
        "Wednesday": flags[2],
        "Thursday": flags[3],
        "Friday": flags[4],
        "Saturday": flags[5],
    }
    return next(
        (label for label, active in labels.items() if active),
        "Sunday" if all(not active for active in flags) else "not available",
    )

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
        t.team_name AS opponent,
        m.days_since_last_home_game,
        m.win_pct_before_game,
        m.day_monday,
        m.day_tuesday,
        m.day_wednesday,
        m.day_thursday,
        m.day_friday,
        m.day_saturday
    FROM predictions AS p
    JOIN ml_feature AS m ON m.game_id = p.game_id
    JOIN fact_game AS g ON g.game_id = p.game_id
    JOIN dim_team AS t ON t.team_id = g.opponent_id
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
        opponent,
        days_since_last_home_game,
        win_pct_before_game,
        day_monday,
        day_tuesday,
        day_wednesday,
        day_thursday,
        day_friday,
        day_saturday,
    ) = row
    error_direction = (
        "underpredicted"
        if predicted < actual
        else "overpredicted"
        if predicted > actual
        else "matched actual attendance"
    )
    response = client.responses.create(
        model="gpt-5.6-sol",
        max_output_tokens=200,
        input=PROMPT_TEMPLATE.format(
            opponent=opponent or "not available",
            days_since_last_home_game=(
                days_since_last_home_game
                if days_since_last_home_game is not None
                else "not available"
            ),
            win_pct_before_game=format_percent(win_pct_before_game),
            day_of_week=format_day(
                (
                    day_monday,
                    day_tuesday,
                    day_wednesday,
                    day_thursday,
                    day_friday,
                    day_saturday,
                )
            ),
            predicted=format_number(predicted),
            actual=format_number(actual),
            error=format_number(error),
            error_direction=error_direction,
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
