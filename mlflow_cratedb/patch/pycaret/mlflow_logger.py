"""
## Problem
AttributeError: 'ThreadLocalVariable' object has no attribute 'copy'
https://github.com/pycaret/pycaret/issues/4100

## Solution
https://github.com/pycaret/pycaret/pull/4146

## Source
https://github.com/pycaret/pycaret/blob/master/pycaret/loggers/mlflow_logger.py
"""

from contextlib import contextmanager

from mlflow.tracking.fluent import _active_run_stack


@contextmanager
def set_active_mlflow_run(run):
    """Set active MLFlow run to `run` and then back to what it was."""
    current = _active_run_stack.get()
    new_stack = current.copy()
    new_stack.append(run)
    _active_run_stack.set(new_stack)
    try:
        yield
    finally:
        current = _active_run_stack.get()
        new_stack = current.copy()
        try:
            new_stack.remove(run)
        except ValueError:
            pass
        _active_run_stack.set(new_stack)


@contextmanager
def clean_active_mlflow_run():
    """Trick MLFlow into thinking there are no active runs."""
    old_stack = _active_run_stack.get().copy()
    _active_run_stack.set([])
    try:
        yield
    finally:
        current = _active_run_stack.get()
        active_run = current[-1] if current else None
        _active_run_stack.set(old_stack)
        if active_run is not None:
            current = _active_run_stack.get().copy()
            current.append(active_run)
            _active_run_stack.set(current)


def patch_logger():
    try:
        import pycaret.loggers.mlflow_logger as mlflow_logger

        mlflow_logger.set_active_mlflow_run = set_active_mlflow_run
        mlflow_logger.clean_active_mlflow_run = clean_active_mlflow_run
    except ImportError:
        pass
