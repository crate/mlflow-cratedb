CRATEDB = "crate"


def patch_dbtypes():
    """
    Register CrateDB as available database type.
    """
    import mlflow.store.db.db_types as db_types

    db_types.CRATEDB = CRATEDB

    if db_types.CRATEDB not in db_types.DATABASE_ENGINES:
        db_types.DATABASE_ENGINES.append(db_types.CRATEDB)

    import mlflow.tracking._tracking_service.utils as tracking_utils

    tracking_utils._tracking_store_registry.register(CRATEDB, tracking_utils._get_sqlalchemy_store)
