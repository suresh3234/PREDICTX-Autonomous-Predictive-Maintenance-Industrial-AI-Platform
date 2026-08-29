import pickle

import pytest

from ml.registry.manager import ModelRegistryManager


@pytest.fixture
def registry_setup(tmp_path):
    # Initialize registry manager in a test-isolated temporary directory
    store_dir = tmp_path / "model_store"
    manager = ModelRegistryManager(base_dir=str(store_dir))

    # Create fake model pickle files to simulate registration artifacts
    dummy_model = {"model_param": 42}
    dummy_scaler = {"scale_param": 10.0}

    model_path = tmp_path / "model.pkl"
    scaler_path = tmp_path / "scaler.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(dummy_model, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(dummy_scaler, f)

    artifacts = {"model": str(model_path), "scaler": str(scaler_path)}

    return manager, artifacts


def test_registration_and_versioning(registry_setup):
    manager, artifacts = registry_setup

    v1 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.40},
        hyperparameters={"nu": 0.1},
        dataset_lineage="data/synthetic/sensor_readings.csv",
    )
    assert v1 == "1.0.0"

    # Next candidate should auto-increment patch version
    v2 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.45},
        hyperparameters={"nu": 0.2},
        dataset_lineage="data/synthetic/sensor_readings.csv",
    )
    assert v2 == "1.0.1"


def test_promotion_gates_baseline(registry_setup):
    manager, artifacts = registry_setup

    # Register candidate that FAILS the baseline gate (F1 < 0.30 for anomaly_detection)
    v1 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.25},
        hyperparameters={},
        dataset_lineage="lineage_path",
    )

    # Promotion should be rejected
    success = manager.promote_model("anomaly_detection", v1)
    assert not success
    assert manager.records["anomaly_detection"][v1]["status"] == "CANDIDATE"


def test_promotion_gates_comparison(registry_setup):
    manager, artifacts = registry_setup

    # 1. Register and promote first candidate (passes gate)
    v1 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.35},
        hyperparameters={},
        dataset_lineage="lineage_path",
    )
    assert manager.promote_model("anomaly_detection", v1)
    assert manager.records["anomaly_detection"][v1]["status"] == "PRODUCTION"

    # 2. Register second candidate that is WORSE than current production
    v2 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.33},
        hyperparameters={},
        dataset_lineage="lineage_path",
    )
    # Promotion should be rejected
    assert not manager.promote_model("anomaly_detection", v2)
    assert manager.records["anomaly_detection"][v1]["status"] == "PRODUCTION"
    assert manager.records["anomaly_detection"][v2]["status"] == "CANDIDATE"

    # 3. Register third candidate that is BETTER than current production
    v3 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.42},
        hyperparameters={},
        dataset_lineage="lineage_path",
    )
    # Promotion should succeed, archiving v1
    assert manager.promote_model("anomaly_detection", v3)
    assert manager.records["anomaly_detection"][v3]["status"] == "PRODUCTION"
    assert manager.records["anomaly_detection"][v1]["status"] == "ARCHIVED"


def test_load_production_model(registry_setup):
    manager, artifacts = registry_setup

    v1 = manager.register_model(
        task="anomaly_detection",
        artifacts=artifacts,
        metrics={"F1-Score": 0.55},
        hyperparameters={"param": "test"},
        dataset_lineage="lineage_path",
    )
    manager.promote_model("anomaly_detection", v1)

    loaded = manager.load_production_model("anomaly_detection")
    assert loaded["metadata"]["version"] == "1.0.0"
    assert loaded["artifacts"]["model"] == {"model_param": 42}
    assert loaded["artifacts"]["scaler"] == {"scale_param": 10.0}
