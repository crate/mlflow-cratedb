import os
import tarfile
from unittest import mock

import pytest
from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository

from mlflow_cratedb.adapter.cratedb_artifact_repo import CrateDBArtifactRepository

REPOSITORY_URI = "crate://crate@localhost:4200/bucket-one?schema=testdrive"


@pytest.fixture
def cratedb_artifact_repo():
    repo = CrateDBArtifactRepository(REPOSITORY_URI)
    repo._get_cratedb_client().reset_fs()
    return repo


@pytest.fixture
def mocked_connect():
    with mock.patch("mlflow_cratedb.contrib.object_store.CrateDBObjectStore.connect"):
        yield


@pytest.mark.parametrize("scheme", ["crate"])
def test_artifact_uri_factory_valid_http(scheme, mocked_connect):
    repo = get_artifact_repository(f"{scheme}://example.org/bucket-foo")
    assert isinstance(repo, CrateDBArtifactRepository)

    client = repo._get_cratedb_client()
    assert client.http_url == "http://example.org"
    assert client.bucket_name == "bucket-foo"


@pytest.mark.parametrize("scheme", ["crate"])
def test_artifact_uri_factory_valid_https(scheme, mocked_connect):
    repo = get_artifact_repository(f"{scheme}://example.org/bucket-foo?ssl=true")
    assert isinstance(repo, CrateDBArtifactRepository)

    client = repo._get_cratedb_client()
    assert client.http_url == "https://example.org/"
    assert client.bucket_name == "bucket-foo"


def test_artifact_uri_factory_invalid_1():
    with pytest.raises(ValueError) as ex:
        get_artifact_repository("crate://example.org")
    assert ex.match("Bucket name missing in CrateDB artifact storage URI")


def test_artifact_uri_factory_invalid_2():
    with pytest.raises(ValueError) as ex:
        CrateDBArtifactRepository("http://example.org")
    assert ex.match("Not a CrateDB artifact storage URI")


def test_log_and_download_file_basic(cratedb_artifact_repo, tmp_path):
    repo = cratedb_artifact_repo

    file_name = "test.txt"
    file_path = os.path.join(tmp_path, file_name)
    file_text = "Hello world!"

    with open(file_path, "w") as f:
        f.write(file_text)

    cratedb_artifact_repo.log_artifact(file_path)
    downloaded_text = open(repo.download_artifacts(file_name)).read()
    assert downloaded_text == file_text


def test_log_and_download_directory(cratedb_artifact_repo, tmp_path):
    repo = cratedb_artifact_repo

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "b.txt"), "w") as f:
        f.write("B")
    with open(os.path.join(nested_path, "c.txt"), "w") as f:
        f.write("C")

    repo.log_artifacts(subdir_path)

    # Download individual files and verify correctness of their contents
    downloaded_file_a_text = open(repo.download_artifacts("a.txt")).read()
    assert downloaded_file_a_text == "A"
    downloaded_file_b_text = open(repo.download_artifacts("b.txt")).read()
    assert downloaded_file_b_text == "B"
    downloaded_file_c_text = open(repo.download_artifacts("nested/c.txt")).read()
    assert downloaded_file_c_text == "C"

    # Download the nested directory and verify correctness of its contents
    downloaded_dir = repo.download_artifacts("nested")
    assert os.path.basename(downloaded_dir) == "nested"
    text = open(os.path.join(downloaded_dir, "c.txt")).read()
    assert text == "C"

    # Download the root directory and verify correctness of its contents
    downloaded_dir = repo.download_artifacts("")
    dir_contents = os.listdir(downloaded_dir)
    assert "nested" in dir_contents
    assert os.path.isdir(os.path.join(downloaded_dir, "nested"))
    assert "a.txt" in dir_contents
    assert "b.txt" in dir_contents


@pytest.mark.skip(reason="noway")
def test_log_and_download_two_items_with_same_content(cratedb_artifact_repo, tmp_path):
    """
    Because CrateDB stores BLOB items indexed by content digest / hash value,
    it needs special handling, otherwise things go south.
    This test case verifies that multiple items of the same content can exist.
    """

    repo = cratedb_artifact_repo

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.one.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "a.two.txt"), "w") as f:
        f.write("A")

    # Add two items, with the same content.
    repo.log_artifacts(subdir_path)

    # Delete one of the items.
    repo.delete_artifacts("a.one.txt")

    # Verify that the other item is still present.
    downloaded_dir = repo.download_artifacts("")
    dir_contents = os.listdir(downloaded_dir)
    assert "a.two.txt" in dir_contents

    a_two_payload = open(repo.download_artifacts("a.two.txt")).read()
    assert a_two_payload == "A"


def test_log_and_list_directory(cratedb_artifact_repo, tmp_path):
    repo = cratedb_artifact_repo

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "b.txt"), "w") as f:
        f.write("BB")
    with open(os.path.join(nested_path, "c.txt"), "w") as f:
        f.write("C")

    repo.log_artifacts(subdir_path)

    root_artifacts_listing = sorted([(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts()])
    assert root_artifacts_listing == [
        ("a.txt", False, 1),
        ("b.txt", False, 2),
        ("nested", True, None),
    ]

    nested_artifacts_listing = sorted([(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts("nested")])
    assert nested_artifacts_listing == [("nested/c.txt", False, 1)]


def test_delete_all_artifacts(cratedb_artifact_repo, tmp_path):
    repo = cratedb_artifact_repo

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    path_a = os.path.join(subdir_path, "a.txt")
    path_b = os.path.join(subdir_path, "b.tar.gz")
    path_c = os.path.join(nested_path, "c.csv")

    with open(path_a, "w") as f:
        f.write("A")
    with tarfile.open(path_b, "w:gz") as f:
        f.add(path_a)
    with open(path_c, "w") as f:
        f.write("col1,col2\n1,3\n2,4\n")

    repo.log_artifacts(subdir_path)

    # confirm that artifacts are present
    artifact_file_names = [obj.path for obj in repo.list_artifacts()]
    assert "a.txt" in artifact_file_names
    assert "b.tar.gz" in artifact_file_names
    assert "nested" in artifact_file_names

    repo.delete_artifacts()
    tmpdir_objects = repo.list_artifacts()
    assert not tmpdir_objects


def test_delete_single_artifact(cratedb_artifact_repo, tmp_path):
    repo = cratedb_artifact_repo

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "b.txt"), "w") as f:
        f.write("BB")
    with open(os.path.join(nested_path, "c.txt"), "w") as f:
        f.write("C")

    repo.log_artifacts(subdir_path)

    root_artifacts_listing = sorted([(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts()])
    assert root_artifacts_listing == [
        ("a.txt", False, 1),
        ("b.txt", False, 2),
        ("nested", True, None),
    ]

    repo.delete_artifacts("b.txt")

    root_artifacts_listing = sorted([(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts()])
    assert root_artifacts_listing == [
        ("a.txt", False, 1),
        ("nested", True, None),
    ]
