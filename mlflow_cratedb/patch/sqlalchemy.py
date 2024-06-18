def patch_sqlalchemy():
    from sqlalchemy_cratedb.support import patch_autoincrement_timestamp

    patch_autoincrement_timestamp()
