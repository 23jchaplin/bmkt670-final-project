import altair as alt
import pandas as pd
import psycopg2
import streamlit as st

st.set_page_config(page_title="Packers Attendance", layout="wide")

st.sidebar.title("🏈 Packers Attendance")
st.sidebar.write("For: game-day operations manager")

page = st.sidebar.radio(
    "Page",
    [
        "1. What happened",
        "2. How good are the predictions",
        "3. What should we do",
    ]
)

postgresql_secrets = st.secrets["connections"]["postgresql"]

db_config = {
    "host": postgresql_secrets["host"],
    "port": postgresql_secrets["port"],
    "dbname": postgresql_secrets["database"],
    "user": postgresql_secrets["username"],
    "password": postgresql_secrets["password"],
}


def read_query(query, params=None):
    connection = psycopg2.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=columns)
    finally:
        connection.close()


if page == "1. What happened":
    st.title("What Happened")
    st.write("Explore historical attendance at Lambeau Field.")

    query = """
        SELECT
            m.game_id,
            d.date_id AS game_date,
            m.season,
            m.attendance
        FROM ml_feature AS m
        JOIN fact_game AS f ON m.game_id = f.game_id
        JOIN dim_date AS d ON m.date_id = d.date_id
        ORDER BY d.date_id
    """

    data = read_query(query)

    if data.empty:
        st.info("No home game data is available.")
        st.stop()

    data["game_date"] = pd.to_datetime(data["game_date"])
    data["day_of_week"] = data["game_date"].dt.day_name()

    # Continue your existing season filter, metrics, and charts here.
    # Season filter
    seasons = sorted(data["season"].unique().tolist())
    selected_seasons = st.multiselect(
        "Select seasons",
        options=seasons,
        default=seasons,
        help="Choose one or more seasons to compare.",
    )

    if not selected_seasons:
        st.info("Select at least one season to view attendance.")
        st.stop()

    data = data[data["season"].isin(selected_seasons)]

    # Summary metrics
    home_games = data["game_id"].nunique()
    average_attendance = data["attendance"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Home Games", f"{home_games:,}")
    col2.metric(
        "Average Attendance",
        f"{average_attendance:,.0f}" if pd.notna(average_attendance) else "N/A"
    )
    col3.metric("Stadium Capacity", "81,441")

    # Exclude missing attendance from charts only
    chart_data = data.dropna(subset=["attendance"])

    if chart_data.empty:
        st.info("No attendance values are available for the selected seasons.")
        st.stop()

    # Chart 1
    chart_data = chart_data.copy()
    chart_data["game_number"] = chart_data.groupby("season").cumcount()
    game_counts = chart_data.groupby("season")["game_number"].transform("max").clip(lower=1)
    chart_data["season_jitter"] = (
        chart_data["game_number"] / game_counts - 0.5
    ) * 0.6
    chart_data["day_game_number"] = chart_data.groupby("day_of_week").cumcount()
    day_game_counts = (
        chart_data.groupby("day_of_week")["day_game_number"]
        .transform("max")
        .clip(lower=1)
    )
    chart_data["day_jitter"] = (
        chart_data["day_game_number"] / day_game_counts - 0.5
    ) * 0.6

    average_by_season = (
        chart_data.groupby("season", as_index=False)["attendance"]
        .mean()
        .rename(columns={"attendance": "season_average"})
    )

    average_by_day = (
        chart_data.groupby("day_of_week", as_index=False)["attendance"]
        .mean()
        .rename(columns={"attendance": "day_average"})
    )

    y_max = max(81441, chart_data["attendance"].max())
    y_domain = [75000, y_max]
    day_colors = alt.Scale(scheme="tableau10")
    dark_chart = {
        "background": "#1f2937",
        "axis": alt.Axis(labelColor="white", titleColor="white", gridColor="#4b5563"),
        "legend": alt.Legend(labelColor="white", titleColor="white"),
        "title": alt.TitleConfig(color="white"),
        "view": {"stroke": "transparent"},
    }

    points = alt.Chart(chart_data).mark_circle(
        opacity=0.8,
        size=65,
    ).encode(
        x=alt.X("season:N", title="Season", sort=seasons),
        xOffset=alt.XOffset("season_jitter:Q", title=None),
        y=alt.Y("attendance:Q", title="Attendance", scale=alt.Scale(domain=y_domain)),
        color=alt.value("#d95f6a"),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("game_date:T", title="Game date"),
            alt.Tooltip("attendance:Q", title="Attendance", format=","),
        ],
    )

    season_average_line = alt.Chart(average_by_season).mark_line(
        color="white",
        size=3,
    ).encode(
        x=alt.X("season:N", sort=seasons),
        y=alt.Y("season_average:Q", scale=alt.Scale(domain=y_domain)),
    )

    season_average_points = alt.Chart(average_by_season).mark_circle(
        color="white",
        size=90,
    ).encode(
        x=alt.X("season:N", sort=seasons),
        y=alt.Y("season_average:Q", scale=alt.Scale(domain=y_domain)),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("season_average:Q", title="Season average", format=",.0f"),
        ],
    )


    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    average_by_day["day_of_week"] = pd.Categorical(
        average_by_day["day_of_week"], categories=day_order, ordered=True
    )
    average_by_day = average_by_day.sort_values("day_of_week")

    day_points = alt.Chart(chart_data).mark_circle(
        opacity=0.8,
        size=65,
    ).encode(
        x=alt.X("day_of_week:N", title="Day of week", sort=day_order),
        xOffset=alt.XOffset("day_jitter:Q", title=None),
        y=alt.Y("attendance:Q", title="Attendance", scale=alt.Scale(domain=y_domain)),
        color=alt.Color("day_of_week:N", title="Day of week", scale=day_colors),
        tooltip=[
            alt.Tooltip("season:N", title="Season"),
            alt.Tooltip("game_date:T", title="Game date"),
            alt.Tooltip("day_of_week:N", title="Day"),
            alt.Tooltip("attendance:Q", title="Attendance", format=","),
        ],
    )

    day_average_line = alt.Chart(average_by_day).mark_tick(
        color="white",
        thickness=3,
        size=40,
    ).encode(
        x=alt.X("day_of_week:N", sort=day_order),
        y=alt.Y("day_average:Q", scale=alt.Scale(domain=y_domain)),
    )

    day_average_points = alt.Chart(average_by_day).mark_circle(
        color="white",
        size=90,
    ).encode(
        x=alt.X("day_of_week:N", sort=day_order),
        y=alt.Y("day_average:Q", scale=alt.Scale(domain=y_domain)),
        tooltip=[
            alt.Tooltip("day_of_week:N", title="Day"),
            alt.Tooltip("day_average:Q", title="Average attendance", format=",.0f"),
        ],
    )

    season_chart = (
        (points + season_average_line + season_average_points)
        .properties()
        .configure(**dark_chart)
    )
    day_chart = (
        (day_points + day_average_line + day_average_points)
        .properties()
        .configure(**dark_chart)
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Attendance by season")
        st.altair_chart(
            season_chart,
            width="stretch",
            alt="Attendance for each home game with the average attendance for each season",
        )
        st.caption(
            "Each dot is one home game. The white line and dots "
            "show each season's average attendance which only slightly flucuates from year to year"
        )
    average_saturday = average_by_day.loc[average_by_day["day_of_week"] == "Saturday", "day_average"].values[0]
    with chart_col2:
        st.subheader("Attendance by day of the week")
        st.altair_chart(
            day_chart,
            width="stretch",
            alt="Attendance for each home game by day of the week with average attendance",
        )
        st.caption(
            f"Each dot is one home game, colored by day of the week. The white "
            f"is the average. In the selected seasons Saturday games draw the most "
            f"attendance, with an average of {average_saturday} people."
        )

elif page == "2. How good are the predictions":
    st.title("How Good Are the Predictions?")
    st.write(
        "Evaluation of model predictions against actual attendance on 2024 "
        "validation and 2025 test games."
    )
    data = read_query("""
    SELECT
        p.game_id,
        m.date_id AS game_date,
        p.split,
        p.actual,
        p.predicted,
        p.error,
        p.model_name
    FROM predictions AS p
    JOIN ml_feature AS m ON p.game_id = m.game_id
    WHERE p.split IN ('validate', 'test')
    ORDER BY m.date_id
    """)

    baseline_data = read_query("""
        SELECT AVG(attendance) AS baseline_prediction
        FROM ml_feature
        WHERE split = 'train'
        AND attendance IS NOT NULL
    """)

    baseline_prediction = baseline_data["baseline_prediction"].iloc[0]

    if pd.isna(baseline_prediction):
        st.warning("Training attendance is needed to calculate the baseline.")
        st.stop()

    baseline_prediction = float(baseline_prediction)

    data["absolute_error"] = data["error"].abs()
    data["baseline_error"] = (data["actual"] - baseline_prediction).abs()
    validate_data = data[data["split"] == "validate"].copy()
    test_data = data[data["split"] == "test"].copy()

    baseline_validate_mae = validate_data["baseline_error"].mean()
    model_validate_mae = validate_data["absolute_error"].mean()
    model_test_mae = test_data["absolute_error"].mean()
    validate_improvement = baseline_validate_mae - model_validate_mae

    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline MAE (2024)", f"{baseline_validate_mae:,.0f} fans")
    col2.metric(
        "Model MAE (2024, validate)",
        f"{model_validate_mae:,.0f} fans",
        delta=f"{validate_improvement:+,.0f} vs. baseline",
        delta_color="normal",
    )
    col3.metric("Model MAE (2025, test)", f"{model_test_mae:,.0f} fans")

    if model_validate_mae < baseline_validate_mae:
        st.success(
            f"Yes. The validation model MAE was {validate_improvement:,.0f} "
            "fans lower than the baseline."
        )
    elif model_validate_mae > baseline_validate_mae:
        st.warning(
            f"No. The validation model MAE was "
            f"{abs(validate_improvement):,.0f} fans higher than the baseline."
        )
    else:
        st.info("The validation model and baseline had the same MAE.")

    chart_min = 70000
    chart_max = max(
        chart_min,
        float(data[["actual", "predicted"]].max().max()),
    )
    chart_domain = [chart_min, chart_max]
    reference_line = pd.DataFrame(
        {"predicted": chart_domain, "actual": chart_domain}
    )

    st.subheader("Predicted vs. Actual Attendance")
    points = alt.Chart(data).mark_circle(size=75, opacity=0.85).encode(
        x=alt.X(
            "predicted:Q",
            title="Predicted attendance",
            scale=alt.Scale(domain=chart_domain),
        ),
        y=alt.Y(
            "actual:Q",
            title="Actual attendance",
            scale=alt.Scale(domain=chart_domain),
        ),
        color=alt.Color("split:N", title="Split"),
        tooltip=[
            alt.Tooltip("game_id:N", title="Game ID"),
            alt.Tooltip("split:N", title="Split"),
            alt.Tooltip("actual:Q", title="Actual", format=","),
            alt.Tooltip("predicted:Q", title="Predicted", format=","),
            alt.Tooltip("absolute_error:Q", title="Absolute error", format=","),
        ],
    )
    perfect_predictions = alt.Chart(reference_line).mark_line(
        color="#777777",
        strokeDash=[4, 4],
        size=2,
    ).encode(
        x=alt.X("predicted:Q", scale=alt.Scale(domain=chart_domain)),
        y=alt.Y("actual:Q", scale=alt.Scale(domain=chart_domain)),
    )
    st.altair_chart(
        perfect_predictions + points,
        width="stretch",
        alt="Predicted versus actual attendance with a dotted perfect-prediction line",
    )
    st.caption(
        "Dots on the dotted line are perfect predictions. Points farther from "
        "the line represent larger errors."
    )

    data["times_mae"] = data["absolute_error"] / model_validate_mae
    data["flag"] = data["times_mae"].apply(
        lambda value: "Unusual" if value > 2 else "Larger than usual"
    )
    biggest_misses = data[data["times_mae"] >= 1.5].sort_values(
        "absolute_error", ascending=False
    )

    st.subheader("Biggest misses")
    st.caption(
        "Showing only misses at least 1.5 times the validation model's typical "
        f"miss of {model_validate_mae:,.0f} fans. Over 2 times MAE is unusual."
    )
    table = biggest_misses[
        [
            "game_id", "split", "actual", "predicted", "error",
            "times_mae", "flag"
        ]
    ].rename(columns={
        "game_id": "Game ID",
        "split": "Split",
        "actual": "Actual",
        "predicted": "Predicted",
        "error": "Error",
        "times_mae": "x Typical miss",
        "flag": "Flag",
    })
    st.dataframe(
        table.style.format({
            "Actual": "{:,.0f}",
            "Predicted": "{:,.0f}",
            "Error": "{:,.0f}",
            "x Typical miss": "{:.1f}x",
        }),
        hide_index=True,
        width="stretch",
    )

    if not biggest_misses.empty:
        worst = biggest_misses.iloc[0]
        game_date = pd.to_datetime(worst["game_date"]).strftime("%B %d, %Y")
        direction = "below" if worst["error"] < 0 else "above"
        st.write(
            f"Most unusual miss: {game_date}. Attendance was "
            f"{worst['absolute_error']:,.0f} fans {direction} the prediction, "
            f"{worst['times_mae']:.1f} times the typical miss. "
            "Weather, ticket demand, or a special event could have affected "
            "attendance in ways the model did not capture."
        )
    else:
        st.info("No validation or test misses were larger than usual.")
elif page == "3. What should we do":
    # Put your recommendations and prediction tool here.
    st.title("What Should We Do?")