# Backlog

## Iteration +2

### General
- FIXME: `testdrive` is hardcoded here
- Apply database schema at connection time already, using `set search_path`. 
  In this spirit, tables do not need to be addressed everywhere in full-qualified notation.
- Other than the "MLflow Tracking" subsystem, is it sensible to unlock the "MLflow Model
  Registry" subsystem as well, when possible at all? See GH-33.
  https://mlflow.org/docs/latest/model-registry.html
- UX: Provide a Docker Compose file, which bundles the whole trinity
- Project: Move repository to the `crate` organization

### Documentation
- Docs: Add "About MLflow" section to README
- Docs: Add "What's inside" section to README
- Docs: Demonstrate the "Container Use" with CrateDB Cloud instead of Docker container running locally
- Docs: Demonstrate use of `--backend=databricks`
- Docs: Run an MLflow project from the given URI, using `mlflow run`
- Docs: Demonstrate the "automatic logging" feature
  https://mlflow.org/docs/latest/tracking.html#automatic-logging

## Iteration +3
- Examples: Add more examples, eventually using different ML libraries
- Docs: Explore `mlflow experiments search`
- UX: Set up Conda feedstock repository, corresponding to the upstream one
  https://github.com/conda-forge/mlflow-feedstock
- According to @andnig, looking into MLflow, specifically using Ray, makes sense.
  - https://github.com/ray-project/ray/blob/f3c86d17/doc/source/ray-air/deployment.rst#L12
  - https://github.com/ray-project/ray/blob/f3c86d17/doc/source/tune/tutorials/tune_get_data_in_and_out.md?plain=1#L243
  - https://github.com/ray-project/ray/blob/f3c86d17/doc/source/tune/api/logging.rst#L50
  - https://github.com/ray-project/ray/blob/f3c86d17/doc/source/ray-core/_examples/datasets_train/datasets_train.py#L32
  - https://github.com/ray-project/ray/blob/f3c86d17/doc/source/train/user-guides/experiment-tracking.rst#L196
  - https://github.com/ray-project/ray/blob/f3c86d17/python/ray/air/tests/test_integration_mlflow.py#L253

## Iteration +4
- UX: CLI shortcut for `ddl/drop.sql`


## Done
- Use or provide wheel packages for `hashids` and `vasuki`
- Add `versioningit`
- Add example `tracking_merlion.py`
- Integrate tutorial from `cratedb-examples`
- Add GHA recipe to build and ship OCI image
- CI: Do not build OCI images on _each_ PR in the long run, it costs too many
  resources. Instead, document how to run OCI builds on demand on specific
  branches, when it is needed to ship images for testing purposes.
- Documentation: Write a few words about schema/table structure:
  Data tables are in `doc`, while MLflow tables are in `mlflow`.
- Documentation: Write a few words about standalone programs, and the need to import `mlflow_cratedb` there,
  see, for example, tracking_dummy.py#L53-L55.
  Alternatively, find an "autoload" solution for Python?
- Code: Refactor / break out the generic SQLALchemy polyfill patches into `cratedb-toolkit`
- Code: Refactor SQLALchemy polyfills and patches into `sqlalchemy-cratedb`
