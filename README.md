# MLflow adapter for CrateDB

[![Tests](https://github.com/crate/mlflow-cratedb/actions/workflows/main.yml/badge.svg)](https://github.com/crate/mlflow-cratedb/actions/workflows/main.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/crate/mlflow-cratedb.svg)](https://codecov.io/gh/crate/mlflow-cratedb/)
[![Python versions](https://img.shields.io/pypi/pyversions/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)

[![License](https://img.shields.io/github/license/crate/mlflow-cratedb.svg)](https://github.com/crate/mlflow-cratedb/blob/main/LICENSE)
[![Status](https://img.shields.io/pypi/status/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)
[![PyPI](https://img.shields.io/pypi/v/mlflow-cratedb.svg)](https://pypi.org/project/mlflow-cratedb/)
[![Downloads](https://pepy.tech/badge/mlflow-cratedb/month)](https://pypi.org/project/mlflow-cratedb/)


## About

An adapter for [MLflow] to use [CrateDB] as a storage database for [MLflow
Tracking]. MLflow is an open source platform to manage the whole ML lifecycle,
including experimentation, reproducibility, deployment, and a central model
registry.


## Setup

Install the most recent version of the `mlflow-cratedb` package.
```shell
pip install --upgrade 'mlflow-cratedb[examples]'
```

To verify if the installation worked, you can inspect the version numbers
of the software components you just installed.
```shell
mlflow-cratedb --version
mlflow-cratedb cratedb --version
```


## Documentation

The [MLflow Tracking] subsystem is about recording and querying experiments, across
code, data, config, and results.

The MLflow adapter for CrateDB can be used in different ways. Please refer
to the [handbook], and the documentation about [container usage].

For more general information, see [Machine Learning with CrateDB]
and [examples about MLflow and CrateDB].


## Development

For joining the development, or for making changes to the software, read about
how to [install a development sandbox].


## Project Information

### Resources
- [Source code](https://github.com/crate/mlflow-cratedb)
- [Documentation](https://github.com/crate/mlflow-cratedb/tree/main/docs)
- [Python Package Index (PyPI)](https://pypi.org/project/mlflow-cratedb/)

### Contributions
This library is an open source project, and is [managed on GitHub].
Every kind of contribution, feedback, or patch, is much welcome. [Create an
issue] or submit a patch if you think we should include a new feature, or to
report or fix a bug.

### Development
In order to set up a development environment on your workstation, please head
over to the [development sandbox] documentation. When you see the software
tests succeed, you should be ready to start hacking.

### License
The project is licensed under the terms of the Apache License 2.0, like [MLflow]
and [CrateDB], see [LICENSE].

### Acknowledgements

[Siddharth Murching], [Corey Zumar], [Harutaka Kawamura], [Ben Wilson], and
all other contributors for conceiving and maintaining [MLflow].

[Andreas Nigg] for contributing the [tracking_merlion.py] and [tracking_pycaret.py]
ML experiment programs, using [Merlion] and [PyCaret].

[Andreas Nigg]: https://github.com/andnig
[Ben Wilson]: https://github.com/BenWilson2
[container usage]: https://github.com/crate/mlflow-cratedb/blob/main/docs/container.md
[Corey Zumar]: https://github.com/dbczumar
[CrateDB]: https://github.com/crate/crate
[CrateDB Cloud]: https://console.cratedb.cloud/
[Create an issue]: https://github.com/crate/mlflow-cratedb/issues
[development sandbox]: https://github.com/crate/mlflow-cratedb/blob/main/docs/development.md
[examples about MLflow and CrateDB]: https://github.com/crate/cratedb-examples/tree/main/topic/machine-learning/mlops-mlflow
[handbook]: https://github.com/crate/mlflow-cratedb/blob/main/docs/handbook.md
[Harutaka Kawamura]: https://github.com/harupy
[install a development sandbox]: https://github.com/crate/mlflow-cratedb/blob/main/docs/development.md
[LICENSE]: https://github.com/crate/mlflow-cratedb/blob/main/LICENSE
[Machine Learning with CrateDB]: https://cratedb.com/docs/guide/domain/ml/
[managed on GitHub]: https://github.com/crate/mlflow-cratedb
[Merlion]: https://github.com/salesforce/Merlion
[MLflow]: https://mlflow.org/
[MLflow Tracking]: https://mlflow.org/docs/latest/tracking.html
[PyCaret]: https://pycaret.org/
[Siddharth Murching]: https://github.com/smurching
[tracking_merlion.py]: https://github.com/crate/mlflow-cratedb/blob/main/examples/tracking_merlion.py
[tracking_pycaret.py]: https://github.com/crate/mlflow-cratedb/blob/main/examples/tracking_pycaret.py
