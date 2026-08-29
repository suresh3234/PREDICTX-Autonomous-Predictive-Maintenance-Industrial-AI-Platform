import re

import pandas as pd


class DataValidator:
    def __init__(self):
        # Physical boundary constraints (lower_limit, upper_limit)
        self.bounds = {
            "temperature": (-40.0, 200.0),  # Celsius
            "vibration": (0.0, 50.0),  # mm/s
            "pressure": (0.0, 500.0),  # PSI
            "rpm": (0.0, 10000.0),
            "voltage": (0.0, 1000.0),  # V
            "current": (0.0, 200.0),  # A
            "power": (0.0, 100.0),  # kW
            "humidity": (0.0, 100.0),  # %
            "load": (0.0, 100.0),  # %
            "operating_hours": (0.0, 100000.0),
            "RUL": (0.0, 20000.0),
        }

        self.required_columns = [
            "machine_id",
            "timestamp",
            "machine_type",
            "temperature",
            "vibration",
            "pressure",
            "rpm",
            "voltage",
            "current",
            "power",
            "humidity",
            "load",
            "operating_hours",
            "maintenance_count",
            "last_maintenance",
            "failure",
            "failure_type",
            "RUL",
        ]

    def validate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
        """
        Validates the input DataFrame.
        Returns:
            - valid_df: Clean DataFrame with valid rows.
            - quarantined_df: DataFrame containing rejected/quarantined rows with failure reasons.
            - quality_report: Metrics detailing data quality scores.
        """
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), {"status": "empty_dataset"}

        # 1. Initialize logs/reasons
        reasons = pd.Series("", index=df.index)

        # 2. Schema check (missing columns)
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Schema mismatch. Missing required columns: {missing_cols}"
            )

        # 3. Type validations and missing values checks
        null_mask = df[self.required_columns].isnull().any(axis=1)
        reasons[null_mask] += "missing_values; "

        # Validate Machine ID pattern (M[0-9]+)
        machine_pattern = re.compile(r"^M\d+$")
        invalid_machine_ids = df["machine_id"].apply(
            lambda x: not isinstance(x, str) or not machine_pattern.match(x)
        )
        reasons[invalid_machine_ids] += "invalid_machine_id; "

        # 4. Out-of-bounds sensor readings
        for sensor, (low, high) in self.bounds.items():
            if sensor in df.columns:
                # Type cast if needed, non-numeric values will raise errors
                try:
                    vals = pd.to_numeric(df[sensor], errors="coerce")
                    out_of_bounds = (vals < low) | (vals > high) | vals.isnull()
                    # Exclude already marked missing values
                    out_of_bounds = out_of_bounds & ~df[sensor].isnull()
                    reasons[out_of_bounds] += f"out_of_bounds_{sensor}; "
                except Exception:
                    reasons[True] += f"invalid_type_{sensor}; "

        # Check duplicate timestamps per machine
        dup_mask = df.duplicated(subset=["machine_id", "timestamp"], keep=False)
        reasons[dup_mask] += "duplicate_timestamp; "

        # Check timestamp ordering
        # Group by machine and check if current timestamp is greater than previous
        is_unsorted = pd.Series(False, index=df.index)
        for _, group in df.groupby("machine_id"):
            timestamps = pd.to_datetime(group["timestamp"], errors="coerce")
            if timestamps.isnull().any():
                reasons[
                    group.index[timestamps.isnull()]
                ] += "invalid_timestamp_format; "
            else:
                # Check if sorted monotonically increasing
                unsorted_indices = group.index[timestamps.diff().dt.total_seconds() < 0]
                is_unsorted[unsorted_indices] = True
        reasons[is_unsorted] += "out_of_order_timestamp; "

        # 6. Separate Valid and Quarantined data
        is_invalid = reasons != ""
        valid_df = df[~is_invalid].copy()
        quarantined_df = df[is_invalid].copy()
        quarantined_df["quarantine_reason"] = reasons[is_invalid].str.rstrip("; ")

        # 7. Compute Quality Metrics
        total_rows = len(df)
        invalid_rows = len(quarantined_df)

        completeness = (
            1.0
            - (
                df[self.required_columns].isnull().sum().sum()
                / (total_rows * len(self.required_columns))
            )
        ) * 100
        uniqueness = (
            1.0 - (df.duplicated(subset=["machine_id", "timestamp"]).sum() / total_rows)
        ) * 100
        validity = (1.0 - (invalid_rows / total_rows)) * 100

        # Consistency: checks chronological ordering correctness
        consistency = (1.0 - (is_unsorted.sum() / total_rows)) * 100

        quality_report = {
            "total_records": total_rows,
            "valid_records": len(valid_df),
            "quarantined_records": invalid_rows,
            "metrics": {
                "completeness_percentage": round(completeness, 2),
                "uniqueness_percentage": round(uniqueness, 2),
                "validity_percentage": round(validity, 2),
                "consistency_percentage": round(consistency, 2),
            },
            "status": "healthy" if validity > 95 else "degraded",
        }

        return valid_df, quarantined_df, quality_report
