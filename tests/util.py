# Source: mlflow:tests/integration/utils.py and mlflow:tests/store/tracking/test_file_store.py
from typing import List

from click.testing import CliRunner
from mlflow.entities import DatasetInput


def invoke_cli_runner(*args, **kwargs):
    """
    Helper method to invoke the CliRunner while asserting that the exit code is actually 0.
    """

    res = CliRunner().invoke(*args, **kwargs)
    assert res.exit_code == 0, f"Got non-zero exit code {res.exit_code}. Output is: {res.output}"
    return res


def assert_dataset_inputs_equal(inputs1: List[DatasetInput], inputs2: List[DatasetInput]):
    inputs1 = sorted(inputs1, key=lambda inp: (inp.dataset.name, inp.dataset.digest))
    inputs2 = sorted(inputs2, key=lambda inp: (inp.dataset.name, inp.dataset.digest))
    assert len(inputs1) == len(inputs2)
    for idx, inp1 in enumerate(inputs1):
        inp2 = inputs2[idx]
        assert dict(inp1.dataset) == dict(inp2.dataset)
        tags1 = sorted(inp1.tags, key=lambda tag: tag.key)
        tags2 = sorted(inp2.tags, key=lambda tag: tag.key)
        for idx, tag1 in enumerate(tags1):
            tag2 = tags2[idx]
            assert tag1.key == tag1.key
            assert tag1.value == tag2.value
