"""FastAPI application factory."""

from typing import Any

from flightrecorder.config import AppConfig
from flightrecorder.runtime import RuntimeContext, build_runtime_context


def create_app(
    config: AppConfig | None = None,
    runtime: RuntimeContext | None = None,
) -> Any:
    """Create the backend ASGI app.

    FastAPI is imported lazily so the standard-library backend core can be
    tested before Termux dependency verification is complete.
    """

    try:
        from fastapi import FastAPI
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

    return app
