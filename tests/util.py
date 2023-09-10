# Source: mlflow:tests/integration/utils.py and mlflow:tests/store/tracking/test_file_store.py
import subprocess
from contextlib import contextmanager
from typing import List

import psutil
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


@contextmanager
def process(*args, **kwargs) -> subprocess.Popen:
    """
    Wrapper around `subprocess.Popen` to also terminate child processes after exiting.

    https://gist.github.com/jizhilong/6687481#gistcomment-3057122
    """
    proc = subprocess.Popen(*args, **kwargs)  # noqa: S603
    try:
        yield proc
    finally:
        try:
            children = psutil.Process(proc.pid).children(recursive=True)
        except psutil.NoSuchProcess:
            return
        for child in children:
            child.kill()
        proc.kill()
