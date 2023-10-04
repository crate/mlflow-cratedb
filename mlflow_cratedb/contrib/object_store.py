"""
## About
Access object store on top of CrateDB's BLOB store from the command-line.

## Usage

For convenient interactive use, define two environment variables.
When not defining `--url` or `CRATEDB_SQLALCHEMY_URL`, the program will
connect to CrateDB at `crate@localhost:4200` by default.

Synopsis::

    # Define the SQLAlchemy URL to your CrateDB instance, including bucket name.
    export CRATEDB_SQLALCHEMY_URL=crate://username:password@cratedb.example.net:4200/bucket?ssl=true

    # Upload an item to the BLOB store.
    python object_store.py upload /path/to/file
    OK

    # Download an item from the BLOB store.
    python object_store.py download /path/to/file

Full command line example, without defining environment variables::

    python object_store.py \
        --url=crate://crate@localhost:4200/testdrive \
        upload /path/to/file

"""
import dataclasses
import logging
import os
import sys
import typing as t
from argparse import ArgumentError, ArgumentParser
from pathlib import Path

import hyperlink
from mlflow import MlflowException

from mlflow_cratedb.contrib.blob_store import CrateDBBlobContainer, truncate

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class ObjectItem:
    key: str
    parent: t.Optional["ObjectItem"] = None
    children: t.List["ObjectItem"] = dataclasses.field(default_factory=list)
    size: t.Optional[int] = None

    @property
    def is_dir(self):
        return len(self.children) > 0


class CrateDBObjectStore:
    """
    An object store on top of CrateDB's BLOB store.
    """

    def __init__(self, url: str):
        self.sqlalchemy_url = url
        self.bucket_name, self.http_url = decode_sqlalchemy_url(self.sqlalchemy_url)

        # BLOB store and path -> id map.
        self.blob = CrateDBBlobContainer(url=self.http_url, name=self.bucket_name)
        self.blob_map: t.Dict[str, str] = {}

        # Filesystem overlay.
        # TODO: Currently still memory-based, needs to be persisted.
        self.root: ObjectItem = None  # type: ignore
        self.index: t.Dict[str, ObjectItem] = {}
        self.reset_fs()

    def reset_fs(self):
        # TODO: Remove after persistent implementation of filesystem overlay.
        self.blob_map = {}
        self.root = ObjectItem(key="")
        self.index = {"": self.root}

    def connect(self):
        self.blob.connect()

    def disconnect(self):
        self.blob.disconnect()

    def upload(self, key: str, payload: t.Union[bytes, bytearray]) -> str:
        """
        Upload an item to the BLOB store.

        - https://cratedb.com/docs/python/en/latest/blobs.html#upload-blobs
        - https://cratedb.com/docs/crate/reference/en/latest/general/blobs.html#uploading
        """
        node = self._object_item(key, mknode=True)

        digest = self.blob.upload(payload)
        self.blob_map[key] = digest
        node.size = len(payload)

        return digest

    def download(self, key: str) -> bytes:
        key = key.rstrip("/")
        try:
            digest = self.blob_map[key]
        except KeyError as ex:
            # TODO: Test failure condition. Use a different exception type.
            raise MlflowException(f"Object not found: {key}") from ex
        return self.blob.download(digest)

    def list(self, key: str):  # noqa: A003
        """
        List all objects matching path prefix.
        """
        # Find filesystem node item.
        key = key or ""
        node = self.index[key]

        # Generate child items.
        entries = []
        for child in node.children:
            name = child.key if not key else f"{key}/{child.key}"
            is_dir = child.is_dir
            file_size = child.size
            entry = (name, is_dir, None if is_dir else file_size)
            entries.append(entry)
        return entries

    def delete(self, key: str):
        """
        Delete all objects matching path prefix.

        Thoughts: A "DELETE ALL" operation could also be implemented by
                  using `select * from "blob"."bucket-one";`.
        """
        for name in self._object_keys(key):
            # Manage filesystem.
            item = self.index[name]
            if item is self.root:
                continue
            del self.index[name]
            if item.parent:
                item.parent.children.remove(item)

            # Remove BLOB item.
            if not item.is_dir:
                digest = self.blob_map[name]
                self.blob.delete(digest)
                del self.blob_map[name]

    def _object_item(self, key, mknode: bool = False) -> ObjectItem:
        if key not in self.index and not mknode:
            raise KeyError(f"ObjectItem does not exist: {key}")

        node: ObjectItem
        if key in self.index:
            node = self.index[key]
        else:
            # Each upload implicitly means `mkdir -p $(dirname $name)`.
            node = self.root
            frags = key.split("/")
            full_name = ""
            for frag in frags:
                item = ObjectItem(key=frag, parent=node)
                node.children.append(item)

                full_name += "/" + frag if full_name else frag
                self.index[full_name] = item

                node = item
        return node

    def _object_keys(self, prefix: str):
        prefix = prefix or ""
        results = []
        for key in self.index:
            if key.startswith(prefix):
                results.append(key)
        return results

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *excs):
        self.disconnect()


