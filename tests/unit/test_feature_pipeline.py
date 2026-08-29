import pandas as pd
import pytest

from ml.features.pipelines import FeaturePipeline


@pytest.fixture
def sample_sequence():
    # Construct a temporal sequence of sensor readings for a single machine
    records = []
    base_time = pd.Timestamp("2026-08-27 12:00:00")
    for i in range(30):  # 30 steps
        records.append(
            {
                "machine_id": "M1001",
                "timestamp": (base_time + pd.Timedelta(minutes=10 * i)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "machine_type": "Industrial Motor",
                "temperature": 60.0 + i * 0.5,  # Increasing temperature
                "vibration": 1.5 + (i % 3) * 0.2,  # oscillating vibration
                "pressure": 35.0,
                "rpm": 1800.0,
                "voltage": 220.0,
                "current": 15.0,
                "power": 2.8,
                "humidity": 45.0,
                "load": 70.0,
                "operating_hours": 12.0 + i * (10 / 60.0),
                "maintenance_count": 0,
                "last_maintenance": "2026-08-27 11:00:00",
                "failure": 0,
                "failure_type": "None",
                "RUL": 240.0 - i * (10 / 60.0),
            }
        )
    return pd.DataFrame(records)


def test_feature_pipeline_generation(sample_sequence):
    pipeline = FeaturePipeline(rolling_windows=[3, 6])
    df_features = pipeline.transform(sample_sequence, drop_na=True)

    # We should have fewer rows than the original 30 because lag=20 drops the first 20 rows
    assert len(df_features) == 10

    # Verify new features exist
    new_cols = [col for col in df_features.columns if col.startswith("feature_")]
    assert len(new_cols) > 0
    assert "feature_temp_x_vib" in new_cols
    assert "feature_temperature_lag_1" in new_cols
    assert "feature_temperature_lag_20" in new_cols
    assert "feature_vibration_rms_6" in new_cols
    assert "feature_vibration_crest_factor_3" in new_cols
    assert "feature_days_since_maintenance" in new_cols
    assert "feature_operating_cycle" in new_cols

    # Verify calculation logic for interactions
    first_row = df_features.iloc[0]
    expected_interaction = first_row["temperature"] * first_row["vibration"]
    assert (
        pytest.approx(first_row["feature_temp_x_vib"], rel=1e-5) == expected_interaction
    )

    # Verify lag logic: lag_1 should match the previous row's raw value in the original sequence
    # Let's find the original row corresponding to df_features.iloc[0] (which is index 20 in sample_sequence)
    original_idx = 20
    assert (
        df_features.iloc[0]["feature_temperature_lag_1"]
        == sample_sequence.iloc[original_idx - 1]["temperature"]
    )
    assert (
        df_features.iloc[0]["feature_temperature_lag_5"]
        == sample_sequence.iloc[original_idx - 5]["temperature"]
    )

    # Verify rate-of-change delta
    expected_delta = (
        df_features.iloc[0]["temperature"]
        - df_features.iloc[0]["feature_temperature_lag_1"]
    )
    assert (
        pytest.approx(df_features.iloc[0]["feature_temperature_delta"], rel=1e-5)
        == expected_delta
    )

    # Verify no target leakage (RUL and failure tags are left unmodified)
    assert "RUL" in df_features.columns
    assert "failure" in df_features.columns
    assert "failure_type" in df_features.columns
    # Ensure targets were not renamed or prefixed
    assert not any(
        col.startswith("feature_") for col in ["RUL", "failure", "failure_type"]
    )
