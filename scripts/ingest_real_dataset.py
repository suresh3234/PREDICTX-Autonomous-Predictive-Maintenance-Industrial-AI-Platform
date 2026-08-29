import os
import urllib.request

import numpy as np
import pandas as pd


def ingest_real_world_dataset():
    data_dir = "data/synthetic"
    os.makedirs(data_dir, exist_ok=True)
    target_path = os.path.join(data_dir, "sensor_readings.csv")

    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    print(
        f"Downloading real-world AI4I 2020 Predictive Maintenance dataset from:\n{url}"
    )

    try:
        temp_csv, _ = urllib.request.urlretrieve(url)
        df_raw = pd.read_csv(temp_csv)
        print(f"Successfully downloaded dataset with shape: {df_raw.shape}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return

    # Clean column names (remove brackets, spaces, etc.)
    df_raw.columns = [col.strip() for col in df_raw.columns]
    print("Columns found in raw dataset:", list(df_raw.columns))

    # ------------------ MAPPING TO PREDICTX SCHEMA ------------------
    # We partition the 10,000 rows into 10 virtual machines of 1,000 rows each.
    # This provides continuous sequential sensor readings per machine.
    df_raw["machine_index"] = np.floor(np.arange(len(df_raw)) / 1000).astype(int)
    df_raw["machine_id"] = df_raw["machine_index"].apply(lambda x: f"M{1000 + x}")

    # Map machine types
    type_map = {"L": "Light Industrial", "M": "Medium Duty", "H": "Heavy Duty"}
    df_raw["machine_type"] = df_raw["Type"].map(type_map).fillna("Medium Duty")

    # Sensor mapping (Celsius = Kelvin - 273.15)
    df_raw["temperature"] = df_raw["Air temperature [K]"] - 273.15
    df_raw["vibration"] = (
        df_raw["Process temperature [K]"] - 273.15
    )  # process temperature tracks friction/heat
    df_raw["pressure"] = df_raw[
        "Torque [Nm]"
    ]  # torque is mechanical stress/force proxy
    df_raw["rpm"] = df_raw["Rotational speed [rpm]"]

    # Simulate voltage and current based on load
    np.random.seed(42)
    df_raw["voltage"] = 220.0 + np.random.normal(loc=0.0, scale=1.5, size=len(df_raw))
    # current draws proportional to Torque (pressure) and RPM
    df_raw["current"] = (
        (df_raw["pressure"] * df_raw["rpm"] / 10000.0)
        + 5.0
        + np.random.normal(0.0, 0.2, len(df_raw))
    )
    df_raw["power"] = (df_raw["voltage"] * df_raw["current"]) / 1000.0

    # Additional environmental & operational variables
    df_raw["humidity"] = 50.0 + np.random.normal(0.0, 3.0, len(df_raw))
    df_raw["load"] = (df_raw["pressure"] / df_raw["pressure"].max()) * 100.0
    df_raw["operating_hours"] = df_raw["Tool wear [min]"] / 60.0  # tool wear in hours

    df_raw["maintenance_count"] = (df_raw["Tool wear [min]"] / 80).astype(int)

    # Timestamps (10-minute intervals starting from 2026-08-01)
    base_time = pd.to_datetime("2026-08-01 00:00:00")
    df_raw["row_idx_within_machine"] = df_raw.groupby("machine_id").cumcount()
    df_raw["timestamp"] = df_raw["row_idx_within_machine"].apply(
        lambda x: base_time + pd.Timedelta(minutes=10 * x)
    )
    df_raw["last_maintenance"] = base_time  # default baseline

    # Ground Truth mapping
    df_raw["failure"] = df_raw["Machine failure"]

    # Map specific failure types
    df_raw["failure_type"] = "None"
    df_raw.loc[df_raw["TWF"] == 1, "failure_type"] = "Tool Wear Failure"
    df_raw.loc[df_raw["HDF"] == 1, "failure_type"] = "Heat Dissipation Failure"
    df_raw.loc[df_raw["PWF"] == 1, "failure_type"] = "Power Failure"
    df_raw.loc[df_raw["OSF"] == 1, "failure_type"] = "Overstrain Failure"
    df_raw.loc[df_raw["RNF"] == 1, "failure_type"] = "Random Failure"
    # General fallback for raw machine failures without subtype flags
    df_raw.loc[
        (df_raw["failure"] == 1) & (df_raw["failure_type"] == "None"), "failure_type"
    ] = "General Failure"

    # ------------------ CALCULATING REMAINING USEFUL LIFE (RUL) ------------------
    # For each row, calculate hours remaining until the next failure event on that machine.
    df_raw["RUL"] = 150.0  # Default initial value

    for _, group in df_raw.groupby("machine_id"):
        # Sort chronologically to make calculations correct
        group = group.sort_values(by="timestamp")
        failure_indices = group[group["failure"] == 1].index.tolist()

        group_indices = group.index.tolist()
        for idx in group_indices:
            current_time = group.loc[idx, "timestamp"]
            # Find the next future failure index
            future_failures = [f_idx for f_idx in failure_indices if f_idx >= idx]

            if future_failures:
                next_fail_idx = future_failures[0]
                next_fail_time = group.loc[next_fail_idx, "timestamp"]
                time_delta = next_fail_time - current_time
                df_raw.loc[idx, "RUL"] = time_delta.total_seconds() / 3600.0
            else:
                # If no further failure exists, count down to the end of the sequence
                end_time = group["timestamp"].max()
                time_delta = end_time - current_time
                df_raw.loc[idx, "RUL"] = (time_delta.total_seconds() / 3600.0) + 50.0

    # Select columns matching our schema
    schema_cols = [
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
    df_output = df_raw[schema_cols]

    # Save mapped real-world data
    df_output.to_csv(target_path, index=False)
    print(
        f"\nReal-world dataset successfully ingested, mapped, and saved to: {target_path}"
    )
    print(
        f"Total rows: {len(df_output)} | Virtual Machines: {df_output['machine_id'].nunique()}"
    )


if __name__ == "__main__":
    ingest_real_world_dataset()
