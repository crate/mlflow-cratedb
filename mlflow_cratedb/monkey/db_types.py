def patch_dbtypes():
    """
    Register CrateDB as available database type.
    """
    import mlflow.store.db.db_types as db_types

    db_types.CRATEDB = "crate"

    if db_types.CRATEDB not in db_types.DATABASE_ENGINES:
        db_types.DATABASE_ENGINES.append(db_types.CRATEDB)
