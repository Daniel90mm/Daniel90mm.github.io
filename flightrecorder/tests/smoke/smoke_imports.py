"""Smoke test: import all backend modules without instantiating provider clients."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))


def main() -> None:
    import flightrecorder.app
    import flightrecorder.config
    import flightrecorder.costs
    import flightrecorder.database
    import flightrecorder.documents
    import flightrecorder.providers
    import flightrecorder.runtime
    import flightrecorder.schema
    import flightrecorder.serializers
    import flightrecorder.storage

    print("app ok")
    print("config ok")
    print("costs ok")
    print("database ok")
    print("documents ok")
    print("providers ok")
    print("runtime ok")
    print("schema ok")
    print("serializers ok")
    print("storage ok")
    print("package import smoke test passed")


if __name__ == "__main__":
    main()
