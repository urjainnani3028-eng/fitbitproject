"""Data-quality checks for dailyActivity_merged.csv.

If someone replaces or edits the dataset, these tests make sure it still has
the shape the app expects before the change can be merged.
"""

from pathlib import Path

import pandas as pd
import pytest

DATA_PATH = Path(__file__).resolve().parent.parent / "dailyActivity_merged.csv"

FEATURES = [
    "TotalSteps",
    "TotalDistance",
    "TrackerDistance",
    "Calories",
    "VeryActiveDistance",
    "ModeratelyActiveDistance",
    "LightActiveDistance",
    "SedentaryActiveDistance",
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes",
    "SedentaryMinutes",
]


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)


def test_dataset_exists():
    assert DATA_PATH.exists(), "dailyActivity_merged.csv is missing"


def test_has_required_columns(df):
    missing = set(FEATURES) - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_has_enough_rows_for_clustering(df):
    # KMeans with 3 clusters needs well over 3 rows to be meaningful
    assert len(df) >= 30


def test_features_are_numeric(df):
    for col in FEATURES:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"


def test_no_negative_values(df):
    negatives = (df[FEATURES] < 0).sum()
    assert negatives.sum() == 0, f"Negative values found:\n{negatives[negatives > 0]}"


def test_minutes_fit_in_a_day(df):
    minute_cols = ["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]
    total = df[minute_cols].sum(axis=1)
    assert (total <= 1440).all(), "Some rows have more than 1440 minutes in a day"
