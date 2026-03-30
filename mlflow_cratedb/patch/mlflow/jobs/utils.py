# MLflow jobs are started in subprocesses. The code here tries to monkey
# patch relevant routines to forward the required monkeypatching appropriately.
import os
import subprocess
import sys


def _start_huey_consumer_proc(
    huey_instance_key: str,
    max_job_parallelism: int,
):
    """
    Reconfigure to invoke a custom huey consumer module,
    located within this package, to register the CrateDB
    storage handler before.
    """
    from mlflow.environment_variables import MLFLOW_LOGGING_LEVEL
    from mlflow.server.constants import MLFLOW_HUEY_INSTANCE_KEY
    from mlflow.utils.process import _exec_cmd

    cmd = [
        sys.executable,
        "-m",
        "mlflow_cratedb.patch.mlflow.jobs.huey_consumer",
        "mlflow.server.jobs._huey_consumer.huey_instance",
        "-w",
        str(max_job_parallelism),
    ]

    # Add quiet flag if logging level is WARNING or higher
    log_level = (MLFLOW_LOGGING_LEVEL.get() or "INFO").upper()
    if log_level in ("WARNING", "WARN", "ERROR", "CRITICAL"):
        cmd.append("-q")

    return _exec_cmd(
        cmd,
        capture_output=False,
        synchronous=False,
        extra_env={
            MLFLOW_HUEY_INSTANCE_KEY: huey_instance_key,
        },
    )


def _start_periodic_tasks_consumer_proc():
    """
    Reconfigure to invoke a custom huey consumer module,
    located within this package, to register the CrateDB
    storage handler before.
    """
    from mlflow.environment_variables import MLFLOW_LOGGING_LEVEL
    from mlflow.server.jobs.utils import PERIODIC_TASKS_WORKER_COUNT
    from mlflow.utils.process import _exec_cmd

    cmd = [
        sys.executable,
        "-m",
        "mlflow_cratedb.patch.mlflow.jobs.huey_consumer",
        "mlflow.server.jobs._periodic_tasks_consumer.huey_instance",
        "-w",
        str(PERIODIC_TASKS_WORKER_COUNT),
    ]

    # Add quiet flag if logging level is WARNING or higher
    log_level = (MLFLOW_LOGGING_LEVEL.get() or "INFO").upper()
    if log_level in ("WARNING", "WARN", "ERROR", "CRITICAL"):
        cmd.append("-q")

    return _exec_cmd(
        cmd,
        capture_output=False,
        synchronous=False,
    )


def _launch_job_runner(env_map, server_proc_pid):
    """
    Reconfigure to invoke a custom `mlflow.server.jobs._job_runner`,
    located within this package, to register the CrateDB
    storage handler before.
    """
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "mlflow_cratedb.patch.mlflow.jobs._job_runner",
        ],
        env={**os.environ, **env_map, "MLFLOW_SERVER_PID": str(server_proc_pid)},
    )


def patch_jobs_utils():
    """
    Intercept `mlflow.server.jobs.utils._{start,launch}` functions, reconfiguring
    them to invoke wrapper code to run before `mlflow.server.jobs._job_runner`.
    """
    import mlflow.server.jobs.utils as job_utils

    job_utils._start_huey_consumer_proc = _start_huey_consumer_proc
    job_utils._start_periodic_tasks_consumer_proc = _start_periodic_tasks_consumer_proc
    job_utils._launch_job_runner = _launch_job_runner
