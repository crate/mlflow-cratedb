# Changelog


## in progress

## 2023-11-24 v2.8.1
- Update to [MLflow 2.8.1](https://github.com/mlflow/mlflow/releases/tag/v2.8.1)

## 2023-11-24 v2.8.0
- Update to [MLflow 2.8.0](https://github.com/mlflow/mlflow/releases/tag/v2.8.0)

  Attention: Please note when updating from a previous version:
  The database model changed slightly, adding the `storage_location`
  column to the `model_versions` table. In order to accommodate the
  update, run this SQL DDL command, for example using `crash`.
  ```sql
  ALTER TABLE mlflow.model_versions ADD COLUMN storage_location TEXT NULL;
  ```
  Note that it is always advised to create backups of your database content.
  This is an excellent opportunity to do that.

- Fix uniqueness constraints
  - `mlflow.server.auth.db.models.SqlUser.username`.
  - `m.s.a.d.m.SqlExperimentPermission`: "experiment_id", "user_id"
  - `m.s.a.d.m.SqlRegisteredModelPermission`: "name", "user_id"
- Fix OCI build re. `psutil` package on aarch64.
- Optimize OCI image sizes.
- Add example experiment program `tracking_pycaret.py`, and a corresponding
  test case. Thanks, @andnig.
- Examples: Use `refresh_table` to synchronize CrateDB write operations.

## 2023-11-01 v2.7.1
- Fix uniqueness constraint with `SqlRegisteredModel.name`. Thanks, @andnig.
- Downgrade to Python 3.10. A few packages like PyCaret are not ready for
  Python 3.11 yet. Thanks, @andnig.

## 2023-10-11 v0.2.0
- Update to [MLflow 2.7](https://github.com/mlflow/mlflow/releases/tag/v2.7.0)
- Improve `table_exists()` in `example_merlion.py`
- SQLAlchemy: Use server-side `now()` function for "autoincrement" columns
- Use SQLAlchemy patches and polyfills from `cratedb-toolkit`
- Update and improve documentation

## 2023-09-12 v0.1.1
- Documentation: Improve "Container Usage" page
- Documentation: Update README with real `pip install` command

## 2023-09-12 v0.1.0
- Initial thing, proof-of-concept
- Add software tests
- CLI: Add `mlflow-cratedb cratedb --version` command
- Project: Add `versioningit`, for effortless versioning
- Add patch for SQLAlchemy Inspector's `get_table_names`
- Reorder CrateDB SQLAlchemy Dialect polyfills
- Add example experiment program `tracking_merlion.py`, and corresponding tests
- Add example program `tracking_dummy.py`, and improve test infrastructure
- Documentation: Add information about how to connect to CrateDB Cloud
- CI: Add GHA workflows to build and publish OCI container images to GHCR
- Tests: Enable code coverage tracking
- Fix SQL DDL files, and add missing columns to make the Models tab load in the UI,
  see GH-17. Thanks, @hammerhead.
