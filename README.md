# MLflow adapter for CrateDB


## About

An adapter wrapper for [MLflow] to use [CrateDB] as a storage database
for [MLflow Tracking].

[MLflow] is an open source platform to manage the ML lifecycle, including
experimentation, reproducibility, deployment, and a central model registry.

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


## Usage

The MLflow adapter for CrateDB can be used in different ways. Please refer
to the [handbook](./docs/handbook.md) and the documentation about
[container usage](./docs/container.md).


## Development

For joining the development, or for making changes to the software, read about
how to [install a development sandbox](./docs/development.md).


## Project Information

### Resources
- [Source code](https://github.com/crate-workbench/mlflow-cratedb)
- [Documentation](https://github.com/crate-workbench/mlflow-cratedb/tree/main/docs)
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

[Andreas Nigg] for contributing the [tracking_merlion.py](./examples/tracking_merlion.py)
ML experiment program, which is using [Merlion].


[Andreas Nigg]: https://github.com/andnig
[Ben Wilson]: https://github.com/BenWilson2
[Corey Zumar]: https://github.com/dbczumar
[CrateDB]: https://github.com/crate/crate
[CrateDB Cloud]: https://console.cratedb.cloud/
[Create an issue]: https://github.com/crate-workbench/mlflow-cratedb/issues
[development sandbox]: https://github.com/crate-workbench/mlflow-cratedb/blob/main/docs/development.md
[Harutaka Kawamura]: https://github.com/harupy
[LICENSE]: https://github.com/crate-workbench/mlflow-cratedb/blob/main/LICENSE
[managed on GitHub]: https://github.com/crate-workbench/mlflow-cratedb
[Merlion]: https://github.com/salesforce/Merlion
[MLflow]: https://mlflow.org/
[MLflow Tracking]: https://mlflow.org/docs/latest/tracking.html
[Siddharth Murching]: https://github.com/smurching
