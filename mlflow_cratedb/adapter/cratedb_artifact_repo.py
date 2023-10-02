import datetime as dt
import os
import posixpath
from functools import lru_cache

from mlflow.entities import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository, verify_artifact_path
from mlflow.store.artifact.artifact_repository_registry import _artifact_repository_registry
from mlflow.store.artifact.http_artifact_repo import HttpArtifactRepository
from mlflow.tracking._tracking_service.utils import _get_default_host_creds

from mlflow_cratedb.contrib.object_store import CrateDBObjectStore, decode_sqlalchemy_url

_MAX_CACHE_SECONDS = 300


def _get_utcnow_timestamp():
    return dt.datetime.utcnow().timestamp()


@lru_cache(maxsize=64)
def _cached_get_cratedb_client(url, timestamp):  # pylint: disable=unused-argument
    """
    A cached `CrateDBObjectStore` client instance.

    Caching is important so that there will be a dedicated client instance per
    endpoint URL/bucket. Otherwise, a new client instance, with a corresponding
    database connection, would be created on each operation.

    Similar to the S3 client wrapper, in order to manage expired/stale
    connections well, expire the connection regularly by using the
    `timestamp` parameter to invalidate the function cache.
    """
    store = CrateDBObjectStore(url=url)
    store.connect()
    return store


def _get_cratedb_client(url):
    # Invalidate cache every `_MAX_CACHE_SECONDS`.
    timestamp = int(_get_utcnow_timestamp() / _MAX_CACHE_SECONDS)

    return _cached_get_cratedb_client(url, timestamp)


class CrateDBArtifactRepository(ArtifactRepository):
    """
    Stores artifacts into a CrateDB object store.

    crate://crate@localhost:4200/bucket-one?schema=testdrive
    """

    ROOT_PATH = ""

    def __init__(self, artifact_uri):
        super().__init__(artifact_uri)
        # Decode for verification purposes, in order to fail early.
        decode_sqlalchemy_url(artifact_uri)

    def _get_cratedb_client(self):
        return _get_cratedb_client(url=self.artifact_uri)

    @property
    def _host_creds(self):
        return _get_default_host_creds(self.artifact_uri)

    def log_artifact(self, local_file, artifact_path=None):
        verify_artifact_path(artifact_path)

        dest_path = self.ROOT_PATH
        if artifact_path:
            dest_path = posixpath.join(self.ROOT_PATH, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))
        with open(local_file, "rb") as f:
            self._get_cratedb_client().upload(dest_path, f.read())

    def log_artifacts(self, local_dir, artifact_path=None):
        HttpArtifactRepository.log_artifacts(self, local_dir, artifact_path=artifact_path)

    def list_artifacts(self, path=None):
        # CrateDBObjectStore.list() already returns tuples of `(path, is_dir, size)`,
        # so the convergence to MLflow's `FileInfo` objects is straight-forward.
        infos = []
        for entry in self._get_cratedb_client().list(path):
            infos.append(FileInfo(*entry))
        return sorted(infos, key=lambda f: f.path)

    def _download_file(self, remote_file_path, local_path):
        payload = self._get_cratedb_client().download(remote_file_path)
        with open(local_path, "wb") as f:
            f.write(payload)

    def delete_artifacts(self, artifact_path=None):
        self._get_cratedb_client().delete(artifact_path)


_artifact_repository_registry.register("crate", CrateDBArtifactRepository)
