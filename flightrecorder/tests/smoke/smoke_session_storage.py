"""Smoke test: create a session and asset through SessionStore, print paths."""

from __future__ import annotations

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.database import connect_metadata_db
from flightrecorder.storage import SessionStore


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        connection = connect_metadata_db(runtime_home)
        store = SessionStore(runtime_home, connection)

        metadata = store.create_session(
            provider="google",
            model="gemini-2.5-pro",
            started_at=datetime.now(timezone.utc),
            slug="smoke-test",
        )

        asset_path = store.store_asset(
            metadata.session_id,
            filename="smoke-photo.jpg",
            data=b"placeholder-image",
        )

        session_path = store.session_path(metadata.session_id)

        print(f"session_id: {metadata.session_id}")
        print(f"session_path: {session_path}")
        print(f"asset_path: {asset_path}")
        print(f"session_exists: {session_path.exists()}")
        print(f"asset_exists: {asset_path.exists()}")

        loaded_meta, loaded_msgs = store.get_session(metadata.session_id)
        print(f"session_id_match: {loaded_meta.session_id == metadata.session_id}")
        print(f"image_count: {loaded_meta.image_count}")
        print(f"message_count: {loaded_meta.message_count}")

        connection.close()

    print("session storage smoke test passed")


if __name__ == "__main__":
    main()
