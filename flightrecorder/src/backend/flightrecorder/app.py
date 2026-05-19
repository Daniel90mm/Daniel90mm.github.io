"""FastAPI application factory."""

from pathlib import Path
from typing import Any

from flightrecorder.config import AppConfig
from flightrecorder.runtime import RuntimeContext, build_runtime_context

_FRONTEND_DIR: Path | None = None


def _resolve_frontend_dir() -> Path:
    """Resolve the frontend directory relative to this module."""
    global _FRONTEND_DIR
    if _FRONTEND_DIR is None:
        package_dir = Path(__file__).resolve().parent
        _FRONTEND_DIR = package_dir.parent.parent / "frontend"
    return _FRONTEND_DIR


def create_app(
    config: AppConfig | None = None,
    runtime: RuntimeContext | None = None,
) -> Any:
    """Create the backend ASGI app.

    FastAPI is imported lazily so the standard-library backend core can be
    tested before Termux dependency verification is complete.
    """

    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import FileResponse
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI is not installed. Install backend dependencies before "
            "starting the ASGI app."
        ) from exc

    resolved_runtime = runtime or build_runtime_context(config)
    app = FastAPI(title="flightrecorder", version="0.1.0")
    app.state.runtime = resolved_runtime

    from flightrecorder.api import router as api_router

    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    frontend_dir = _resolve_frontend_dir()
    index_html = frontend_dir / "index.html"

    if index_html.is_file():
        @app.get("/")
        async def serve_frontend() -> FileResponse:
            return FileResponse(index_html, media_type="text/html")

        @app.get("/assets/{asset_path:path}")
        async def serve_frontend_asset(asset_path: str) -> FileResponse:
            path = (frontend_dir / asset_path).resolve()
            if asset_path == "index.html" or not path.is_file():
                raise HTTPException(status_code=404, detail="Asset not found")
            if frontend_dir.resolve() not in path.parents:
                raise HTTPException(status_code=404, detail="Asset not found")
            return FileResponse(path)

    return app
