"""
About

Use MLflow and CrateDB to track the metrics, parameters, and outcomes of an ML
experiment program using Merlion. It uses the `machine_temperature_system_failure.csv`
dataset from the Numenta Anomaly Benchmark data.

- https://github.com/crate-workbench/mlflow-cratedb
- https://mlflow.org/docs/latest/tracking.html

Usage

Before running the program, optionally define the `MLFLOW_TRACKING_URI` environment
variable, in order to record events and metrics either directly into the database,
or by submitting them to an MLflow Tracking Server.

    # Use CrateDB database directly
    export MLFLOW_TRACKING_URI="crate://crate@localhost/?schema=mlflow"

    # Use MLflow Tracking Server
    export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

Resources

- https://mlflow.org/
- https://github.com/crate/crate
- https://github.com/salesforce/Merlion
- https://github.com/numenta/NAB
"""

import datetime as dt
import os

import mlflow
import numpy as np
import pandas as pd
from crate import client
from merlion.evaluate.anomaly import TSADMetric
from merlion.models.defaults import DefaultDetector, DefaultDetectorConfig
from merlion.utils import TimeSeries


def connect_database():
    """
    Connect to CrateDB, and return database connection object.
    """
    dburi = os.getenv("CRATEDB_HTTP_URL", "http://crate@localhost:4200")
    return client.connect(dburi)


def table_exists(table_name: str) -> bool:
    """
    Check if database table exists.
    """
    conn = connect_database()
    cursor = conn.cursor()
    sql = (
        f"SELECT table_name FROM information_schema.tables "  # noqa: S608
        f"WHERE table_name = '{table_name}' AND table_schema = CURRENT_SCHEMA"
    )
    cursor.execute(sql)
    rowcount = cursor.rowcount
    cursor.close()
    conn.close()
    return rowcount > 0


def import_data(data_table_name: str, anomalies_table_name: str):
    """
    Download Numenta Anomaly Benchmark data, and load into database.
    """

    data = pd.read_csv(
        "https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/machine_temperature_system_failure.csv"
    )

    # Split the data into chunks of 1000 rows each for better insert performance.
    chunk_size = 1000
    chunks = np.array_split(data, int(len(data) / chunk_size))

    # Insert data into CrateDB.
    with connect_database() as conn:
        cursor = conn.cursor()
        # Create the table if it doesn't exist.
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {data_table_name} (timestamp TIMESTAMP, temperature DOUBLE)")
        # Insert the data in chunks.
        for chunk in chunks:
            sql = f"INSERT INTO {data_table_name} (timestamp, temperature) VALUES (?, ?)"  # noqa: S608
            cursor.executemany(sql, list(chunk.itertuples(index=False, name=None)))

        # Create the table to hold known and detected anomalies.
        cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {anomalies_table_name} (
                    "ts_start" TIMESTAMP WITHOUT TIME ZONE,
                    "ts_end" TIMESTAMP WITHOUT TIME ZONE,
                    "score" DOUBLE PRECISION,
                    "experiment_id" BIGINT,
                    "run_id" TEXT,
                    "description" TEXT
                );
            """
        )

        known_anomalies = [
            ("2013-12-15 17:50:00.000000", "2013-12-17 17:00:00.000000"),
            ("2014-01-27 14:20:00.000000", "2014-01-29 13:30:00.000000"),
            ("2014-02-07 14:55:00.000000", "2014-02-09 14:05:00.000000"),
        ]
        cursor.executemany(
            f"INSERT INTO {anomalies_table_name} (ts_start, ts_end) VALUES (?, ?)", known_anomalies  # noqa: S608
        )


def read_data(table_name: str) -> pd.DataFrame:
    """
    Read data from database into pandas DataFrame.
    """
    conn = connect_database()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT DATE_BIN('5 min'::INTERVAL, "timestamp", 0),
                       MAX(temperature)
                FROM {table_name}
                GROUP BY 1
                ORDER BY 1 ASC
            """  # noqa: S608
        )
        data = cursor.fetchall()

    # Convert database response to pandas DataFrame.
    time_series = pd.DataFrame(
        [{"timestamp": pd.Timestamp.fromtimestamp(item[0] / 1000), "value": item[1]} for item in data]
    )
    # Set the timestamp as the index
    return time_series.set_index("timestamp")


