# MLflow adapter for CrateDB

[![Tests](https://github.com/crate/mlflow-cratedb/actions/workflows/main.yml/badge.svg)](https://github.com/crate/mlflow-cratedb/actions/workflows/main.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/crate/mlflow-cratedb.svg)](https://codecov.io/gh/crate/mlflow-cratedb/)
[![Python versions](https://img.shields.io/pypi/pyversions/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)

[![License](https://img.shields.io/github/license/crate/mlflow-cratedb.svg)](https://github.com/crate/mlflow-cratedb/blob/main/LICENSE)
[![Status](https://img.shields.io/pypi/status/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)
[![PyPI](https://img.shields.io/pypi/v/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)
[![Downloads](https://pepy.tech/badge/mlflow-cratedb/month)](https://pypi.org/project/mlflow-cratedb/)

» [Documentation]
| [Changelog]
| [PyPI]
| [Issues]
| [Source code]
| [License]
| [CrateDB]
| [Community Forum]

## About

[MLflow] is an open source AI engineering platform for managing the whole
ML lifecycle for agents, LLMs, and ML models, including experimentation,
reproducibility, and deployment.

[CrateDB] is a distributed and scalable SQL database for storing and analyzing
massive amounts of data in near real-time, even with complex queries. 
CrateDB is based on Lucene and Elasticsearch, but [compatible with PostgreSQL].

## Details

MLflow enables teams of all sizes to debug, evaluate, monitor, and optimize
production-quality AI applications while controlling costs and managing access
to models and data.

The MLflow adapter for CrateDB is an adapter for [MLflow] to use [CrateDB]
as a storage database for its various subsystems.

## Features

The [MLflow Experiment Tracking] subsystem is an API and UI for logging and
recording parameters, code versions, metrics, and output files when running
your machine learning code, and for later visualizing the results by querying
experiments across code, data, and config.

The [MLflow Model Registry] is a centralized model store, set of APIs and a UI
designed to collaboratively manage the full lifecycle of a machine learning model,
including lineage, versioning, aliasing, metadata tagging, and annotation support. 

The [MLflow Dataset Tracking] module is a comprehensive solution for dataset
management throughout the ML model development workflow. It enables you to track,
version, and manage datasets used in training, validation, and evaluation,
providing complete lineage from raw data to model predictions.

## What's inside

The source code of the `mlflow-cratedb` package, which implements
the [MLflow adapter for CrateDB]. It works with both [CrateDB] and
[CrateDB Cloud].

The source code is effectively a few monkey patches that amalgamate
MLflow with the necessary changes to support CrateDB. The patches are
curated until the adapter can eventually be upstreamed into MLflow
mainline as another storage database type.

## Documentation

The MLflow adapter for CrateDB can be used in different ways. Please refer
to the [handbook], and the documentation about [container usage].

For more general information, see [Machine Learning with CrateDB]
and [examples about MLflow and CrateDB].

## Status

The software is currently in beta status. We welcome any problem reports
to improve quality and fix bugs.

## Usage

For installation per [PyPI package][PyPI], [OCI image],
and usage information, please visit the [handbook] document.

In order to set up a development environment on your workstation, please head
over to the [development sandbox] documentation. When you see the software
tests succeed, you should be ready to start hacking.

## Project Information

### Resources

- [Source code](https://github.com/crate/mlflow-cratedb)
- [Documentation](https://github.com/crate/mlflow-cratedb/tree/main/docs)
- [Python Package Index (PyPI)](https://pypi.org/project/mlflow-cratedb/)

### Acknowledgements

Kudos to the authors of all the many software components this library is
inheriting from and building upon.

### Contributing

The MLflow adapter for CrateDB is an open-source project, and is
[managed on GitHub]. Feel free to use the adapter as provided or else
modify / extend it as appropriate for your own applications.

Any kind of contribution, feedback, or patch, is much welcome. [Create an
issue] or submit a patch if you think we should include a new feature, or
to report or fix a bug.

### Acknowledgements

[Siddharth Murching], [Corey Zumar], [Harutaka Kawamura], [Ben Wilson], and
all other contributors for conceiving and maintaining [MLflow].

[Andreas Nigg] for contributing the [tracking_merlion.py] and [tracking_pycaret.py]
ML experiment programs, using [Merlion] and [PyCaret].

### License

The project is licensed under the terms of the Apache License 2.0, like [MLflow]
and [CrateDB], see [LICENSE].


[Changelog]: https://github.com/crate/mlflow-cratedb/blob/main/CHANGES.md
[Community Forum]: https://community.cratedb.com/
[Documentation]: https://cratedb.com/docs/guide/integrate/mlflow/
[Issues]: https://github.com/crate/mlflow-cratedb/issues
[License]: https://github.com/crate/mlflow-cratedb/blob/main/LICENSE
[managed on GitHub]: https://github.com/crate/mlflow-cratedb
[PyPI]: https://pypi.org/project/mlflow-cratedb/
[Source code]: https://github.com/crate/mlflow-cratedb

[badge-ci]: https://github.com/crate/mlflow-cratedb/actions/workflows/tests.yml/badge.svg
[badge-coverage]: https://codecov.io/gh/crate/mlflow-cratedb/branch/main/graph/badge.svg
[badge-downloads-per-month]: https://pepy.tech/badge/mlflow-cratedb/month
[badge-license]: https://img.shields.io/github/license/crate/mlflow-cratedb.svg
[badge-package-version]: https://img.shields.io/pypi/v/mlflow-cratedb.svg
[badge-python-versions]: https://img.shields.io/pypi/pyversions/mlflow-cratedb.svg
[badge-release-notes]: https://img.shields.io/github/release/crate/mlflow-cratedb?label=Release+Notes
[badge-status]: https://img.shields.io/pypi/status/mlflow-cratedb.svg
[project-ci]: https://github.com/crate/mlflow-cratedb/actions/workflows/tests.yml
[project-coverage]: https://app.codecov.io/gh/crate/mlflow-cratedb
[project-downloads]: https://pepy.tech/project/mlflow-cratedb/
[project-license]: https://github.com/crate/mlflow-cratedb/blob/main/LICENSE
[project-pypi]: https://pypi.org/project/mlflow-cratedb
[project-release-notes]: https://github.com/crate/mlflow-cratedb/releases

[Andreas Nigg]: https://github.com/andnig
[Ben Wilson]: https://github.com/BenWilson2
[compatible with PostgreSQL]: https://cratedb.com/docs/guide/feature/postgresql-compatibility/
[container usage]: https://github.com/crate/mlflow-cratedb/blob/main/docs/container.md
[Corey Zumar]: https://github.com/dbczumar
[CrateDB]: https://cratedb.com/database
[CrateDB Cloud]: https://cratedb.com/deployment/public-cloud
[Create an issue]: https://github.com/crate/mlflow-cratedb/issues
[development sandbox]: https://github.com/crate/mlflow-cratedb/blob/main/docs/development.md
[examples about MLflow and CrateDB]: https://github.com/crate/cratedb-examples/tree/main/topic/machine-learning/mlflow
[handbook]: https://github.com/crate/mlflow-cratedb/blob/main/docs/handbook.md
[Harutaka Kawamura]: https://github.com/harupy
[issue tracker]: https://github.com/crate/mlflow-cratedb/issues
[LICENSE]: https://github.com/crate/mlflow-cratedb/blob/main/LICENSE
[Machine Learning with CrateDB]: https://cratedb.com/docs/guide/solution/machine-learning/
[managed on GitHub]: https://github.com/crate/mlflow-cratedb
[Merlion]: https://github.com/salesforce/Merlion
[MLflow]: https://mlflow.org/
[MLflow adapter for CrateDB]: https://github.com/crate/mlflow-cratedb
[MLflow Dataset Tracking]: https://mlflow.org/docs/latest/ml/dataset/
[MLflow Experiment Tracking]: https://mlflow.org/docs/latest/ml/tracking/
[MLflow Model Registry]: https://mlflow.org/docs/latest/ml/model-registry/
[OCI image]: https://github.com/crate/mlflow-cratedb/pkgs/container/mlflow-cratedb
[PyCaret]: https://pycaret.org/
[Siddharth Murching]: https://github.com/smurching
[tracking_merlion.py]: https://github.com/crate/mlflow-cratedb/blob/main/examples/tracking_merlion.py
[tracking_pycaret.py]: https://github.com/crate/mlflow-cratedb/blob/main/examples/tracking_pycaret.py
