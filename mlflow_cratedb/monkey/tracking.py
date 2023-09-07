def patch_sqlalchemy_store():
    from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore

    SqlAlchemyStore.create_experiment = create_experiment


def create_experiment(self, name, artifact_location=None, tags=None):
    """
    MLflow's `create_experiment`, but with a synchronization patch for CrateDB.
    It is annotated with "Patch begin|end" in the code below.
    """
    import sqlalchemy
    from mlflow import MlflowException
    from mlflow.entities import LifecycleStage
    from mlflow.protos.databricks_pb2 import RESOURCE_ALREADY_EXISTS
    from mlflow.store.tracking.dbmodels.models import SqlExperiment, SqlExperimentTag
    from mlflow.utils.time_utils import get_current_time_millis
    from mlflow.utils.uri import resolve_uri_if_local
    from mlflow.utils.validation import _validate_experiment_name

    _validate_experiment_name(name)
    if artifact_location:
        artifact_location = resolve_uri_if_local(artifact_location)
    with self.ManagedSessionMaker() as session:
        try:
            creation_time = get_current_time_millis()
            experiment = SqlExperiment(
                name=name,
                lifecycle_stage=LifecycleStage.ACTIVE,
                artifact_location=artifact_location,
                creation_time=creation_time,
                last_update_time=creation_time,
            )
            experiment.tags = [SqlExperimentTag(key=tag.key, value=tag.value) for tag in tags] if tags else []
            session.add(experiment)

            # Patch begin.
            # TODO: Submit upstream?
            session.flush()

            # TODO: This is specific to CrateDB. Implement as an SQLAlchemy hook in some way?
            session.execute(sqlalchemy.text(f"REFRESH TABLE {SqlExperiment.__tablename__};"))
            # Patch end.

            if not artifact_location:
                # this requires a double write. The first one to generate an autoincrement-ed ID
                eid = session.query(SqlExperiment).filter_by(name=name).first().experiment_id
                experiment.artifact_location = self._get_artifact_location(eid)
        except sqlalchemy.exc.IntegrityError as e:
            raise MlflowException(
                f"Experiment(name={name}) already exists. Error: {e}",
                RESOURCE_ALREADY_EXISTS,
            ) from e

        session.flush()
        return str(experiment.experiment_id)
