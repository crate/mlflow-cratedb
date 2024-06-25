# Changelog


## in progress

## 2024-06-25 v2.14.1
- Started using more SQLAlchemy patches and polyfills from `sqlalchemy-cratedb`
- Updated to MLflow 2.14.1. See release notes for
  [MLflow 2.14.1](https://github.com/mlflow/mlflow/releases/tag/v2.14.1).

## 2024-06-18 v2.14.0
- Remove patch for SQLAlchemy Inspector's `get_table_names`.
  Use `sqlalchemy-cratedb>=0.37` instead, which includes the patch.
- Update to MLflow 2.14.0. See release notes for
  [MLflow 2.14.0](https://github.com/mlflow/mlflow/releases/tag/v2.14.0).

## 2024-06-11 v2.13.2
- Dependencies: Migrate from `crate[sqlalchemy]` to `sqlalchemy-cratedb`
- Update to MLflow 2.13.2. See release notes for
  [MLflow 2.13.2](https://github.com/mlflow/mlflow/releases/tag/v2.13.2).

## 2024-06-04 v2.13.1
- Update to MLflow 2.13.1. See release notes for
  [MLflow 2.13.1](https://github.com/mlflow/mlflow/releases/tag/v2.13.1).

## 2024-05-21 v2.13.0
- Update to MLflow 2.13.0. See release notes for
  [MLflow 2.13.0](https://github.com/mlflow/mlflow/releases/tag/v2.13.0).

## 2024-05-17 v2.12.2
- Update to MLflow 2.12.2. See release notes for
  [MLflow 2.12.2](https://github.com/mlflow/mlflow/releases/tag/v2.12.2).

## 2024-05-07 v2.12.1
- Update to MLflow 2.12.1. See release notes for
  [MLflow 2.12.1](https://github.com/mlflow/mlflow/releases/tag/v2.12.1).
- Update to PyCaret 3.3.2. See release notes for
  [PyCaret 3.3.1](https://github.com/pycaret/pycaret/releases/tag/3.3.1),
  [PyCaret 3.3.2](https://github.com/pycaret/pycaret/releases/tag/3.3.2).
- Chore: Update to most recent mypy, pyproject-fmt, ruff, and sqlparse
- CI: Run tests on Python 3.10 and 3.11

## 2024-04-10 v2.11.3
- Update to MLflow 2.11.3. See release notes for
  [MLflow 2.11.0](https://github.com/mlflow/mlflow/releases/tag/v2.11.0),
  [MLflow 2.11.1](https://github.com/mlflow/mlflow/releases/tag/v2.11.1),
  [MLflow 2.11.2](https://github.com/mlflow/mlflow/releases/tag/v2.11.2),
  [MLflow 2.11.3](https://github.com/mlflow/mlflow/releases/tag/v2.11.3).
- Fix incompatibility with Python 3.11.9

## 2024-02-13 v2.10.2
- Update to [MLflow 2.10.2](https://github.com/mlflow/mlflow/releases/tag/v2.10.2)

## 2024-01-30 v2.10.0
- Update to [MLflow 2.10.0](https://github.com/mlflow/mlflow/releases/tag/v2.10.0)

## 2024-01-25 v2.9.2
- Update to [MLflow 2.9.2](https://github.com/mlflow/mlflow/releases/tag/v2.9.2)
- Update to Python 3.11 across the board

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
