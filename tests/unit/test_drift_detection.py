import numpy as np
import pytest

from ml.monitoring.drift import AlertSystem, DataDriftDetector


@pytest.fixture
def mock_drift_data():
    np.random.seed(42)
    # 10 features, 500 samples baseline
    X_baseline = np.random.normal(loc=0.0, scale=1.0, size=(500, 10))
    feature_names = [f"sensor_{i}" for i in range(10)]

    # Target actual data without drift (identical distribution)
    X_stable = np.random.normal(loc=0.0, scale=1.0, size=(250, 10))

    # Target actual data with moderate drift (shift mean on 2 features)
    X_moderate_drift = np.random.normal(loc=0.0, scale=1.0, size=(250, 10))
    X_moderate_drift[:, 0] += 0.8  # Shift first feature significantly
    X_moderate_drift[:, 1] += 0.9  # Shift second feature significantly

    # Target actual data with severe drift (shift mean on all features)
    X_severe_drift = np.random.normal(loc=2.5, scale=1.2, size=(250, 10))

    return X_baseline, feature_names, X_stable, X_moderate_drift, X_severe_drift


def test_no_drift(mock_drift_data):
    baseline, names, stable, _, _ = mock_drift_data
    detector = DataDriftDetector(baseline, names)

    results = detector.detect_drift(stable)
    assert results["alert_level"] == "OK"
    assert results["drifted_features_ratio"] < 0.20
    assert results["mean_psi"] < 0.10


def test_moderate_drift(mock_drift_data):
    baseline, names, _, moderate, _ = mock_drift_data
    detector = DataDriftDetector(baseline, names)

    results = detector.detect_drift(moderate)
    assert results["alert_level"] == "WARNING"
    assert results["feature_level_drift"]["sensor_0"]["drifted"] is True
    assert results["feature_level_drift"]["sensor_1"]["drifted"] is True
    assert results["feature_level_drift"]["sensor_2"]["drifted"] is False


def test_severe_drift(mock_drift_data):
    baseline, names, _, _, severe = mock_drift_data
    detector = DataDriftDetector(baseline, names)

    results = detector.detect_drift(severe)
    assert results["alert_level"] == "CRITICAL"
    assert results["drifted_features_ratio"] >= 0.8  # Almost all features drifted
    assert results["mean_psi"] >= 0.25


def test_alert_system():
    res = AlertSystem.send_alert(
        subject="Model Performance Degradation",
        message="Model F1 score has dropped below 0.50 on verification batch.",
        alert_level="CRITICAL",
    )
    assert res["status"] == "DISPATCHED"
    assert res["payload"]["severity"] == "CRITICAL"
    assert "F1 score has dropped" in res["payload"]["message"]
