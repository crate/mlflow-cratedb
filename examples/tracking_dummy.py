"""
About

Use MLflow and CrateDB to track the metrics and parameters of a dummy ML
experiment program.

- https://github.com/crate/mlflow-cratedb
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
"""

import logging
import sys

import mlflow

logger = logging.getLogger()


def run_experiment():
    """
    Run an MLflow dummy workflow, without any data.
    """
    logger.info("Running experiment")
    mlflow.set_experiment("dummy-experiment")

    mlflow.log_metric("precision", 0.33)
    mlflow.log_metric("recall", 0.48)
    mlflow.log_metric("f1", 0.85)
    mlflow.log_metric("mttd", 42.42)
    mlflow.log_param("anomaly_threshold", 0.10)
    mlflow.log_param("min_alm_window", 3600)
    mlflow.log_param("alm_window_minutes", 60)
    mlflow.log_param("alm_suppress_minutes", 5)
    mlflow.log_param("ensemble_size", 25)


def start_adapter():
    logger.info("Initializing CrateDB adapter")
    import mlflow_cratedb  # noqa: F401


def setup_logging():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main():
    """
    Run dummy experiment.
    """
    setup_logging()
    start_adapter()
    run_experiment()


if __name__ == "__main__":
    main()
