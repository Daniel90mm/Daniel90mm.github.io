# Smoke command index

Quick commands for all current smoke scripts. Run from the `flightrecorder/`
directory.

| Script | Command |
|--------|---------|
| `tests/smoke/smoke_schema.py` | `python tests/smoke/smoke_schema.py` |
| `tests/smoke/smoke_hugo_paths.py` | `python tests/smoke/smoke_hugo_paths.py` |
| `tests/smoke/smoke_idea_capture.py` | `.venv/bin/python tests/smoke/smoke_idea_capture.py` |
| `tests/smoke/smoke_session_storage.py` | `python tests/smoke/smoke_session_storage.py` |
| `tests/smoke/smoke_runtime_context.py` | `python tests/smoke/smoke_runtime_context.py` |
| `tests/smoke/smoke_cost_logging.py` | `python tests/smoke/smoke_cost_logging.py` |
| `tests/smoke/smoke_budget.py` | `.venv/bin/python tests/smoke/smoke_budget.py` |
| `tests/smoke/smoke_backend_health.py` | `.venv/bin/python tests/smoke/smoke_backend_health.py` |
| `tests/smoke/smoke_imports.py` | `.venv/bin/python tests/smoke/smoke_imports.py` |
| `tests/smoke/smoke_pricing.py` | `.venv/bin/python tests/smoke/smoke_pricing.py` |
| `tests/smoke/smoke_project_documents.py` | `.venv/bin/python tests/smoke/smoke_project_documents.py` |
| `tests/smoke/smoke_session_api.py` | `.venv/bin/python tests/smoke/smoke_session_api.py` |
| `tests/smoke/smoke_termux_helper.py` | `.venv/bin/python tests/smoke/smoke_termux_helper.py` |

Scripts that don't require FastAPI use the system Python directly.
Scripts that import FastAPI or FastAPI-dependent modules use `.venv/bin/python`.

## One-liner to run all

```sh
for script in tests/smoke/smoke_*.py; do
    case "$script" in
        *smoke_backend_health*|*smoke_budget*|*smoke_idea_capture*|*smoke_imports*|*smoke_pricing*|*smoke_project_documents*|*smoke_session_api*|*smoke_termux_helper*)
            python=".venv/bin/python" ;;
        *)
            python="python" ;;
    esac
    echo "=== $script ==="
    PYTHONPATH=src/backend $python "$script" || exit 1
done
```
