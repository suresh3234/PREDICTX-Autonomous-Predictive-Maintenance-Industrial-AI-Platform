import os
import pickle
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

from ml.features.pipelines import FeaturePipeline
from ml.forecasting.models import LSTMForecaster, RidgeForecaster

# Sensors to forecast
SENSORS = ["temperature", "vibration", "pressure", "power", "current"]
HORIZONS = {"1h": 6, "6h": 36, "24h": 144}


def create_forecasting_sequences(df, feature_cols, target_cols, seq_length=24):
    """
    Creates 3D sequence arrays for features and 2D target arrays for forecasting,
    aligning them chronologically and preventing sequence overlap across machine IDs.
    """
    X_seq = []
    y_seq = []

    for _, group in df.groupby("machine_id"):
        group_sorted = group.sort_values(by="timestamp")
        X_group = group_sorted[feature_cols].values
        y_group = group_sorted[target_cols].values

        if len(group_sorted) >= seq_length:
            for i in range(len(group_sorted) - seq_length + 1):
                X_seq.append(X_group[i : i + seq_length])
                y_seq.append(y_group[i + seq_length - 1])

    return np.array(X_seq), np.array(y_seq)


def train_and_evaluate_forecasters():
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

    df_features["timestamp"] = pd.to_datetime(df_features["timestamp"])
    df_features = df_features.sort_values(by="timestamp").reset_index(drop=True)

    feature_cols = [col for col in df_features.columns if col.startswith("feature_")]

    # Construct target columns by shifting values backwards (future values)
    target_cols = []
    for sensor in SENSORS:
        for name, steps in HORIZONS.items():
            col_name = f"target_{sensor}_{name}"
            df_features[col_name] = df_features.groupby("machine_id")[sensor].shift(
                -steps
            )
            target_cols.append(col_name)

    # Drop rows containing NaNs in target columns (the tail of each sequence where future values do not exist)
    df_features = df_features.dropna(subset=target_cols).reset_index(drop=True)
    print(f"Total dataset size after target shifting: {len(df_features)} rows")
    print(f"Total features: {len(feature_cols)} | Total targets: {len(target_cols)}")

    # Chronological Split (70/30)
    split_idx = int(len(df_features) * 0.7)
    df_train = df_features.iloc[:split_idx].copy()
    df_test = df_features.iloc[split_idx:].copy()

    # Standardize features
    scaler = StandardScaler()
    scaler.fit(df_train[feature_cols].values)

    df_train_scaled = df_train.copy()
    df_test_scaled = df_test.copy()
    df_train_scaled[feature_cols] = scaler.transform(df_train[feature_cols].values)
    df_test_scaled[feature_cols] = scaler.transform(df_test[feature_cols].values)

    # ------------------ Part 1: Tabular Ridge forecaster baseline ------------------
    print("\n--- Training Tabular Ridge Forecaster Baseline ---")
    X_train_tab = df_train_scaled[feature_cols].values
    X_test_tab = df_test_scaled[feature_cols].values

    y_train = df_train_scaled[target_cols].values
    y_test = df_test_scaled[target_cols].values

    ridge_clf = RidgeForecaster(alpha=10.0)
    ridge_clf.fit(X_train_tab, y_train)

    ridge_preds = ridge_clf.predict(X_test_tab)

    # Compute metrics per column
    ridge_maes = []
    ridge_r2s = []

    for idx, _ in enumerate(target_cols):
        mae = mean_absolute_error(y_test[:, idx], ridge_preds[:, idx])
        r2 = r2_score(y_test[:, idx], ridge_preds[:, idx])
        ridge_maes.append(mae)
        ridge_r2s.append(r2)

    print(
        f"Ridge Baseline -> Average MAE: {np.mean(ridge_maes):.3f} | Average R2: {np.mean(ridge_r2s):.3f}"
    )

    # ------------------ Part 2: Sequence LSTM forecaster ------------------
    print("\n--- Training Sequence LSTM Forecaster ---")
    seq_length = 24

    X_train_seq, y_train_seq = create_forecasting_sequences(
        df_train_scaled, feature_cols, target_cols, seq_length=seq_length
    )
    X_test_seq, y_test_seq = create_forecasting_sequences(
        df_test_scaled, feature_cols, target_cols, seq_length=seq_length
    )

    print(
        f"Train sequences shape: {X_train_seq.shape} | Target shape: {y_train_seq.shape}"
    )

    lstm_clf = LSTMForecaster(
        seq_length=seq_length, epochs=10, batch_size=128, lr=0.005
    )
    lstm_clf.fit(X_train_seq, y_train_seq)

    lstm_preds = lstm_clf.predict(X_test_seq)

    lstm_maes = []
    lstm_r2s = []

    for idx, _ in enumerate(target_cols):
        mae = mean_absolute_error(y_test_seq[:, idx], lstm_preds[:, idx])
        r2 = r2_score(y_test_seq[:, idx], lstm_preds[:, idx])
        lstm_maes.append(mae)
        lstm_r2s.append(r2)

    print(
        f"LSTM Forecaster -> Average MAE: {np.mean(lstm_maes):.3f} | Average R2: {np.mean(lstm_r2s):.3f}"
    )

    # ------------------ Part 3: Model Comparison & Saving ------------------
    print("\n=== MODEL COMPARISON BY CHANNEL ===")
    comparison_data = []
    for idx, col in enumerate(target_cols):
        clean_name = col.replace("target_", "")
        comparison_data.append(
            {
                "Channel": clean_name,
                "Ridge MAE": f"{ridge_maes[idx]:.3f}",
                "LSTM MAE": f"{lstm_maes[idx]:.3f}",
                "Ridge R2": f"{ridge_r2s[idx]:.3f}",
                "LSTM R2": f"{lstm_r2s[idx]:.3f}",
            }
        )
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))

    # Save the best model
    models_dir = "ml/forecasting"
    os.makedirs(models_dir, exist_ok=True)

    model_save_path = os.path.join(models_dir, "best_forecaster_model.pkl")
    scaler_save_path = os.path.join(models_dir, "forecaster_scaler.pkl")

    # Choose best model
    if np.mean(lstm_maes) < np.mean(ridge_maes):
        best_model = lstm_clf
        best_name = "LSTM"
    else:
        best_model = ridge_clf
        best_name = "Ridge"

    with open(model_save_path, "wb") as f:
        pickle.dump(best_model, f)
    with open(scaler_save_path, "wb") as f:
        pickle.dump(scaler, f)

    print(f"\nSaved production Forecaster model ({best_name}) to {model_save_path}")
    print(f"Saved Forecaster feature scaler to {scaler_save_path}")


if __name__ == "__main__":
    train_and_evaluate_forecasters()
