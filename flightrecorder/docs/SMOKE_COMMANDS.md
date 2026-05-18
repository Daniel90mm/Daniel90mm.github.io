# Smoke command index

Quick commands for all current smoke scripts. Run from the `flightrecorder/`
directory.

| Script | Command |
|--------|---------|
| `tests/smoke/smoke_schema.py` | `python tests/smoke/smoke_schema.py` |
| `tests/smoke/smoke_hugo_paths.py` | `python tests/smoke/smoke_hugo_paths.py` |
| `tests/smoke/smoke_session_storage.py` | `python tests/smoke/smoke_session_storage.py` |
| `tests/smoke/smoke_runtime_context.py` | `python tests/smoke/smoke_runtime_context.py` |
| `tests/smoke/smoke_cost_logging.py` | `python tests/smoke/smoke_cost_logging.py` |
| `tests/smoke/smoke_backend_health.py` | `.venv/bin/python tests/smoke/smoke_backend_health.py` |
| `tests/smoke/smoke_pricing.py` | `.venv/bin/python tests/smoke/smoke_pricing.py` |

Scripts that don't require FastAPI use the system Python directly.
Scripts that import FastAPI or FastAPI-dependent modules use `.venv/bin/python`.

## One-liner to run all

```sh
for script in tests/smoke/smoke_*.py; do
    case "$script" in
        *smoke_backend_health*|*smoke_pricing*)
            python=".venv/bin/python" ;;
        *)
            python="python" ;;
    esac
    echo "=== $script ==="
    PYTHONPATH=src/backend $python "$script" || exit 1
done
```
