import os
import pickle
import shutil

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

from ml.anomaly.models import OneClassSVMDetector
from ml.classification.models import FailureThreatClassifier
from ml.features.pipelines import FeaturePipeline
from ml.monitoring.drift import AlertSystem, DataDriftDetector
from ml.registry.manager import ModelRegistryManager
from ml.rul.models import RandomForestRULRegressor


class RetrainingPipeline:
    """
    Orchestrates the automated retraining loop for PredictX.
    Triggered by critical data drift alerts or explicit overrides.
    """

    def __init__(
        self, registry_manager: ModelRegistryManager, drift_detector: DataDriftDetector
    ):
        self.registry_manager = registry_manager
        self.drift_detector = drift_detector
        self.feature_pipeline = FeaturePipeline()

    def check_drift_and_retrain(
        self, task: str, raw_data_path: str, force: bool = False
    ) -> dict:
        """
        Loads incoming telemetry data, checks for distribution drift,
        and retrains the model if drift is critical or forced.
        """
        if not os.path.exists(raw_data_path):
            raise FileNotFoundError(
                f"Incoming telemetry data not found at: {raw_data_path}"
            )

        df_raw = pd.read_csv(raw_data_path)
        df_features = self.feature_pipeline.transform(df_raw, drop_na=True)

        # Ensure chronological order
        df_features["timestamp"] = pd.to_datetime(df_features["timestamp"])
        df_features = df_features.sort_values(by="timestamp").reset_index(drop=True)

        feature_cols = [
            col
            for col in df_features.columns
            if col.startswith("feature_") and col != "feature_failure_type"
        ]
        X_actual = df_features[feature_cols].values

        # Run Drift Detection
        drift_alert = "OK"
        if self.drift_detector.baseline_data is not None:
            drift_res = self.drift_detector.detect_drift(X_actual)
            drift_alert = drift_res["alert_level"]

        retrain_triggered = (drift_alert == "CRITICAL") or force

        if not retrain_triggered:
            print(f"Retraining not triggered. Drift status: {drift_alert}.")
            return {
                "drift_alert": drift_alert,
                "retrained": False,
                "promoted": False,
                "version": None,
            }

        # Trigger Retraining Notification Alert
        AlertSystem.send_alert(
            subject=f"Retraining Triggered for {task}",
            message=f"Model retraining initiated. Trigger: Drift status {drift_alert} (Force={force})",
            alert_level="WARNING" if not force else "INFO",
        )

        # Setup temporary directories for candidate serialization
        temp_dir = "ml/retraining/tmp"
        os.makedirs(temp_dir, exist_ok=True)

        scaler = StandardScaler()

        # Chronological Split (70% train, 30% test)
        split_idx = int(len(df_features) * 0.7)
        df_train = df_features.iloc[:split_idx].copy()
        df_test = df_features.iloc[split_idx:].copy()

        X_train_raw = df_train[feature_cols].values
        X_test_raw = df_test[feature_cols].values

        # ------------------ TASK-SPECIFIC RETRAINING ------------------
        if task == "anomaly_detection":
            # Filter healthy subset for training
            healthy_mask = (df_train["failure"] == 0) & (df_train["RUL"] > 12.0)
            X_train_healthy = X_train_raw[healthy_mask.values]
            if len(X_train_healthy) == 0:
                X_train_healthy = X_train_raw  # fallback

            scaler.fit(X_train_healthy)
            X_train_scaled = scaler.transform(X_train_healthy)
            X_test_scaled = scaler.transform(X_test_raw)

            model = OneClassSVMDetector(nu=0.1)
            model.fit(X_train_scaled)

            y_test = (
                ((df_test["RUL"] <= 4.0) | (df_test["failure"] == 1)).astype(int).values
            )
            _, _, sevs = model.predict_details(X_test_scaled)
            preds = np.array([1 if sev != "NORMAL" else 0 for sev in sevs])
            f1 = f1_score(y_test, preds, zero_division=0)

            metrics = {"F1-Score": f1}
            hyperparameters = {"nu": 0.1}

        elif task == "failure_classification":
            scaler.fit(X_train_raw)
            X_train_scaled = scaler.transform(X_train_raw)
            X_test_scaled = scaler.transform(X_test_raw)

            y_train = (df_train["RUL"] <= 4.0).astype(int).values
            y_test = (df_test["RUL"] <= 4.0).astype(int).values

            model = FailureThreatClassifier(model_type="random_forest", random_state=42)
            model.fit(X_train_scaled, y_train)
            model.tune_threshold_cost_sensitive(X_train_scaled, y_train)

            preds = model.predict(X_test_scaled)
            f1 = f1_score(y_test, preds, zero_division=0)

            metrics = {"F1-Score (0.5)": f1}
            hyperparameters = {
                "n_estimators": 100,
                "optimal_threshold": model.optimal_threshold,
            }

        elif task == "rul_prediction":
            scaler.fit(X_train_raw)
            X_train_scaled = scaler.transform(X_train_raw)
            X_test_scaled = scaler.transform(X_test_raw)

            y_train = df_train["RUL"].values
            y_test = df_test["RUL"].values

            model = RandomForestRULRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            preds = model.predict(X_test_scaled)
            y_test_clipped = np.clip(y_test, 0.0, model.max_rul)
            mae = mean_absolute_error(y_test_clipped, preds)

            metrics = {"MAE (hrs)": mae}
            hyperparameters = {"n_estimators": 100, "max_rul": model.max_rul}

        else:
            raise ValueError(f"Retraining not implemented for task: {task}")

        # Serialize model & scaler to temp folder
        model_path = os.path.join(temp_dir, "model.pkl")
        scaler_path = os.path.join(temp_dir, "scaler.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        # Register new candidate
        artifacts = {"model": model_path, "scaler": scaler_path}
        version = self.registry_manager.register_model(
            task=task,
            artifacts=artifacts,
            metrics=metrics,
            hyperparameters=hyperparameters,
            dataset_lineage=raw_data_path,
        )

        # Check promotion gates
        promoted = self.registry_manager.promote_model(task, version)

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

        return {
            "drift_alert": drift_alert,
            "retrained": True,
            "promoted": promoted,
            "version": version,
        }
