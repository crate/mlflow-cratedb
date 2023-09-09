from mlflow_cratedb.patch.crate_python import check_uniqueness_factory


def polyfill_uniqueness_constraints():
    """
    Establish a manual uniqueness check on the `SqlExperiment.name` column.
    """
    from mlflow.store.tracking.dbmodels.models import SqlExperiment
    from sqlalchemy.event import listen

    listen(SqlExperiment, "before_insert", check_uniqueness_factory(SqlExperiment, "name"))
