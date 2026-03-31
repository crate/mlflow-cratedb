def patch_environment_variables():
    """
    Do not send multiple retrying HTTP requests only if connection is unstable.
    """
    import mlflow.environment_variables as envvars
    from mlflow.environment_variables import _EnvironmentVariable

    envvars.MLFLOW_HTTP_REQUEST_MAX_RETRIES = _EnvironmentVariable("MLFLOW_HTTP_REQUEST_MAX_RETRIES", int, 0)


def patch_constants():
    """
    Rename field names that contain dots.

    InvalidColumnNameException["field.name" contains a dot]
    https://github.com/crate/crate/issues/16063
    """
    from mlflow.tracing import constant
    from mlflow.utils import mlflow_tags

    constant.SpanAttributeKey.MODEL = "mlflow-llm-model"
    mlflow_tags.MLFLOW_USER = "mlflow-user"
