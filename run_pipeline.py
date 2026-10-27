import subprocess
import sys
from pathlib import Path

# Scripts to run, in order
steps = [
    "etl/check_pfr_files.py",   # extract: check the hand-downloaded PFR files
    "etl/extract_games.py",     # extract: games
    "etl/extract_weather.py",   # extract: weather 
    "etl/transform.py",         # clean, match keys, reshape, build features
    "etl/load.py",              # empty tables, then load into Postgres
    "etl/quality_checks.py",    # print PASS/FAIL for each check
    "model/model.py",            # train the model and save predictions
]

for step in steps:
    print(f"\n=== Running {step} ===")
    result = subprocess.run([sys.executable, step], cwd=Path(__file__).resolve().parent)

    if result.returncode != 0:
        print(f"\nStopped: {step} failed. Fix it and run again.")
        sys.exit(1)

print("\nPipeline finished.")