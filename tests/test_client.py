import pytest
from mlflow.entities.evaluation_dataset import EvaluationDataset
from mlflow.exceptions import RestException

pytestmark = pytest.mark.slow


def test_client_dataset_not_found(mlflow_server, mlflow_client, reset_database):
    """
    Request a dataset that does not exist.
    """
    with pytest.raises(RestException) as excinfo:
        mlflow_client.get_dataset("foo")
    assert excinfo.match("RESOURCE_DOES_NOT_EXIST: Evaluation dataset with id 'foo' not found")


def test_client_dataset_basic(mlflow_server, mlflow_client, reset_database):
    """
    Validate basic MLflow dataset creation.
    """

    dataset: EvaluationDataset = mlflow_client.create_dataset("foo")
    assert dataset.name == "foo"

    dataset = mlflow_client.get_dataset(dataset_id=dataset.dataset_id)
    assert dataset.name == "foo"
