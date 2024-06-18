def patch_sqlalchemy():
    from cratedb_toolkit.sqlalchemy import polyfill_autoincrement

    polyfill_autoincrement()
