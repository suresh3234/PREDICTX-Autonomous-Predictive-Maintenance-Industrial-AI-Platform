import numpy as np
import pandas as pd
import pytest

from ml.monitoring.drift import DataDriftDetector
from ml.registry.manager import ModelRegistryManager
from ml.retraining.pipeline import RetrainingPipeline


@pytest.fixture
def retraining_setup(tmp_path):
    store_dir = tmp_path / "model_store"
    registry_manager = ModelRegistryManager(base_dir=str(store_dir))

    # Create baseline features for drift detector
    # 5 features, 100 samples
    np.random.seed(42)
    X_baseline = np.random.normal(loc=0.0, scale=1.0, size=(100, 93))
    feature_names = [f"feature_{i}" for i in range(93)]

    drift_detector = DataDriftDetector(X_baseline, feature_names)
    pipeline = RetrainingPipeline(registry_manager, drift_detector)

    # Create fake raw telemetry CSV
    # We populate columns matching raw schema
    data_len = 100
    rul = np.tile(np.linspace(10.0, 0.0, 20), 5)

    # Correlate temperature and vibration with low RUL (RUL <= 4.0) to make the model perform well
    temperature = np.where(rul <= 4.0, np.random.normal(loc=65.0, scale=1.0, size=data_len), np.random.normal(loc=50.0, scale=1.0, size=data_len))
    vibration = np.where(rul <= 4.0, np.random.normal(loc=25.0, scale=0.2, size=data_len), np.random.normal(loc=20.0, scale=0.2, size=data_len))

    df_raw = pd.DataFrame(
        {
            "machine_id": ["M1000"] * data_len,
            "timestamp": pd.date_range(
                start="2026-08-01", periods=data_len, freq="10min"
            ),
            "machine_type": ["Medium Duty"] * data_len,
            "temperature": temperature,
            "vibration": vibration,
            "pressure": np.random.normal(loc=100.0, scale=5.0, size=data_len),
            "rpm": np.random.normal(loc=1500.0, scale=20.0, size=data_len),
            "voltage": np.random.normal(loc=220.0, scale=1.5, size=data_len),
            "current": np.random.normal(loc=10.0, scale=0.5, size=data_len),
            "power": np.random.normal(loc=2.0, scale=0.1, size=data_len),
            "humidity": np.random.normal(loc=50.0, scale=3.0, size=data_len),
            "load": np.random.normal(loc=70.0, scale=5.0, size=data_len),
            "operating_hours": np.linspace(0.0, 10.0, data_len),
            "maintenance_count": [0] * data_len,
            "last_maintenance": ["2026-08-01"] * data_len,
            "failure": np.tile([0] * 19 + [1], 5),
            "failure_type": ["None"] * data_len,
            "RUL": rul,
        }
    )

    # Write a stable telemetry CSV
    stable_csv_path = tmp_path / "sensor_readings_stable.csv"
    df_raw.to_csv(stable_csv_path, index=False)

    # Write a drifted telemetry CSV (heavily shifted temperature sensor readings)
    df_drifted = df_raw.copy()
    df_drifted["temperature"] += 15.0  # Massive shift triggers critical drift
    drifted_csv_path = tmp_path / "sensor_readings_drifted.csv"
    df_drifted.to_csv(drifted_csv_path, index=False)

    return pipeline, str(stable_csv_path), str(drifted_csv_path)


def test_retraining_no_drift(retraining_setup):
    pipeline, stable_csv, _ = retraining_setup

    # Fit drift detector baseline on stable features first
    df_stable = pipeline.feature_pipeline.transform(
        pd.read_csv(stable_csv), drop_na=True
    )
    feature_cols = [
        col
        for col in df_stable.columns
        if col.startswith("feature_") and col != "feature_failure_type"
    ]
    pipeline.drift_detector.fit_baseline(df_stable[feature_cols].values, feature_cols)

    # Stable data should NOT trigger retraining
    res = pipeline.check_drift_and_retrain(
        task="failure_classification", raw_data_path=stable_csv, force=False
    )
    assert res["retrained"] is False
    assert res["promoted"] is False
    assert res["version"] is None


def test_retraining_forced(retraining_setup):
    pipeline, stable_csv, _ = retraining_setup

    # Retraining forced should execute and promote
    res = pipeline.check_drift_and_retrain(
        task="failure_classification", raw_data_path=stable_csv, force=True
    )
    assert res["retrained"] is True
    assert res["promoted"] is True
    assert res["version"] == "1.0.0"

    # Active production status in registry
    prod_model = pipeline.registry_manager.load_production_model(
        "failure_classification"
    )
    assert prod_model["metadata"]["version"] == "1.0.0"


def test_retraining_drift_triggered(retraining_setup):
    pipeline, stable_csv, drifted_csv = retraining_setup

    # Promote first baseline version
    pipeline.check_drift_and_retrain(
        task="failure_classification", raw_data_path=stable_csv, force=True
    )

    # Fit drift detector baseline on stable features
    df_stable = pipeline.feature_pipeline.transform(
        pd.read_csv(stable_csv), drop_na=True
    )
    feature_cols = [
        col
        for col in df_stable.columns
        if col.startswith("feature_") and col != "feature_failure_type"
    ]
    pipeline.drift_detector.fit_baseline(df_stable[feature_cols].values, feature_cols)

    # Processing drifted CSV should trigger CRITICAL drift alert and retrain
    res = pipeline.check_drift_and_retrain(
        task="failure_classification", raw_data_path=drifted_csv, force=False
    )
    assert res["drift_alert"] == "CRITICAL"
    assert res["retrained"] is True
    assert res["version"] == "1.0.1"
