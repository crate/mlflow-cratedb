# Changelog


## in progress

## 2023-10-11 0.2.0
- Update to [MLflow 2.7](https://github.com/mlflow/mlflow/releases/tag/v2.7.0)
- Improve `table_exists()` in `example_merlion.py`
- SQLAlchemy: Use server-side `now()` function for "autoincrement" columns
- Use SQLAlchemy patches and polyfills from `cratedb-toolkit`
- Update and improve documentation

## 2023-09-12 0.1.1
- Documentation: Improve "Container Usage" page
- Documentation: Update README with real `pip install` command

## 2023-09-12 0.1.0
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
