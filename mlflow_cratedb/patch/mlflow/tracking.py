def patch_tracking():
    """
    Patch the experiment tracking subsystem of MLflow.
    """
    patch_create_default_experiment()


def patch_create_default_experiment():
    """
    The `_create_default_experiment` function runs an SQL query sidetracking
    the SQLAlchemy ORM. Thus, it needs to be explicitly patched to invoke
    a corresponding `REFRESH TABLE` statement afterwards.
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
