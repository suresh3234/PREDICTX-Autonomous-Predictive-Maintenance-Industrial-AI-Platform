import os
import re

import pandas as pd

from ml.features.pipelines import FeaturePipeline
from ml.registry.manager import ModelRegistryManager
from rag.generator import RAGGenerator


class AgenticCopilot:
    """
    Conversational Copilot that orchestrates predictive models and Hybrid RAG documentation.
    Given a natural language query, it extracts the target machine ID, queries its latest
    sensor metrics, runs ML inferences, retrieves manuals, and generates engineering advice.
    """

    def __init__(
        self,
        registry_manager: ModelRegistryManager,
        rag_generator: RAGGenerator,
        sensor_data_path: str = "data/synthetic/sensor_readings.csv",
    ):
        self.registry_manager = registry_manager
        self.rag_generator = rag_generator
        self.sensor_data_path = sensor_data_path
        self.feature_pipeline = FeaturePipeline()

    def _extract_machine_id(self, query: str) -> str:
        """
        Parses machine codes like M1000, M_1000, M_001, etc., from user queries.
        """
        # Matches patterns like M1000, M-1000, M_1000, M001
        match = re.search(r"\b(M[-_]?\d+)\b", query, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None

    def get_latest_telemetry(self, machine_id: str) -> dict:
        """
        Loads the sensor log database file and returns the latest reading row for the machine.
        """
        if not os.path.exists(self.sensor_data_path):
            raise FileNotFoundError(
                f"Sensor readings database not found at {self.sensor_data_path}"
            )

        df = pd.read_csv(self.sensor_data_path)
        # Normalize code formatting (e.g. M-1000 vs M1000)
        df["machine_id_clean"] = (
            df["machine_id"].str.replace(r"[-_]", "", regex=True).str.upper()
        )
        clean_id = machine_id.replace("-", "").replace("_", "").upper()

        df_mach = df[df["machine_id_clean"] == clean_id]
        if df_mach.empty:
            raise ValueError(
                f"Machine ID '{machine_id}' was not found in the telemetry records."
            )

        # Get the latest reading based on timestamp
        df_mach = df_mach.sort_values(by="timestamp")
        latest_row = df_mach.iloc[-1].to_dict()

        # Cleanup clean columns
        latest_row.pop("machine_id_clean", None)
        return latest_row

    def run_predictive_inference(self, telemetry: dict) -> dict:
        """
        Loads the active production models and makes anomaly, failure risk, and RUL predictions.
        """
        # Create single record dataframe for feature extraction
        df_single = pd.DataFrame([telemetry])
        df_features = self.feature_pipeline.transform(df_single, drop_na=False)

        # Fill missing rolling/lag features with default neutral values
        df_features = df_features.fillna(0.0)
        feature_cols = [
            col
            for col in df_features.columns
            if col.startswith("feature_") and col != "feature_failure_type"
        ]

        predictions = {
            "anomaly_severity": "UNKNOWN",
            "failure_probability": 0.0,
            "failure_type": "No Active Threat",
            "predicted_rul": 24.0,
        }

        # 1. Predict Anomaly Status
        try:
            anomaly_prod = self.registry_manager.load_production_model(
                "anomaly_detection"
            )
            model = anomaly_prod["model"]
            scaler = anomaly_prod["scaler"]
            X_scaled = scaler.transform(df_features[feature_cols].values)
            _, _, sevs = model.predict_details(X_scaled)
            predictions["anomaly_severity"] = sevs[0]
        except Exception:
            predictions["anomaly_severity"] = "NORMAL (Fallback)"

        # 2. Predict Failure Threat Class
        try:
            class_prod = self.registry_manager.load_production_model(
                "failure_classification"
            )
            model = class_prod["model"]
            scaler = class_prod["scaler"]
            X_scaled = scaler.transform(df_features[feature_cols].values)
            prob = float(model.predict_proba(X_scaled)[0])
            predictions["failure_probability"] = prob
            predictions["failure_type"] = (
                "High Risk Degradation" if prob >= 0.35 else "Healthy Baseline"
            )
        except Exception:
            predictions["failure_probability"] = 0.02
            predictions["failure_type"] = "Healthy Baseline"

        # 3. Predict RUL Estimate
        try:
            rul_prod = self.registry_manager.load_production_model("rul_prediction")
            model = rul_prod["model"]
            scaler = rul_prod["scaler"]
            X_scaled = scaler.transform(df_features[feature_cols].values)
            predictions["predicted_rul"] = float(model.predict(X_scaled)[0])
        except Exception:
            predictions["predicted_rul"] = 24.0

        return predictions

    def query(self, user_question: str) -> dict:
        """
        Main query entrypoint.
        """
        machine_id = self._extract_machine_id(user_question)

        if machine_id:
            try:
                # 1. Fetch latest sensor data
                telemetry = self.get_latest_telemetry(machine_id)
                # Filter out metadata for clean printing
                clean_telemetry = {
                    k: v
                    for k, v in telemetry.items()
                    if k not in ["machine_id", "timestamp", "failure_type", "failure"]
                }

                # 2. Run inferences
                predictions = self.run_predictive_inference(telemetry)

                # 3. Retrieve documentation context and generate recommendations
                rag_res = self.rag_generator.generate_response(
                    query=user_question,
                    telemetry=clean_telemetry,
                    predictions=predictions,
                )

                return {
                    "machine_id": machine_id,
                    "telemetry": telemetry,
                    "predictions": predictions,
                    "answer": rag_res["response"],
                    "retrieved_documents": rag_res["retrieved_documents"],
                    "is_mock": rag_res["is_mock"],
                }
            except Exception as e:
                return {
                    "error": f"Failed processing request for machine {machine_id}: {str(e)}"
                }
        else:
            # General query without specific machine reference
            rag_res = self.rag_generator.generate_response(
                query=user_question, telemetry={}, predictions={}
            )
            return {
                "machine_id": None,
                "telemetry": None,
                "predictions": None,
                "answer": rag_res["response"],
                "retrieved_documents": rag_res["retrieved_documents"],
                "is_mock": rag_res["is_mock"],
            }
