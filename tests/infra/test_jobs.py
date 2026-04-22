from unittest.mock import patch

import mlflow.server.jobs.utils as job_utils


def test_huey_launch_job_runner():
    with patch("mlflow_cratedb.patch.mlflow.jobs.utils.subprocess.Popen") as popen:
        job_utils._launch_job_runner({}, 9999)
    popen.assert_called_once()


def test_huey_start_huey_consumer_proc():
    with patch("mlflow.utils.process._exec_cmd") as exec_cmd:
        job_utils._start_huey_consumer_proc("foobar", 0)
    exec_cmd.assert_called_once()


def test_huey_start_periodic_tasks_consumer_proc():
    with patch("mlflow.utils.process._exec_cmd") as exec_cmd:
        job_utils._start_periodic_tasks_consumer_proc()
    exec_cmd.assert_called_once()