def read_anomalies():
    """
    Read anomalies from database into pandas DataFrame.
    """
    conn = connect_database()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ts_start, ts_end FROM anomalies WHERE experiment_id IS NULL")
        data = cursor.fetchall()
        return [[pd.to_datetime(start, unit="ms"), pd.to_datetime(end, unit="ms")] for start, end in data]


def save_anomalies(table_name: str, anomalies: pd.DataFrame, mttd: int):
    """
    Save anomalies from a pandas DataFrame into the database.
    """
    conn = connect_database()
    with conn:
        cursor = conn.cursor()
        rows = []
        for index, row in anomalies.iterrows():
            rows.append(
                (
                    index,
                    index + dt.timedelta(seconds=mttd),
                    row["anom_score"],
                    row["experiment_id"],
                    row["run_id"],
                    None,
                )
            )

        cursor.executemany(
            f"""
                INSERT INTO {table_name} (ts_start, ts_end, score, experiment_id, run_id, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """,  # noqa: S608
            rows,
        )


def run_experiment(time_series: pd.DataFrame, anomalies_table_name: str):
    """
    Run experiment on DataFrame, using Merlion. Track it using MLflow.
    """
    mlflow.set_experiment("numenta-merlion-experiment")

    with mlflow.start_run() as current_run:
        input_test_data = time_series[time_series.index < pd.to_datetime("2013-12-15")]

        train_data = TimeSeries.from_pd(input_test_data)
        test_data = TimeSeries.from_pd(time_series[time_series.index >= pd.to_datetime("2013-12-15")])

        model = DefaultDetector(DefaultDetectorConfig())
        model.train(train_data=train_data)

        test_pred = model.get_anomaly_label(time_series=test_data)

        # Prepare the test labels
        time_frames = read_anomalies()

        time_series["test_labels"] = 0
        for start, end in time_frames:
            time_series.loc[(time_series.index >= start) & (time_series.index <= end), "test_labels"] = 1

        test_labels = TimeSeries.from_pd(time_series["test_labels"])

        p = TSADMetric.Precision.value(ground_truth=test_labels, predict=test_pred)
        r = TSADMetric.Recall.value(ground_truth=test_labels, predict=test_pred)
        f1 = TSADMetric.F1.value(ground_truth=test_labels, predict=test_pred)
        mttd = TSADMetric.MeanTimeToDetect.value(ground_truth=test_labels, predict=test_pred)
        print(f"Precision: {p:.4f}, Recall: {r:.4f}, F1: {f1:.4f}\n" f"Mean Time To Detect: {mttd}")  # noqa: T201

        mlflow.log_input(mlflow.data.from_pandas(input_test_data), context="training")
        mlflow.log_metric("precision", p)
        mlflow.log_metric("recall", r)
        mlflow.log_metric("f1", f1)
        mlflow.log_metric("mttd", mttd.total_seconds())
        mlflow.log_param("anomaly_threshold", model.config.threshold.alm_threshold)
        mlflow.log_param("min_alm_window", model.config.threshold.min_alm_in_window)
        mlflow.log_param("alm_window_minutes", model.config.threshold.alm_window_minutes)
        mlflow.log_param("alm_suppress_minutes", model.config.threshold.alm_suppress_minutes)
        mlflow.log_param("ensemble_size", model.config.model.combiner.n_models)

        # Save the model to MLflow.
        model.save("model")
        mlflow.log_artifact("model")

        anomalies = test_pred.to_pd()
        anomalies = anomalies[anomalies["anom_score"] > 0]
        anomalies["experiment_id"] = current_run.info.experiment_id
        anomalies["run_id"] = current_run.info.run_id

        # Save detected anomalies to CrateDB
        save_anomalies(anomalies_table_name, anomalies, mttd.total_seconds())


def main():
    """
    Provision dataset, and run experiment.
    """

    # Table name where the actual data is stored.
    data_table = "machine_data"

    # Taable name where to store anomalies
    anomalies_table = "anomalies"

    # Provision data to operate on, only once.
    if not table_exists(data_table):
        import_data(data_table, anomalies_table)

    # Read data into pandas DataFrame.
    data = read_data(data_table)

    # Run experiment on data.
    run_experiment(data, anomalies_table)


if __name__ == "__main__":
    main()
