import sys

from huey.bin.huey_consumer import consumer_main

if __name__ == "__main__":  # pragma: no cover
    # MacOS on 3.8+ and Linux on 3.14+ need to explicitly specify forking.
    if (sys.platform == "darwin" and sys.version_info >= (3, 8)) or (
        sys.platform.startswith("linux") and sys.version_info >= (3, 14)
    ):
        import multiprocessing

        try:
            multiprocessing.set_start_method("fork")
        except (RuntimeError, ValueError):
            pass
    consumer_main()
