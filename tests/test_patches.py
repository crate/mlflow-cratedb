from mlflow.tracking.fluent import _active_run_stack

from mlflow_cratedb.patch.pycaret.mlflow_logger import clean_active_mlflow_run, set_active_mlflow_run


def test_pycaret_mlflow_logger():

    def run():
        return 42

    initial_stack = _active_run_stack.get().copy()

    with set_active_mlflow_run(run):
        assert run in _active_run_stack.get(), "run should be in active stack"

    assert _active_run_stack.get() == initial_stack, "stack should be restored after exit"

    with clean_active_mlflow_run():
        assert _active_run_stack.get() == [], "stack should be empty inside context"

    assert _active_run_stack.get() == initial_stack, "stack should be restored after clean context"