def decode_sqlalchemy_url(url):
    parsed = hyperlink.parse(url)

    if parsed.scheme != "crate":
        raise ValueError(f"Not a CrateDB artifact storage URI: {url}")

    if not parsed.path:
        raise ValueError(f"Bucket name missing in CrateDB artifact storage URI: {url}")

    # TODO: More sanitation of bucket name?
    path = "/".join(parsed.path).lstrip("/")
    parsed = parsed.replace(path="")

    # Rewrite dialect name in SQLAlchemy connection string to either http or https,
    # so it can be used as a regular URL.
    if parsed.get("ssl"):
        parsed = parsed.replace(scheme="https").remove("ssl")
    else:
        parsed = parsed.replace(scheme="http")

    return path, str(parsed)


def read_arguments():
    parser = ArgumentParser()
    url = parser.add_argument("-u", "--url", type=str)

    actions = parser.add_subparsers(
        dest="action",
        title="action",
        description="valid subcommands",
        help="additional help",
    )
    upload = actions.add_parser("upload", aliases=["up", "put"])
    download = actions.add_parser("download", aliases=["down", "get"])
    delete = actions.add_parser("delete", aliases=["del", "rm"])

    path = upload.add_argument("path", type=Path)
    upload.add_argument("key", type=str, required=False)
    download.add_argument("key", type=str)
    delete.add_argument("key", type=str)

    parser.set_defaults(url=os.environ.get("CRATEDB_SQLALCHEMY_URL", "crate://crate@localhost:4200/testdrive"))

    args = parser.parse_args()

    if not args.url:
        raise ArgumentError(
            url,
            "URL to database not given or empty. " "Use `--url` or `CRATEDB_SQLALCHEMY_URL` environment variable",
        )

    if not args.action:
        raise ArgumentError(actions, "Action not given: Use one of {upload,download,delete}")

    if args.action == "upload" and not args.path.exists():
        raise ArgumentError(path, f"Path does not exist: {args.path}")

    if args.action in ["download", "delete"] and not args.key:
        raise ArgumentError(path, "Object key not given")

    return args


def main():
    args = read_arguments()
    with CrateDBObjectStore(url=args.url) as store:
        if args.action == "upload":
            payload = args.path.read_bytes()
            key = args.key if args.key else args.path
            store.upload(key, payload)
            print("OK")  # noqa: T201
        elif args.action == "download":
            payload = store.download(args.key)
            sys.stdout.buffer.write(payload)
        elif args.action == "delete":
            store.delete(args.key)
        else:
            raise KeyError(f"Action not implemented: {args.action}")


def example(url: str):
    """
    An example conversation with the object store (upload, download, delete).
    """

    # Define arbitrary content for testing purposes.
    path = "/path/to/file"
    content = "An example payload.".encode("utf-8")

    # Upload and re-download content payload.
    logger.info(f"Uploading: {truncate(content)!r}")
    with CrateDBObjectStore(url=url) as store:
        identifier = store.upload(path, content)
        logger.info(f"Identifier: {identifier}")

        downloaded = store.download(path)
        logger.info(f"Downloaded: {truncate(downloaded)!r}")

        store.delete(path)
        logger.info("Deleted.")


def run_example():
    example(
        url="crate://crate@localhost:4200/testdrive",
    )


def setup_logging(level=logging.INFO):
    """
    What the function name says.
    """
    log_format = "%(asctime)-15s [%(name)-10s] %(levelname)-8s: %(message)s"
    logging.basicConfig(format=log_format, stream=sys.stderr, level=level)


if __name__ == "__main__":
    setup_logging()
    run_example()
    # main()  # noqa: ERA001
