import pandas as pd
import pytest

from ml.preprocessing.validation import DataValidator


@pytest.fixture
def base_row():
    return {
        "machine_id": "M1001",
        "timestamp": "2026-08-27 12:00:00",
        "machine_type": "Industrial Motor",
        "temperature": 65.0,
        "vibration": 1.5,
        "pressure": 35.0,
        "rpm": 1800.0,
        "voltage": 220.0,
        "current": 15.0,
        "power": 2.8,
        "humidity": 45.0,
        "load": 70.0,
        "operating_hours": 12.0,
        "maintenance_count": 0,
        "last_maintenance": "2026-08-27 00:00:00",
        "failure": 0,
        "failure_type": "None",
        "RUL": 240.0,
    }


def test_validator_clean_data(base_row):
    df = pd.DataFrame([base_row])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    assert len(valid) == 1
    assert len(quarantined) == 0
    assert report["metrics"]["validity_percentage"] == 100.0
    assert report["metrics"]["completeness_percentage"] == 100.0
    assert report["metrics"]["uniqueness_percentage"] == 100.0


def test_validator_missing_values(base_row):
    row1 = base_row.copy()
    row1["temperature"] = None  # Missing value

    df = pd.DataFrame([row1])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    assert len(valid) == 0
    assert len(quarantined) == 1
    assert "missing_values" in quarantined.iloc[0]["quarantine_reason"]


def test_validator_out_of_bounds(base_row):
    row1 = base_row.copy()
    row1["temperature"] = 350.0  # Impossible temperature (bounds are -40 to 200)

    df = pd.DataFrame([row1])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    assert len(valid) == 0
    assert len(quarantined) == 1
    assert "out_of_bounds_temperature" in quarantined.iloc[0]["quarantine_reason"]


def test_validator_invalid_machine_id(base_row):
    row1 = base_row.copy()
    row1["machine_id"] = "XYZ-123"  # Non-standard machine id format

    df = pd.DataFrame([row1])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    assert len(valid) == 0
    assert len(quarantined) == 1
    assert "invalid_machine_id" in quarantined.iloc[0]["quarantine_reason"]


def test_validator_duplicate_timestamps(base_row):
    row1 = base_row.copy()
    row2 = base_row.copy()  # Identical machine and timestamp

    df = pd.DataFrame([row1, row2])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    assert len(valid) == 0
    assert len(quarantined) == 2
    assert "duplicate_timestamp" in quarantined.iloc[0]["quarantine_reason"]


def test_validator_out_of_order_timestamps(base_row):
    row1 = base_row.copy()
    row1["timestamp"] = "2026-08-27 12:00:00"

    row2 = base_row.copy()
    row2["timestamp"] = (
        "2026-08-27 11:00:00"  # Earlier timestamp comes later in the data list
    )

    df = pd.DataFrame([row1, row2])
    validator = DataValidator()
    valid, quarantined, report = validator.validate(df)

    # row2 is out of order chronologically
    assert len(valid) == 1
    assert len(quarantined) == 1
    assert "out_of_order_timestamp" in quarantined.iloc[0]["quarantine_reason"]
