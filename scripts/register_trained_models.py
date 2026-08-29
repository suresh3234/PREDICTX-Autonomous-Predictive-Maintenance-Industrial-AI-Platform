import os
import sys
from pathlib import Path

# Programmatically add root directory to sys.path
ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from ml.registry.manager import ModelRegistryManager

def register_models():
    registry_dir = "ml/registry/store"
    manager = ModelRegistryManager(base_dir=registry_dir)

    models_to_register = [
        {
            "task": "anomaly_detection",
            "artifacts": {
                "model": "ml/anomaly/best_anomaly_detector.pkl",
                "scaler": "ml/anomaly/anomaly_scaler.pkl",
            },
            "metrics": {"F1-Score": 0.95},
            "hyperparameters": {"nu": 0.05},
            "dataset_lineage": "data/synthetic/sensor_readings.csv",
        },
        {
            "task": "failure_classification",
            "artifacts": {
                "model": "ml/classification/best_failure_threat_model.pkl",
                "scaler": "ml/classification/classification_scaler.pkl",
            },
            "metrics": {"F1-Score (0.5)": 0.88},
            "hyperparameters": {"n_estimators": 100, "optimal_threshold": 0.35},
            "dataset_lineage": "data/synthetic/sensor_readings.csv",
        },
        {
            "task": "rul_prediction",
            "artifacts": {
                "model": "ml/rul/best_rul_model.pkl",
                "scaler": "ml/rul/rul_scaler.pkl",
            },
            "metrics": {"MAE (hrs)": 2.1},
            "hyperparameters": {"n_estimators": 100},
            "dataset_lineage": "data/synthetic/sensor_readings.csv",
        },
        {
            "task": "sensor_forecasting",
            "artifacts": {
                "model": "ml/forecasting/best_forecaster_model.pkl",
                "scaler": "ml/forecasting/forecaster_scaler.pkl",
            },
            "metrics": {"Average MAE": 1.1},
            "hyperparameters": {"seq_length": 24},
            "dataset_lineage": "data/synthetic/sensor_readings.csv",
        },
    ]

    for model_info in models_to_register:
        task = model_info["task"]
        artifacts = model_info["artifacts"]

        # Check if files exist
        missing = [k for k, path in artifacts.items() if not os.path.exists(path)]
        if missing:
            print(f"Skipping {task}: missing artifact files: {missing}")
            continue

        print(f"\nRegistering {task} model...")
        version = manager.register_model(
            task=task,
            artifacts=artifacts,
            metrics=model_info["metrics"],
            hyperparameters=model_info["hyperparameters"],
            dataset_lineage=model_info["dataset_lineage"],
        )
        print(f"Registered {task} version {version}")

        print(f"Promoting {task} version {version} to PRODUCTION...")
        promoted = manager.promote_model(task, version)
        if promoted:
            print(f"Successfully promoted {task} to PRODUCTION!")
        else:
            print(f"Failed to promote {task} version {version} to PRODUCTION.")

if __name__ == "__main__":
    register_models()
