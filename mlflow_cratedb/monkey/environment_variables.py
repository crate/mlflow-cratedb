def patch_environment_variables():
    """
    Do not send multiple retrying HTTP requests only if connection is unstable.
    """
    import mlflow.environment_variables as envvars
    from mlflow.environment_variables import _EnvironmentVariable

    envvars.MLFLOW_HTTP_REQUEST_MAX_RETRIES = _EnvironmentVariable("MLFLOW_HTTP_REQUEST_MAX_RETRIES", int, 0)
