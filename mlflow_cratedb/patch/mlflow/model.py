import sqlalchemy as sa
from sqlalchemy.event import listen
from sqlalchemy_cratedb.support import check_uniqueness_factory


def polyfill_uniqueness_constraints():
    """
    Establish a manual uniqueness check on the `SqlExperiment.name` column.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_polyfill_unique` or such.

    TODO: There are two more unique constraints defined on the MLflow data model.
          - SqlExperimentPermission: "experiment_id", "user_id"
          - SqlRegisteredModelPermission: "name", "user_id"
    """
    from mlflow.server.auth.db.models import SqlExperimentPermission, SqlRegisteredModelPermission, SqlUser
    from mlflow.store.model_registry.dbmodels.models import SqlRegisteredModel
    from mlflow.store.tracking.dbmodels.models import SqlExperiment

    listen(SqlExperiment, "before_insert", check_uniqueness_factory(SqlExperiment, "name"))
    listen(
        SqlExperimentPermission,
        "before_insert",
        check_uniqueness_factory(SqlExperimentPermission, "experiment_id", "user_id"),
    )

    listen(SqlRegisteredModel, "before_insert", check_uniqueness_factory(SqlRegisteredModel, "name"))
    listen(
        SqlRegisteredModelPermission,
        "before_insert",
        check_uniqueness_factory(SqlRegisteredModelPermission, "name", "user_id"),
    )

    listen(SqlUser, "before_insert", check_uniqueness_factory(SqlUser, "username"))


def polyfill_refresh_after_dml():
    """
    Run `REFRESH TABLE <tablename>` after each INSERT, UPDATE, and DELETE operation.

    CrateDB is eventually consistent, i.e. write operations are not flushed to
    disk immediately, so readers may see stale data. In a traditional OLTP-like
    application, this is not applicable.

    This SQLAlchemy extension makes sure that data is synchronized after each
    operation manipulating data.

    TODO: Submit patch to `crate-python`, to be enabled by a
          dialect parameter `crate_dml_refresh` or such.
    """
    from mlflow.store.db.base_sql_model import Base

    for mapper in Base.registry.mappers:
        listen(mapper.class_, "after_insert", do_refresh)
        listen(mapper.class_, "after_update", do_refresh)
        listen(mapper.class_, "after_delete", do_refresh)


def do_refresh(mapper, connection, target):
    """
    SQLAlchemy event handler for `after_{insert,update,delete}` events, invoking `REFRESH TABLE`.
    """
    sql = f"REFRESH TABLE {target.__tablename__}"
    connection.execute(sa.text(sql))
