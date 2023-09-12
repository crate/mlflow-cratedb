# Backlog

## Iteration +2
- Bug: Fix SQL DDL files, see https://github.com/crate-workbench/mlflow-cratedb/issues/17
- Other than the "MLflow Tracking" subsystem, is it sensible to unlock the "MLflow Model
  Registry" subsystem as well, when possible at all?
- https://mlflow.org/docs/latest/model-registry.html
- Code: Refactor / break out the generic SQLALchemy polyfill patches into `crate-python` elegantly
- Docs: Demonstrate the "Container Use" with CrateDB Cloud instead of Docker container running locally
- Docs: Demonstrate use of `--backend=databricks`
- Docs: Run an MLflow project from the given URI, using `mlflow run`
- Docs: Demonstrate the "automatic logging" feature
  https://mlflow.org/docs/latest/tracking.html#automatic-logging
- UX: Provide a Docker Compose file, which bundles the whole trinity
- Project: Move repository to the `crate` organization
- Project: Release 0.2

## Iteration +3
- Examples: Add more examples, eventually using different ML libraries
- Docs: Explore `mlflow experiments search`
- UX: Set up Conda feedstock repository, corresponding to the upstream one
  https://github.com/conda-forge/mlflow-feedstock

## Iteration +4
- UX: CLI shortcut for `ddl/drop.sql`
- CI: Do not build OCI images on _each_ PR in the long run, it costs too many
  resources. Instead, document how to run OCI builds on demand on specific
  branches, when it is needed to ship images for testing purposes.


## Done
- Use or provide wheel packages for `hashids` and `vasuki`
- Add `versioningit`
- Add example `tracking_merlion.py`
- Integrate tutorial from `cratedb-examples`
- Add GHA recipe to build and ship OCI image
