# Use another WSGI application entrypoint instead of `mlflow.server:app`.
# It is defined in `pyproject.toml` at `[project.entry-points."mlflow.app"]`.
MLFLOW_APP_NAME = "mlflow-cratedb"


def patch_run_server():
    """
    Intercept `mlflow.server._run_server`, and set `--app-name` to
    a wrapper application. This is needed to run the monkeypatching also
    within the gunicorn workers.
    """
    import mlflow.server as server

    _run_server_dist = server._run_server

    def run_server(*args, **kwargs):
        args_dict = _get_args_dict(_run_server_dist, args, kwargs)
        args_effective = list(args)
        if "app_name" in args_dict and args_dict["app_name"] is None:
            args_effective.pop()
            kwargs["app_name"] = MLFLOW_APP_NAME
        return _run_server_dist(*args_effective, **kwargs)

    server._run_server = run_server


def _get_args_dict(fn, args, kwargs):
    """
    Returns a dictionary containing both args and kwargs.

    https://stackoverflow.com/a/40363565
    """
    args_names = fn.__code__.co_varnames[: fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}
