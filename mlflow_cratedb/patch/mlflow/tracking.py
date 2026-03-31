def patch_tracking():
    """
    Patch the experiment tracking subsystem of MLflow.
    """
    patch_get_percentile_aggregation()
    patch_get_time_bucket_expression()
    patch_create_default_experiment()


def patch_create_default_experiment():
    """
    The `_create_default_experiment` function runs an SQL query sidetracking
    the SQLAlchemy ORM. Thus, it needs to be explicitly patched to invoke
    a corresponding `REFRESH TABLE` statement afterwards.

    TODO: Submit patch to MLflow.
    """
    import sqlalchemy as sa
    from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

    create_default_experiment_dist = SqlAlchemyStore._create_default_experiment

    def _create_default_experiment(self, session):
        from mlflow.store.tracking.dbmodels.models import SqlExperiment

        outcome = create_default_experiment_dist(self, session)
        session.execute(sa.text(f"REFRESH TABLE {SqlExperiment.__tablename__}"))
        return outcome

    SqlAlchemyStore._create_default_experiment = _create_default_experiment  # type: ignore[method-assign]


def patch_get_percentile_aggregation():
    """
    Render the percentile aggregation clause literally, because using query
    parameters with CrateDB's `percentile` function has problems.

    The implementation adds a dedicated handler for CrateDB.

    https://github.com/crate/crate/issues/19207

    TODO: Remove with CrateDB 6.4+.
    """
    import mlflow.store.db.db_types as db_types
    import sqlalchemy as sa
    from mlflow.store.tracking.utils import sql_trace_metrics_utils
    from mlflow.store.tracking.utils.sql_trace_metrics_utils import (
        get_percentile_aggregation as get_percentile_aggregation_dist,
    )

    if getattr(sql_trace_metrics_utils.get_percentile_aggregation, "_mlflow_cratedb_patched", False):
        return

    def get_percentile_aggregation(
        db_type: str, percentile_value: float, column, partition_by_columns: list[sa.Column] | None = None
    ):
        if db_type == db_types.CRATEDB:  # type: ignore[attr-defined]
            percentile_fraction = percentile_value / 100  # Convert to 0-1 range
            # PostgreSQL variant.
            # outcome = sa.func.percentile_cont(percentile_fraction).within_group(column)  # noqa: ERA001
            # CrateDB variant.
            return sa.literal_column(f"percentile({column.name}, {percentile_fraction})")
        return get_percentile_aggregation_dist(db_type, percentile_value, column, partition_by_columns)

    get_percentile_aggregation._mlflow_cratedb_patched = True  # type: ignore[attr-defined]
    sql_trace_metrics_utils.get_percentile_aggregation = get_percentile_aggregation


def patch_get_time_bucket_expression():
    """
    Render the time bucketing clause literally, because using query
    parameters with CrateDB's `floor` function has problems.

    The implementation selects the MSSQL handler, because that already
    renders the clause literally, benefiting CrateDB perfectly.

    https://github.com/crate/crate/issues/19193

    TODO: Review with recent improvements to `crate-python`.
    """
    import sqlalchemy as sa
    from mlflow.entities.trace_metrics import MetricViewType
    from mlflow.store.db import db_types
    from mlflow.store.tracking.utils import sql_trace_metrics_utils
    from mlflow.store.tracking.utils.sql_trace_metrics_utils import (
        get_time_bucket_expression as get_time_bucket_expression_dist,
    )

    if getattr(sql_trace_metrics_utils.get_time_bucket_expression, "_mlflow_cratedb_patched", False):
        return

    def get_time_bucket_expression(view_type: MetricViewType, time_interval_seconds: int, db_type: str) -> sa.Column:
        if db_type == db_types.CRATEDB:  # type: ignore[attr-defined]
            return get_time_bucket_expression_dist(view_type, time_interval_seconds, db_types.MSSQL)
        return get_time_bucket_expression_dist(view_type, time_interval_seconds, db_type)

    get_time_bucket_expression._mlflow_cratedb_patched = True  # type: ignore[attr-defined]
    sql_trace_metrics_utils.get_time_bucket_expression = get_time_bucket_expression
