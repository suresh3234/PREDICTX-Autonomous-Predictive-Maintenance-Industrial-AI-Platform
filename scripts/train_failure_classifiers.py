import os
import pickle
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler

from ml.classification.models import FailureThreatClassifier, FailureTypeClassifier
from ml.features.pipelines import FeaturePipeline


def train_and_evaluate_classifiers():
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

    # Sort and ensure clean strings
    df_features["timestamp"] = pd.to_datetime(df_features["timestamp"])
    df_features = df_features.sort_values(by="timestamp").reset_index(drop=True)
    df_features["failure_type"] = (
        df_features["failure_type"].replace("None", np.nan).replace("None", np.nan)
    )

    # Propagate upcoming failure type backward to the degradation window
    df_features["failure_type_prop"] = df_features.groupby("machine_id")[
        "failure_type"
    ].bfill()
    df_features["feature_failure_type"] = "None"

    # Assign target label during active degradation window
    degrad_mask = df_features["RUL"] <= 4.0
    df_features.loc[degrad_mask, "feature_failure_type"] = df_features[
        "failure_type_prop"
    ].fillna("None")

    # Define targets
    # y_binary: 1 if in degradation window (RUL <= 4.0) or failure == 1, else 0
    y_binary = (df_features["RUL"] <= 4.0).astype(int).values

    # feature columns
    feature_cols = [
        col
        for col in df_features.columns
        if col.startswith("feature_") and col != "feature_failure_type"
    ]
    print(f"Total features extracted: {len(feature_cols)}")

    # Chronological Split (70/30)
    split_idx = int(len(df_features) * 0.7)
    df_train = df_features.iloc[:split_idx].copy()
    df_test = df_features.iloc[split_idx:].copy()

    X_train = df_train[feature_cols].values
    X_test = df_test[feature_cols].values

    y_train_bin = y_binary[:split_idx]
    y_test_bin = y_binary[split_idx:]

    # Scale features
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ------------------ Part 1: Binary Threat Classifier ------------------
    model_types = ["logistic_regression", "random_forest", "xgboost", "lightgbm"]
    binary_results = {}

    best_bin_f1 = -1.0
    best_bin_model = None
    best_bin_name = None

    print("\n--- Training Binary Threat Classifiers ---")
    for m_type in model_types:
        clf = FailureThreatClassifier(model_type=m_type, random_state=42)
        clf.fit(X_train_scaled, y_train_bin)

        # Predict probabilities
        probs = clf.predict_proba(X_test_scaled)

        # Calculate standard 0.5 threshold metrics
        preds = (probs >= 0.5).astype(int)

        prec = precision_score(y_test_bin, preds, zero_division=0)
        rec = recall_score(y_test_bin, preds, zero_division=0)
        f1 = f1_score(y_test_bin, preds, zero_division=0)

        try:
            auc = roc_auc_score(y_test_bin, probs)
            pr_auc = average_precision_score(y_test_bin, probs)
        except Exception:
            auc, pr_auc = 0.5, 0.5

        binary_results[m_type] = {
            "Precision (0.5)": prec,
            "Recall (0.5)": rec,
            "F1-Score (0.5)": f1,
            "ROC-AUC": auc,
            "PR-AUC": pr_auc,
        }

        print(
            f"{m_type} (Default) -> F1: {f1:.3f} | Prec: {prec:.3f} | Rec: {rec:.3f} | ROC-AUC: {auc:.3f} | PR-AUC: {pr_auc:.3f}"
        )

        if f1 > best_bin_f1:
            best_bin_f1 = f1
            best_bin_model = clf
            best_bin_name = m_type

    print("\n=== BINARY CLASSIFIER SUMMARY ===")
    print(pd.DataFrame(binary_results).T.to_string())

    # Optimize threshold on Validation subset (we use train scaled subset to simulate tuning)
    # Target business parameters
    c_maint = 150.0  # Preventive repair cost
    c_inspect = 30.0  # False alarm inspection cost
    c_down = 1000.0  # Unscheduled breakdown downtime cost

    print(f"\nOptimizing threshold for {best_bin_name} based on operational costs...")
    opt_t = best_bin_model.tune_threshold_cost_sensitive(
        X_train_scaled,
        y_train_bin,
        cost_maintenance=c_maint,
        cost_inspection=c_inspect,
        cost_downtime=c_down,
    )

    # Evaluate with tuned threshold on test set
    tuned_probs = best_bin_model.predict_proba(X_test_scaled)
    tuned_preds = (tuned_probs >= opt_t).astype(int)

    tuned_prec = precision_score(y_test_bin, tuned_preds, zero_division=0)
    tuned_rec = recall_score(y_test_bin, tuned_preds, zero_division=0)
    tuned_f1 = f1_score(y_test_bin, tuned_preds, zero_division=0)

    print(f"Optimal Threshold: {opt_t:.2f}")
    print(
        f"Tuned Model Metrics -> F1: {tuned_f1:.3f} | Precision: {tuned_prec:.3f} | Recall: {tuned_rec:.3f}"
    )

    # ------------------ Part 2: Multi-Class Failure Type Classifier ------------------
    print("\n--- Training Multi-Class Failure Type Classifier ---")

    # We train the failure type classifier only on rows that are within the degradation window
    train_fail_mask = df_train["feature_failure_type"] != "None"
    test_fail_mask = df_test["feature_failure_type"] != "None"

    X_train_mc = X_train_scaled[train_fail_mask.values]
    X_test_mc = X_test_scaled[test_fail_mask.values]

    y_train_mc_str = df_train.loc[train_fail_mask, "feature_failure_type"].values
    y_test_mc_str = df_test.loc[test_fail_mask, "feature_failure_type"].values

    # Label encode failure modes
    le = LabelEncoder()
    y_train_mc = le.fit_transform(y_train_mc_str)
    y_test_mc = le.transform(y_test_mc_str)

    # Train Multi-Class model (e.g. Random Forest Classifier)
    mc_clf = FailureTypeClassifier(model_type="random_forest", random_state=42)
    mc_clf.fit(X_train_mc, y_train_mc)

    mc_preds = mc_clf.predict(X_test_mc)
    mc_f1 = f1_score(y_test_mc, mc_preds, average="macro", zero_division=0)
    mc_prec = precision_score(y_test_mc, mc_preds, average="macro", zero_division=0)
    mc_rec = recall_score(y_test_mc, mc_preds, average="macro", zero_division=0)

    print("Multi-Class Diagnostic Classifier (Random Forest) Metrics:")
    print(
        f"Macro F1: {mc_f1:.3f} | Macro Precision: {mc_prec:.3f} | Macro Recall: {mc_rec:.3f}"
    )

    # Save the models
    models_dir = "ml/classification"
    os.makedirs(models_dir, exist_ok=True)

    binary_model_path = os.path.join(models_dir, "best_failure_threat_model.pkl")
    multiclass_model_path = os.path.join(models_dir, "best_failure_type_model.pkl")
    label_encoder_path = os.path.join(models_dir, "failure_label_encoder.pkl")
    scaler_path = os.path.join(models_dir, "classification_scaler.pkl")

    with open(binary_model_path, "wb") as f:
        pickle.dump(best_bin_model, f)
    with open(multiclass_model_path, "wb") as f:
        pickle.dump(mc_clf, f)
    with open(label_encoder_path, "wb") as f:
        pickle.dump(le, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    print(f"\nSaved production Binary Threat Model to {binary_model_path}")
    print(f"Saved production Multi-Class Diagnostic Model to {multiclass_model_path}")
    print(f"Saved classification feature scaler to {scaler_path}")


if __name__ == "__main__":
    train_and_evaluate_classifiers()
