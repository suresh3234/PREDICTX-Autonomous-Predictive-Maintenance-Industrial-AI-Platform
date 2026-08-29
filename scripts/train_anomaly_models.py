import os
import sys
from pathlib import Path
import pickle

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

from ml.anomaly.models import (
    AutoencoderDetector,
    IsolationForestDetector,
    OneClassSVMDetector,
    StatisticalThresholdDetector,
)
from ml.features.pipelines import FeaturePipeline


def train_and_evaluate():
    data_dir = "data/synthetic"
    sensor_path = os.path.join(data_dir, "sensor_readings.csv")

    if not os.path.exists(sensor_path):
        print("Sensor readings not found. Please run the generator first.")
        return

    print("Loading sensor data and running feature engineering pipeline...")
    df_raw = pd.read_csv(sensor_path)

    # Run Feature Pipeline
    pipeline = FeaturePipeline()
    df_features = pipeline.transform(df_raw, drop_na=True)

    # Identify feature column names (starts with 'feature_')
    feature_cols = [col for col in df_features.columns if col.startswith("feature_")]
    print(f"Total features extracted: {len(feature_cols)}")

    # Chronological Split
    # We sort by timestamp and split: first 70% of timestamps for training, last 30% for testing
    df_features["timestamp"] = pd.to_datetime(df_features["timestamp"])
    df_features = df_features.sort_values(by="timestamp").reset_index(drop=True)

    split_idx = int(len(df_features) * 0.7)
    df_train_full = df_features.iloc[:split_idx].copy()
    df_test = df_features.iloc[split_idx:].copy()

    # Unsupervised Anomaly Training: Fit ONLY on healthy training records.
    # Healthy record definition: no failure, and RUL is > 12 hours
    healthy_mask = (df_train_full["failure"] == 0) & (df_train_full["RUL"] > 12.0)
    df_train_healthy = df_train_full[healthy_mask]

    print(
        f"Training set: {len(df_train_full)} rows (Healthy subset for fitting: {len(df_train_healthy)} rows)"
    )
    print(f"Testing set: {len(df_test)} rows")

    X_train = df_train_healthy[feature_cols].values
    X_test = df_test[feature_cols].values

    # Define Ground Truth labels for testing evaluation:
    # 1 if RUL <= 4.0 (degrading) or failure == 1, else 0
    y_test = ((df_test["RUL"] <= 4.0) | (df_test["failure"] == 1)).astype(int).values

    # Standardize features
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled_data = scaler.transform(X_train)
    X_test_scaled_data = scaler.transform(X_test)

    # Initialize Detectors
    detectors = {
        "Statistical Z-Score": StatisticalThresholdDetector(),
        "Isolation Forest": IsolationForestDetector(n_estimators=100, random_state=42),
        "One-Class SVM": OneClassSVMDetector(nu=0.05),
        "PyTorch Autoencoder": AutoencoderDetector(
            encoding_dim=8, epochs=15, batch_size=64, lr=0.005
        ),
    }

    results = {}
    best_f1 = -1.0
    best_detector_name = None
    best_detector = None

    for name, detector in detectors.items():
        print(f"Training {name}...")
        detector.fit(X_train_scaled_data)

        # Predict on test data
        scores, probs, severities = detector.predict_details(X_test_scaled_data)

        # Determine predictions based on the 95th percentile threshold
        # (labeled as an anomaly if probability >= 0.5, which corresponds to the p95 threshold)
        predictions = (probs >= 0.5).astype(int)

        # Compute metrics
        prec = precision_score(y_test, predictions, zero_division=0)
        rec = recall_score(y_test, predictions, zero_division=0)
        f1 = f1_score(y_test, predictions, zero_division=0)

        try:
            auc = roc_auc_score(y_test, scores)
        except Exception:
            auc = 0.5

        results[name] = {
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "ROC-AUC": auc,
        }
        print(
            f"{name} Results -> F1: {f1:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f} | AUC: {auc:.3f}"
        )

        if f1 > best_f1:
            best_f1 = f1
            best_detector_name = name
            best_detector = detector

    print("\n=== MODEL COMPARISON SUMMARY ===")
    df_results = pd.DataFrame(results).T
    print(df_results.to_string())

    # Save the best model
    models_dir = "ml/anomaly"
    os.makedirs(models_dir, exist_ok=True)

    model_save_path = os.path.join(models_dir, "best_anomaly_detector.pkl")
    scaler_save_path = os.path.join(models_dir, "anomaly_scaler.pkl")

    # Save scaler and best model wrapper
    with open(model_save_path, "wb") as f:
        pickle.dump(best_detector, f)

    with open(scaler_save_path, "wb") as f:
        pickle.dump(scaler, f)

    print(
        f"\nSaved production candidate model ({best_detector_name}) to {model_save_path}"
    )
    print(f"Saved feature scaler to {scaler_save_path}")


if __name__ == "__main__":
    train_and_evaluate()
