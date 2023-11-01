"""
About

Use MLflow and CrateDB to track the metrics, parameters, and outcomes of an ML
experiment program using PyCaret. It uses the Real-world sales forecasting benchmark data
dataset from 4TU.ResearchData.

- https://github.com/crate-workbench/mlflow-cratedb
- https://mlflow.org/docs/latest/tracking.html

Usage

Before running the program, define the `MLFLOW_TRACKING_URI` environment
variable, in order to record events and metrics either directly into the database,
or by submitting them to an MLflow Tracking Server.

    # Use CrateDB database directly
    export MLFLOW_TRACKING_URI="crate://crate@localhost/?schema=mlflow"

    # Use MLflow Tracking Server
    export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

Optionally, you might set the `CRATEDB_HTTP_URL` environment variable, in order
to define the CrateDB HTTP URL. The default value is `http://crate@localhost:4200`.

    # Use custom CrateDB HTTP URL to connect to a CrateDB Cloud instance
    # Replace <username>, <password>, and <instance> with the values
    # from your CrateDB Cloud instance
    export CRATEDB_HTTP_URL="https://<username>:<password>@<instance>.aks1.westeurope.azure.cratedb.net:4200"

Resources

- https://mlflow.org/
- https://github.com/crate/crate
- https://github.com/pycaret/pycaret
- https://data.4tu.nl/articles/dataset/Real-world_sales_forecasting_benchmark_data_-_Extended_version/14406134/1
"""

import os
import time

import numpy as np
import pandas as pd
from crate import client
from mlflow import get_tracking_uri
from mlflow.models import infer_signature
from mlflow.sklearn import log_model
from pycaret.time_series import blend_models, compare_models, finalize_model, save_model, setup, tune_model

import mlflow_cratedb  # noqa: F401


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

def import_data(data_table_name: str):
    """
    Download Real-world sales forecasting benchmark data, and load into database.
    """

    target_data = pd.read_csv(
        "https://data.4tu.nl/file/539debdb-a325-412d-b024-593f70cba15b/a801f5d4-5dfe-412a-ace2-a64f93ad0010"
    )
    related_data = pd.read_csv(
        "https://data.4tu.nl/file/539debdb-a325-412d-b024-593f70cba15b/f2bd27bd-deeb-4933-bed7-29325ee05c2e",
        header=None,
    )
    related_data.columns = ["item", "org", "date", "unit_price"]
    data = target_data.merge(related_data, on=["item", "org", "date"])
    data["total_sales"] = data["unit_price"] * data["quantity"]
    data["date"] = pd.to_datetime(data["date"])

    # Split the data into chunks of 1000 rows each for better insert performance
    chunk_size = 1000
    chunks = np.array_split(data, int(len(data) / chunk_size))

    # Insert the data into CrateDB
    with connect_database() as conn:
        cursor = conn.cursor()
        # Create the table if it doesn't exist
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {data_table_name}
            ("item" TEXT,
            "org" TEXT,
            "date" TIMESTAMP,
            "quantity" BIGINT,
            "unit_price" DOUBLE PRECISION,
            "total_sales" DOUBLE PRECISION)""")

        # Insert the data in chunks
        for chunk in chunks:
            cursor.executemany(
                f"""INSERT INTO {data_table_name}
                (item, org, date, quantity, unit_price, total_sales)
                VALUES (?, ?, ?, ?, ?, ?)""",  # noqa: S608
                list(chunk.itertuples(index=False, name=None)),
            )
        cursor.close()


def refresh_table(table_name: str):
    """Refresh the table, to make sure the data is up to date.
    Required due to crate being eventually consistent."""

    with connect_database() as conn:
        cursor = conn.cursor()
        cursor.execute(f"REFRESH TABLE {table_name}")
        cursor.close()

def read_data(table_name: str) -> pd.DataFrame:
    """
    Read data from database into pandas DataFrame.
    """

    query = f"""
            SELECT
                DATE_TRUNC('month', date) as month,
                SUM(total_sales) AS total_sales
            FROM {table_name}
            GROUP BY month
            ORDER BY month
        """
    with connect_database() as conn:
        data = pd.read_sql(query, conn)

    data["month"] = pd.to_datetime(data["month"], unit="ms")
    data.sort_values(by=["month"], inplace=True)
    return data


def run_experiment(data: pd.DataFrame):
    """
    Run experiment on DataFrame, using PyCaret. Track it using MLflow.
    The mlflow tracking is automatically executed by PyCaret.
    """

    # creating a blend of 3 models, which perform best on MASE metric
    pycaret_setup = setup(data,
                          fh=15,
                          target="total_sales",
                          index="month",
                          log_experiment=True,
                          verbose=False)

    best3 = compare_models(sort="MASE", n_select=3)
    tuned_models = [tune_model(i) for i in best3]
    blended = blend_models(estimator_list=tuned_models, optimize="MASE")
    best_model = finalize_model(blended)

    # saving the model to disk
    if not os.path.exists("model"):
        os.makedirs("model")
    save_model(best_model, 'model/crate-salesforecast')

    # Create a name for the model
    timestamp = int(time.time())

    # registering the model with mlflow, but only if MLFLOW_TRACKING_URI is
    # set to a tracking server
    if not get_tracking_uri().startswith("file://"):
        y_pred = best_model.predict()
        signature = infer_signature(None, y_pred)
        log_model(
            sk_model=best_model,
            artifact_path="crate-salesforecast",
            signature=signature,
            registered_model_name=f"crate-salesforecast-model-{timestamp}",
        )
    else:
        print(# noqa: T201
            "MLFLOW_TRACKING_URI is not set to a tracking server, "
            "so the model will not be registered with mlflow")


def main():
    """
    Provision dataset, and run experiment.
    """

    # Table name where the actual data is stored.
    data_table = "sales_data_for_forecast"

    # Provision data to operate on, only once.
    if not table_exists(data_table):
        import_data(data_table)

        # Refresh the table - due to crate's eventual consistency.
        refresh_table(data_table)

    # Read data into pandas DataFrame.
    data = read_data(data_table)
    # Run experiment on data.
    run_experiment(data)


if __name__ == "__main__":
    main()
