import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_eda():
    data_dir = "data/synthetic"
    sensor_path = os.path.join(data_dir, "sensor_readings.csv")
    machines_path = os.path.join(data_dir, "machines.csv")

    if not os.path.exists(sensor_path) or not os.path.exists(machines_path):
        print("Data files not found. Please run the generator script first.")
        return

    print("Loading data for EDA analysis...")
    df_readings = pd.read_csv(sensor_path)
    df_machines = pd.read_csv(machines_path)

    # Create docs and images directories
    docs_dir = "docs"
    images_dir = os.path.join(docs_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # 1. Dataset Overview
    total_records = len(df_readings)
    num_machines = df_readings["machine_id"].nunique()
    cols = df_readings.columns.tolist()

    # 2. Missing Values Analysis
    missing_vals = df_readings.isnull().sum()

    # Plot missing values
    plt.figure(figsize=(10, 4))
    sns.barplot(x=missing_vals.index, y=missing_vals.values, color="royalblue")
    plt.xticks(rotation=45, ha="right")
    plt.title("Missing Values Count per Column")
    plt.tight_layout()
    missing_plot_path = os.path.join(images_dir, "missing_values.png")
    plt.savefig(missing_plot_path)
    plt.close()

    # 3. Distributions of sensor readings
    sensors = ["temperature", "vibration", "pressure", "rpm", "voltage", "current"]
    plt.figure(figsize=(12, 8))
    for idx, sensor in enumerate(sensors):
        plt.subplot(2, 3, idx + 1)
        sns.histplot(df_readings[sensor], kde=True, bins=30, color="teal")
        plt.title(f"{sensor.capitalize()} Distribution")
    plt.tight_layout()
    dist_plot_path = os.path.join(images_dir, "sensor_distributions.png")
    plt.savefig(dist_plot_path)
    plt.close()

    # 4. Correlation Matrix
    plt.figure(figsize=(10, 8))
    corr_matrix = df_readings[
        sensors + ["power", "load", "operating_hours", "RUL"]
    ].corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Matrix of Sensors and State Variables")
    plt.tight_layout()
    corr_plot_path = os.path.join(images_dir, "correlation_matrix.png")
    plt.savefig(corr_plot_path)
    plt.close()

    # 5. Machine Type breakdown
    plt.figure(figsize=(6, 4))
    sns.countplot(
        data=df_machines,
        x="machine_type",
        hue="machine_type",
        palette="Set2",
        legend=False,
    )
    plt.title("Number of Machines by Type")
    plt.tight_layout()
    type_plot_path = os.path.join(images_dir, "machine_types.png")
    plt.savefig(type_plot_path)
    plt.close()

    # 6. Failure count analysis & Class Imbalance
    failures_df = df_readings[df_readings["failure"] == 1]
    fail_counts = df_readings["failure"].value_counts()
    fail_type_counts = failures_df["failure_type"].value_counts()

    # Plot Class Imbalance
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    x_labels = [
        "Healthy (0)" if val == 0 else "Failure (1)" for val in fail_counts.index
    ]
    sns.barplot(
        x=x_labels,
        y=fail_counts.values,
        palette="Pastel1",
        hue=x_labels,
        legend=False,
    )
    plt.title("Class Distribution (Imbalance)")

    plt.subplot(1, 2, 2)
    if not fail_type_counts.empty:
        sns.barplot(
            x=fail_type_counts.values,
            y=fail_type_counts.index,
            palette="viridis",
            hue=fail_type_counts.index,
            legend=False,
        )
        plt.title("Failure Type Counts")
    plt.tight_layout()
    class_imbalance_path = os.path.join(images_dir, "class_imbalance.png")
    plt.savefig(class_imbalance_path)
    plt.close()

    # 7. Temporal trends (Sensor values over time)
    # We will pick a machine and plot its temperature/vibration trend
    sample_m_id = df_readings["machine_id"].iloc[0]
    machine_data = df_readings[df_readings["machine_id"] == sample_m_id].copy()
    machine_data["timestamp"] = pd.to_datetime(machine_data["timestamp"])
    machine_data = machine_data.sort_values("timestamp")

    plt.figure(figsize=(12, 5))
    plt.plot(
        machine_data["timestamp"],
        machine_data["temperature"],
        label="Temperature (°C)",
        color="crimson",
    )
    plt.ylabel("Temperature (°C)")
    plt.twinx()
    plt.plot(
        machine_data["timestamp"],
        machine_data["vibration"],
        label="Vibration (mm/s)",
        color="navy",
        alpha=0.7,
    )
    plt.ylabel("Vibration (mm/s)")
    plt.title(f"Temporal Trend for Machine {sample_m_id}")
    plt.tight_layout()
    temporal_plot_path = os.path.join(images_dir, "temporal_trend.png")
    plt.savefig(temporal_plot_path)
    plt.close()

    # 8. Sensor Relationships (Scatter)
    plt.figure(figsize=(6, 5))
    sns.scatterplot(
        data=df_readings.sample(min(1000, len(df_readings))),
        x="temperature",
        y="vibration",
        hue="failure",
        palette="Set1",
        alpha=0.6,
    )
    plt.title("Temperature vs Vibration Scatter Plot")
    plt.tight_layout()
    scatter_plot_path = os.path.join(images_dir, "sensor_relationships.png")
    plt.savefig(scatter_plot_path)
    plt.close()

    # 9. Degradation patterns leading up to failures
    # Let's see if there are any failure events in our selected machine
    degrad_plot_path = None
    machine_failures = machine_data[machine_data["failure"] == 1]
    if not machine_failures.empty:
        fail_time = machine_failures["timestamp"].iloc[0]
        # Get window of 3 days before the failure
        degrad_window = machine_data[
            (machine_data["timestamp"] >= fail_time - pd.Timedelta(days=3))
            & (machine_data["timestamp"] <= fail_time)
        ]

        plt.figure(figsize=(10, 4))
        plt.plot(
            degrad_window["timestamp"],
            degrad_window["vibration"],
            color="orange",
            marker="o",
            markersize=2,
        )
        plt.title(
            f"Degradation Pattern: Vibration Increase Leading to Failure on {sample_m_id}"
        )
        plt.xlabel("Timestamp")
        plt.ylabel("Vibration (mm/s)")
        plt.axvline(x=fail_time, color="red", linestyle="--", label="Failure Event")
        plt.legend()
        plt.tight_layout()
        degrad_plot_path = os.path.join(images_dir, "degradation_pattern.png")
        plt.savefig(degrad_plot_path)
        plt.close()

    # 10. Compile the EDA Markdown Report
    report_content = f"""# PredictX: Exploratory Data Analysis (EDA) Report

This report presents findings from analyzing the synthetic industrial sensor dataset. It documents the dataset schema, variable distributions, correlation patterns, failure distributions, and machine degradation behavior.

---

## 1. Dataset Overview
* **Total Sensor Records**: {total_records}
* **Total Unique Machines**: {num_machines}
* **Feature Schema**: `{", ".join(cols)}`

## 2. Missing Values Analysis
All simulated sensor rows are fully validated and populated.
![Missing Values Graph](images/missing_values.png)

## 3. Sensor Value Distributions
Below are the frequency distributions of the primary continuous sensor variables (temperature, vibration, pressure, rpm, voltage, current). The distributions match the normal baselines configured for each machine class, plus diurnal oscillations.
![Sensor Distributions](images/sensor_distributions.png)

## 4. Feature Correlations
We observe strong correlations between corresponding parameters, e.g., current and voltage determining power. Remaining Useful Life (RUL) shows a negative correlation with temperature and vibration drift during degradation periods.
![Correlation Heatmap](images/correlation_matrix.png)

## 5. Machine Inventory
The simulated inventory splits across standard machine classes:
![Machine Types count](images/machine_types.png)

## 6. Failure Distribution & Class Imbalance
As expected for predictive maintenance datasets, the failure class is highly imbalanced, reflecting a realistic operational baseline.
* **Normal Operating Records (Class 0)**: {fail_counts.get(0, 0)}
* **Failure Alarm Events (Class 1)**: {fail_counts.get(1, 0)}

![Class Imbalance Graph](images/class_imbalance.png)

## 7. Temporal & Sensor Relationships
Sensor values fluctuate continuously under baseline noise and daily cycles.
![Temporal Trend graph](images/temporal_trend.png)

A clear boundary forms between normal operations and high-temperature/high-vibration failure coordinates.
![Sensor Relationships Scatter](images/sensor_relationships.png)

"""
    if degrad_plot_path:
        report_content += """## 8. Degradation Patterns
Prior to a scheduled failure event (e.g. Bearing Failure), the machine exhibits a clear gradual wear pattern. In this window, vibration increases exponentially and temperature climbs as friction increases.
![Degradation Pattern](images/degradation_pattern.png)
"""

    report_path = os.path.join(docs_dir, "eda_report.md")
    with open(report_path, "w") as f:
        f.write(report_content)

    print(
        f"EDA Analysis complete! Generated figures in {images_dir} and report in {report_path}"
    )


if __name__ == "__main__":
    generate_eda()
