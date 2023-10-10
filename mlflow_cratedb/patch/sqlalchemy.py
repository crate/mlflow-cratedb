def patch_sqlalchemy():
    from cratedb_toolkit.sqlalchemy import patch_inspector, polyfill_autoincrement

    patch_inspector()
    polyfill_autoincrement()
