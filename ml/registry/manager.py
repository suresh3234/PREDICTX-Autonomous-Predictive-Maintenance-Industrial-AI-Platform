import json
import os
import pickle
import shutil
from datetime import datetime


class ModelRegistryManager:
    """
    Manages semantic versioning, artifact storage, performance logging,
    transition audits, and promotion gating for PredictX ML models.
    """

    def __init__(self, base_dir="ml/registry/store"):
        self.base_dir = base_dir
        self.registry_json_path = os.path.join(self.base_dir, "registry.json")
        os.makedirs(self.base_dir, exist_ok=True)
        self._load_registry()

        # Baseline metrics gates (thresholds models must pass to be candidates)
        self.gates = {
            "anomaly_detection": {"metric": "F1-Score", "min_val": 0.30},
            "failure_classification": {"metric": "F1-Score (0.5)", "min_val": 0.50},
            "rul_prediction": {"metric": "MAE (hrs)", "max_val": 10.0},
            "sensor_forecasting": {"metric": "Average MAE", "max_val": 4.0},
        }

    def _load_registry(self):
        if os.path.exists(self.registry_json_path):
            with open(self.registry_json_path) as f:
                self.records = json.load(f)
        else:
            self.records = {}

    def _save_registry(self):
        with open(self.registry_json_path, "w") as f:
            json.dump(self.records, f, indent=4)

    def _generate_next_version(self, task: str) -> str:
        if task not in self.records or not self.records[task]:
            return "1.0.0"

        # Get all existing versions
        versions = list(self.records[task].keys())
        # Sort semantic versions (major.minor.patch)
        parsed_versions = []
        for v in versions:
            try:
                parts = list(map(int, v.split(".")))
                parsed_versions.append((parts, v))
            except ValueError:
                continue

        parsed_versions.sort()
        latest_parts, _ = parsed_versions[-1]

        # Increment patch version by default for candidate registry
        next_parts = [latest_parts[0], latest_parts[1], latest_parts[2] + 1]
        return ".".join(map(str, next_parts))

    def register_model(
        self,
        task: str,
        artifacts: dict[str, str],
        metrics: dict[str, float],
        hyperparameters: dict,
        dataset_lineage: str,
    ) -> str:
        """
        Registers a new model candidate, copies its artifacts to the registry store,
        and saves version metadata.
        """
        if task not in [
            "anomaly_detection",
            "failure_classification",
            "rul_prediction",
            "sensor_forecasting",
        ]:
            raise ValueError(f"Unsupported task type: {task}")

        version = self._generate_next_version(task)
        version_dir = os.path.join(self.base_dir, task, version)
        os.makedirs(version_dir, exist_ok=True)

        # Copy model artifacts (pkl models, scalers, encoders) to store
        copied_artifacts = {}
        for key, src_path in artifacts.items():
            if not os.path.exists(src_path):
                raise FileNotFoundError(f"Artifact source file not found: {src_path}")
            dest_name = f"{key}_{os.path.basename(src_path)}"
            dest_path = os.path.join(version_dir, dest_name)
            shutil.copy2(src_path, dest_path)
            copied_artifacts[key] = dest_path

        # Log metadata
        if task not in self.records:
            self.records[task] = {}

        timestamp = datetime.utcnow().isoformat() + "Z"
        self.records[task][version] = {
            "version": version,
            "status": "CANDIDATE",
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "dataset_lineage": dataset_lineage,
            "created_at": timestamp,
            "artifacts": copied_artifacts,
            "transition_audit": [
                {
                    "from_status": "NONE",
                    "to_status": "CANDIDATE",
                    "timestamp": timestamp,
                    "reason": "Initial model registration as candidate.",
                }
            ],
        }
        self._save_registry()
        return version

    def promote_model(self, task: str, version: str) -> bool:
        """
        Gates and promotes a model version to PRODUCTION if it passes baseline thresholds
        and outperforms the current active PRODUCTION model on verification metrics.
        """
        if task not in self.records or version not in self.records[task]:
            raise ValueError(f"Model version {version} not found for task {task}")

        candidate = self.records[task][version]
        gate_rules = self.gates[task]
        metric_name = gate_rules["metric"]

        # Check Candidate against Baseline Gate
        if metric_name not in candidate["metrics"]:
            raise ValueError(
                f"Required evaluation metric {metric_name} missing from version {version}"
            )

        val = candidate["metrics"][metric_name]

        # Check baseline thresholds
        if "min_val" in gate_rules and val < gate_rules["min_val"]:
            print(
                f"Promotion rejected: Version {version} failed baseline gate. {metric_name} is {val:.3f} (required >= {gate_rules['min_val']:.3f})"
            )
            return False
        if "max_val" in gate_rules and val > gate_rules["max_val"]:
            print(
                f"Promotion rejected: Version {version} failed baseline gate. {metric_name} is {val:.3f} (required <= {gate_rules['max_val']:.3f})"
            )
            return False

        # Find current PRODUCTION model
        current_prod_version = None
        for v_name, v_meta in self.records[task].items():
            if v_meta["status"] == "PRODUCTION":
                current_prod_version = v_name
                break

        # Compare Candidate against current active PRODUCTION model
        if current_prod_version:
            prod_meta = self.records[task][current_prod_version]
            prod_val = prod_meta["metrics"][metric_name]

            # Gating check: must outperform production
            is_better = False
            if "min_val" in gate_rules:  # higher is better (F1-score, R2)
                is_better = val > prod_val
            elif "max_val" in gate_rules:  # lower is better (MAE, RMSE)
                is_better = val < prod_val

            if not is_better:
                print(
                    f"Promotion rejected: Version {version} ({metric_name}: {val:.3f}) does not outperform current PRODUCTION version {current_prod_version} ({metric_name}: {prod_val:.3f})"
                )
                return False

            # Downgrade old production model to ARCHIVED
            timestamp = datetime.utcnow().isoformat() + "Z"
            prod_meta["status"] = "ARCHIVED"
            prod_meta["transition_audit"].append(
                {
                    "from_status": "PRODUCTION",
                    "to_status": "ARCHIVED",
                    "timestamp": timestamp,
                    "reason": f"Superseded by newly promoted version {version}.",
                }
            )

        # Promote candidate to PRODUCTION
        timestamp = datetime.utcnow().isoformat() + "Z"
        candidate["status"] = "PRODUCTION"
        candidate["transition_audit"].append(
            {
                "from_status": "CANDIDATE",
                "to_status": "PRODUCTION",
                "timestamp": timestamp,
                "reason": "Outperformed previous model and passed promotion gates.",
            }
        )
        self._save_registry()
        print(
            f"Successfully promoted version {version} to PRODUCTION for task: {task}!"
        )
        return True

    def load_production_model(self, task: str) -> dict:
        """
        Loads and returns the active PRODUCTION model metadata and deserialized artifact dictionary.
        """
        if task not in self.records:
            raise KeyError(f"No registered models for task: {task}")

        prod_meta = None
        for _, v_meta in self.records[task].items():
            if v_meta["status"] == "PRODUCTION":
                prod_meta = v_meta
                break

        if not prod_meta:
            raise RuntimeError(
                f"No PRODUCTION model currently designated for task: {task}"
            )

        loaded_artifacts = {}
        for key, filepath in prod_meta["artifacts"].items():
            if not os.path.exists(filepath):
                raise FileNotFoundError(
                    f"Model artifact file missing from registry store: {filepath}"
                )
            with open(filepath, "rb") as f:
                loaded_artifacts[key] = pickle.load(f)

        return {"metadata": prod_meta, "artifacts": loaded_artifacts}
