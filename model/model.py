import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

FIGURE_DIR = Path("docs/figures")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
my_random_seed = 42

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "packers_attendance"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
}
connection = psycopg2.connect(**DB_CONFIG)
# Use the project's existing database settings in .env.

# Read the saved split assignments from Postgres.
cur = connection.cursor()

cur.execute("SELECT * FROM ml_feature ORDER BY date_id, game_id;")
df = pd.DataFrame(cur.fetchall(), columns=[column[0] for column in cur.description])
connection.close()

train = df[df["split"] == "train"]
validate = df[df["split"] == "validate"]
test = df[df["split"] == "test"]

print(f"Train rows: {len(train)}")
print(f"Validate rows: {len(validate)}")
print(f"Test rows: {len(test)}")

# Chart 1: Distribution of attendance
plt.figure(figsize=(8, 5))
plt.hist(train["attendance"].dropna(), bins=10, color="forestgreen", edgecolor="white")
plt.title("Distribution of Home-Game Attendance (Training Data)")
plt.xlabel("Attendance")
plt.ylabel("Number of Games")
plt.ticklabel_format(style="plain", axis="x", useOffset=False)
plt.tight_layout()
plt.savefig(FIGURE_DIR / "attendance_distribution.png", dpi=300)
plt.close()

# Chart 2: Attendance against prior win percentage
win_pct_data = train.dropna(subset=["attendance", "win_pct_before_game"])

plt.figure(figsize=(8, 5))
plt.scatter(win_pct_data["win_pct_before_game"], win_pct_data["attendance"], color="forestgreen", alpha=0.7)
plt.title("Attendance vs. Prior Win Percentage (Training Data)")
plt.xlabel("Win Percentage Before Game")
plt.ylabel("Attendance")
plt.xlim(-0.05, 1.05)
plt.ticklabel_format(style="plain", axis="y", useOffset=False)
plt.tight_layout()
plt.savefig(FIGURE_DIR / "attendance_vs_win_pct.png", dpi=300)
plt.close()

# Chart 3: Attendance against days since the previous home game
home_gap_data = train.dropna(subset=["attendance", "days_since_last_home_game"])

plt.figure(figsize=(8, 5))
plt.scatter(home_gap_data["days_since_last_home_game"], home_gap_data["attendance"], color="forestgreen", alpha=0.7)
plt.title("Attendance vs. Days Since Last Home Game (Training Data)")
plt.xlabel("Days Since Last Home Game")
plt.ylabel("Attendance")
plt.ticklabel_format(style="plain", axis="y", useOffset=False)
plt.tight_layout()
plt.savefig(FIGURE_DIR / "attendance_vs_home_game_gap.png", dpi=300)
plt.close()

# Calculate the baseline prediction using training attendance only
baseline_prediction = train["attendance"].mean()

# Compare that prediction with actual validation attendance
baseline_results = validate[["game_id", "attendance"]].copy()
baseline_results["baseline_guess"] = baseline_prediction
baseline_results["absolute_error"] = (
    baseline_results["attendance"] - baseline_results["baseline_guess"]
).abs()

baseline_mae = baseline_results["absolute_error"].mean()

print(f"\nBaseline prediction: {baseline_prediction:,.2f} fans")
print(f"Baseline validation MAE: {baseline_mae:,.2f} fans")
print(baseline_results.to_string(index=False))

# Remove IDs, the split label, and the target from the predictors
exclude_columns = ["game_id", "date_id", "split", "attendance"]

x_train = train.drop(columns=exclude_columns).apply(pd.to_numeric, errors="raise")
x_validate = validate.drop(columns=exclude_columns).apply(pd.to_numeric, errors="raise")

y_train = train["attendance"].astype(float)
y_validate = validate["attendance"].astype(float)

# Baseline: predict the training average for every validation game
baseline_prediction = y_train.mean()
baseline_predictions = [baseline_prediction] * len(y_validate)
baseline_mae = mean_absolute_error(y_validate, baseline_predictions)

results = [{"Model": "Baseline: training mean", "Validation MAE": baseline_mae}]

# Linear Regression model
linear_regression = LinearRegression()
linear_regression.fit(x_train, y_train)
y_pred_validate = linear_regression.predict(x_validate)
validation_mae = mean_absolute_error(y_validate, y_pred_validate)
results.append({"Model": "Linear Regression", "Validation MAE": validation_mae})


# Train a random forest; limit tree size because the dataset is small
# Remove the additional features for the random forest
remove_columns = [
    "kickoff_afternoon", "kickoff_early_evening", "kickoff_prime_time",
    "kickoff_late", "relative_humidity", "is_postseason", "day_monday", "day_tuesday", 
    "day_wednesday", "day_thursday", "day_friday", "day_saturday"
]

x_train_forest = x_train.drop(columns=remove_columns)
x_validate_forest = x_validate.drop(columns=remove_columns)

random_forest = RandomForestRegressor(
    n_estimators=300,
    max_depth=3,
    min_samples_leaf=3,
    random_state=my_random_seed
)

random_forest.fit(x_train_forest, y_train)
y_pred_validate = random_forest.predict(x_validate_forest)
validation_mae = mean_absolute_error(y_validate, y_pred_validate)
results.append({"Model": "Random Forest Regression", "Validation MAE": validation_mae})

# Scale features
standard_scaler = StandardScaler()
standard_scaler.fit(x_train)
x_train_scaled = standard_scaler.transform(x_train)
x_validate_scaled = standard_scaler.transform(x_validate)


# Create a KNN model
knn = KNeighborsRegressor(
    n_neighbors=5,
    p=2,
    metric="minkowski",
    weights="uniform",
    algorithm="auto"
)
# Fit KNN model on training data
knn.fit(x_train_scaled, y_train)

# Predict on validation data using the KNN model
predictions = knn.predict(x_validate_scaled)
validation_mae = mean_absolute_error(y_validate, predictions)
results.append({"Model": "KNN regression", "Validation MAE": validation_mae})


# Display one comparison table, keeping the baseline first
comparison = pd.DataFrame(results)
print("\nValidation results")
print(comparison.to_string(index=False, float_format=lambda value: f"{value:,.2f}"))


# Prepare test features using the same columns and order as training
x_test = test.drop(columns=exclude_columns).apply(pd.to_numeric, errors="raise")
y_test = test["attendance"].astype(float)

# Score the selected model on test data once
y_pred_test = random_forest.predict(x_test)
test_mae = mean_absolute_error(y_test, y_pred_test)
forest_mae = comparison.loc[comparison["Model"] == "Random Forest Regression", "Validation MAE"].values[0]
# Compare validation and test MAE
final_scores = pd.DataFrame({
    "Dataset": ["Validate", "Test"],
    "Random Forest MAE": [forest_mae, test_mae]
})

print("\nFinal random forest results")
print(final_scores.to_string(index=False, float_format=lambda value: f"{value:,.2f}"))


# Rank the features used to train the random forest
feature_importance = pd.DataFrame({
    "Feature": x_train.columns,
    "Importance": random_forest.feature_importances_
})

top_features = feature_importance.sort_values("Importance", ascending=False).head(4)

print("\nTop four random forest features")
print(top_features.to_string(index=False, float_format=lambda value: f"{value:.4f}"))