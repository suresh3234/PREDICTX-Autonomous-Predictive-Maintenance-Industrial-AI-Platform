import os
import pickle
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from ml.features.pipelines import FeaturePipeline
from ml.rul.models import LSTMRULRegressor, RandomForestRULRegressor


def mean_absolute_percentage_error(y_true, y_pred):
    """Computes MAPE, handling zero targets safely."""
    y_true_safe = np.where(y_true == 0, 1e-8, y_true)
    return np.mean(np.abs((y_true - y_pred) / y_true_safe)) * 100


def create_sequences_per_machine(df, feature_cols, target_col="RUL", seq_length=24):
    """
    Groups data by machine and rolls rows into sequence windows of seq_length.
    Prevents sequences from spanning across different machines.
    """
    X_seq = []
    y_seq = []

    # We group to ensure chronological alignment per machine
    for _, group in df.groupby("machine_id"):
        group_sorted = group.sort_values(by="timestamp")
        X_group = group_sorted[feature_cols].values
        y_group = group_sorted[target_col].values

        if len(group_sorted) >= seq_length:
            for i in range(len(group_sorted) - seq_length + 1):
                X_seq.append(X_group[i : i + seq_length])
                y_seq.append(y_group[i + seq_length - 1])

    return np.array(X_seq), np.array(y_seq)


def train_and_evaluate_rul():
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

    # Ensure chronological order
    df_features["timestamp"] = pd.to_datetime(df_features["timestamp"])
    df_features = df_features.sort_values(by="timestamp").reset_index(drop=True)

    feature_cols = [col for col in df_features.columns if col.startswith("feature_")]
    print(f"Total features extracted: {len(feature_cols)}")

    # Chronological Split (70% train, 30% test)
    split_idx = int(len(df_features) * 0.7)
    df_train = df_features.iloc[:split_idx].copy()
    df_test = df_features.iloc[split_idx:].copy()

    # Fit scaling on training set
    scaler = StandardScaler()
    scaler.fit(df_train[feature_cols].values)

    # Apply scaling (modifying copies to avoid pandas setting warnings)
    df_train_scaled = df_train.copy()
    df_test_scaled = df_test.copy()
    df_train_scaled[feature_cols] = scaler.transform(df_train[feature_cols].values)
    df_test_scaled[feature_cols] = scaler.transform(df_test[feature_cols].values)

    # ------------------ Part 1: Tabular Random Forest baseline ------------------
    print("\n--- Training Tabular Random Forest Baseline ---")
    X_train_tab = df_train_scaled[feature_cols].values
    X_test_tab = df_test_scaled[feature_cols].values

    y_train_tab = df_train_scaled["RUL"].values
    y_test_tab = df_test_scaled["RUL"].values

    rf_reg = RandomForestRULRegressor(n_estimators=100, random_state=42)
    rf_reg.fit(X_train_tab, y_train_tab)

    # Predict and evaluate (ground truth target must also be clipped to max capped RUL)
    rf_preds = rf_reg.predict(X_test_tab)
    y_test_clipped = np.clip(y_test_tab, 0.0, rf_reg.max_rul)

    rf_mae = mean_absolute_error(y_test_clipped, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test_clipped, rf_preds))
    rf_mape = mean_absolute_percentage_error(y_test_clipped, rf_preds)
    rf_r2 = r2_score(y_test_clipped, rf_preds)

    print(
        f"Random Forest baseline -> MAE: {rf_mae:.2f} hrs | RMSE: {rf_rmse:.2f} hrs | MAPE: {rf_mape:.2f}% | R2: {rf_r2:.3f}"
    )

    # ------------------ Part 2: Sequence LSTM regressor ------------------
    print("\n--- Training Sequence LSTM Regressor ---")
    seq_length = 24

    # Create 3D sequences from the scaled DataFrames
    X_train_seq, y_train_seq = create_sequences_per_machine(
        df_train_scaled, feature_cols, target_col="RUL", seq_length=seq_length
    )
    X_test_seq, y_test_seq = create_sequences_per_machine(
        df_test_scaled, feature_cols, target_col="RUL", seq_length=seq_length
    )

    print(f"Train sequences: {X_train_seq.shape} | Test sequences: {X_test_seq.shape}")

    lstm_reg = LSTMRULRegressor(
        seq_length=seq_length, epochs=10, batch_size=128, lr=0.005
    )
    lstm_reg.fit(X_train_seq, y_train_seq)

    lstm_preds = lstm_reg.predict(X_test_seq)
    y_test_seq_clipped = np.clip(y_test_seq, 0.0, lstm_reg.max_rul)

    lstm_mae = mean_absolute_error(y_test_seq_clipped, lstm_preds)
    lstm_rmse = np.sqrt(mean_squared_error(y_test_seq_clipped, lstm_preds))
    lstm_mape = mean_absolute_percentage_error(y_test_seq_clipped, lstm_preds)
    lstm_r2 = r2_score(y_test_seq_clipped, lstm_preds)

    print(
        f"LSTM regressor -> MAE: {lstm_mae:.2f} hrs | RMSE: {lstm_rmse:.2f} hrs | MAPE: {lstm_mape:.2f}% | R2: {lstm_r2:.3f}"
    )

    # ------------------ Part 3: Model Comparison & Saving ------------------
    print("\n=== RUL REGRESSOR MODEL COMPARISON ===")
    results = {
        "Random Forest (Tabular)": [rf_mae, rf_rmse, rf_mape, rf_r2],
        "LSTM (Sequence)": [lstm_mae, lstm_rmse, lstm_mape, lstm_r2],
    }
    df_results = pd.DataFrame(
        results, index=["MAE (hrs)", "RMSE (hrs)", "MAPE (%)", "R2 Score"]
    ).T
    print(df_results.to_string())

    # Save the best model based on MAE
    models_dir = "ml/rul"
    os.makedirs(models_dir, exist_ok=True)

    model_save_path = os.path.join(models_dir, "best_rul_model.pkl")
    scaler_save_path = os.path.join(models_dir, "rul_scaler.pkl")

    # Select best model
    if lstm_mae < rf_mae:
        best_model = lstm_reg
        best_name = "LSTM"
    else:
        best_model = rf_reg
        best_name = "Random Forest"

    with open(model_save_path, "wb") as f:
        pickle.dump(best_model, f)
    with open(scaler_save_path, "wb") as f:
        pickle.dump(scaler, f)

    print(f"\nSaved production RUL model ({best_name}) to {model_save_path}")
    print(f"Saved RUL feature scaler to {scaler_save_path}")


if __name__ == "__main__":
    train_and_evaluate_rul()
