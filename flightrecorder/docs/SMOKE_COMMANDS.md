# Smoke command index

Quick commands for all current smoke scripts. Run from the `flightrecorder/`
directory.

| Script | Command |
|--------|---------|
| `tests/smoke/smoke_schema.py` | `python tests/smoke/smoke_schema.py` |
| `tests/smoke/smoke_hugo_build.py` | `python tests/smoke/smoke_hugo_build.py` |
| `tests/smoke/smoke_hugo_internal_links.py` | `python tests/smoke/smoke_hugo_internal_links.py` |
| `tests/smoke/smoke_hugo_paths.py` | `python tests/smoke/smoke_hugo_paths.py` |
| `tests/smoke/smoke_idea_capture.py` | `.venv/bin/python tests/smoke/smoke_idea_capture.py` |
| `tests/smoke/smoke_session_storage.py` | `python tests/smoke/smoke_session_storage.py` |
| `tests/smoke/smoke_runtime_context.py` | `python tests/smoke/smoke_runtime_context.py` |
| `tests/smoke/smoke_cost_logging.py` | `python tests/smoke/smoke_cost_logging.py` |
| `tests/smoke/smoke_budget.py` | `.venv/bin/python tests/smoke/smoke_budget.py` |
| `tests/smoke/smoke_backend_health.py` | `.venv/bin/python tests/smoke/smoke_backend_health.py` |
| `tests/smoke/smoke_imports.py` | `.venv/bin/python tests/smoke/smoke_imports.py` |
| `tests/smoke/smoke_pricing.py` | `.venv/bin/python tests/smoke/smoke_pricing.py` |
| `tests/smoke/smoke_budget_api.py` | `.venv/bin/python tests/smoke/smoke_budget_api.py` |
| `tests/smoke/smoke_prototype_dogfood.py` | `.venv/bin/python tests/smoke/smoke_prototype_dogfood.py` |
| `tests/smoke/smoke_project_documents.py` | `.venv/bin/python tests/smoke/smoke_project_documents.py` |
| `tests/smoke/smoke_documents_git.py` | `.venv/bin/python tests/smoke/smoke_documents_git.py` |
| `tests/smoke/smoke_budget_hard_stop.py` | `.venv/bin/python tests/smoke/smoke_budget_hard_stop.py` |
| `tests/smoke/smoke_provider_call_guard.py` | `.venv/bin/python tests/smoke/smoke_provider_call_guard.py` |
| `tests/smoke/smoke_small_model_tasks.py` | `.venv/bin/python tests/smoke/smoke_small_model_tasks.py` |
| `tests/smoke/smoke_session_api.py` | `.venv/bin/python tests/smoke/smoke_session_api.py` |
| `tests/smoke/smoke_termux_helper.py` | `.venv/bin/python tests/smoke/smoke_termux_helper.py` |
| `tests/smoke/smoke_provider_usage_fixtures.py` | `python tests/smoke/smoke_provider_usage_fixtures.py` |
| `tests/smoke/smoke_adversarial_fixtures.py` | `python tests/smoke/smoke_adversarial_fixtures.py` |
| `tests/smoke/smoke_project_registry_fixture.py` | `python tests/smoke/smoke_project_registry_fixture.py` |
| `tests/smoke/smoke_spaghetti_fixture.py` | `python tests/smoke/smoke_spaghetti_fixture.py` |
| `tests/smoke/smoke_project_document_fixture.py` | `python tests/smoke/smoke_project_document_fixture.py` |
| `tests/smoke/smoke_api_current_state.py` | `.venv/bin/python tests/smoke/smoke_api_current_state.py` |
| `tests/smoke/smoke_docs_navigation.py` | `.venv/bin/python tests/smoke/smoke_docs_navigation.py` |
| `tests/smoke/smoke_handoff_templates.py` | `.venv/bin/python tests/smoke/smoke_handoff_templates.py` |
| `tests/smoke/smoke_project_registry.py` | `.venv/bin/python tests/smoke/smoke_project_registry.py` |
| `tests/smoke/smoke_matchmaker_rejection_fixtures.py` | `python tests/smoke/smoke_matchmaker_rejection_fixtures.py` |
| `tests/smoke/smoke_docs_navigation_consistency.py` | `python tests/smoke/smoke_docs_navigation_consistency.py` |
| `tests/smoke/smoke_pages_workflow.py` | `python tests/smoke/smoke_pages_workflow.py` |
| `tests/smoke/smoke_publisher.py` | `python tests/smoke/smoke_publisher.py` |
| `tests/smoke/smoke_publisher_fixture_dir.py` | `python tests/smoke/smoke_publisher_fixture_dir.py` |
| `tests/smoke/smoke_frontend_static.py` | `python tests/smoke/smoke_frontend_static.py` |
| `tests/smoke/smoke_frontend_sse_parser.py` | `python tests/smoke/smoke_frontend_sse_parser.py` |
| `tests/smoke/smoke_frontend_dogfood.py` | `.venv/bin/python tests/smoke/smoke_frontend_dogfood.py` |
| `tests/smoke/smoke_documents_api.py` | `.venv/bin/python tests/smoke/smoke_documents_api.py` |
| `tests/smoke/smoke_spaghetti_api.py` | `.venv/bin/python tests/smoke/smoke_spaghetti_api.py` |
| `tests/smoke/smoke_example_config.py` | `.venv/bin/python tests/smoke/smoke_example_config.py` |
| `tests/smoke/smoke_dev_prototype_script.py` | `.venv/bin/python tests/smoke/smoke_dev_prototype_script.py` |
| `tests/smoke/smoke_api_calls_api.py` | `.venv/bin/python tests/smoke/smoke_api_calls_api.py` |
| `tests/smoke/smoke_prototype_walkthrough.py` | `.venv/bin/python tests/smoke/smoke_prototype_walkthrough.py` |
| `tests/smoke/smoke_runtime_status_api.py` | `.venv/bin/python tests/smoke/smoke_runtime_status_api.py` |

Scripts that don't require FastAPI use the system Python directly.
Scripts that import FastAPI or FastAPI-dependent modules use `.venv/bin/python`.

## One-liner to run all

```sh
for script in tests/smoke/smoke_*.py; do
    case "$script" in
            *smoke_adversarial_fixtures*|*smoke_api_calls_api*|*smoke_api_current_state*|*smoke_backend_health*|*smoke_budget*|*smoke_budget_api*|*smoke_budget_hard_stop*|*smoke_docs_navigation*|*smoke_documents_api*|*smoke_documents_git*|*smoke_example_config*|*smoke_frontend_dogfood*|*smoke_handoff_templates*|*smoke_idea_capture*|*smoke_imports*|*smoke_pricing*|*smoke_project_document_fixture*|*smoke_project_documents*|*smoke_project_registry*|*smoke_project_registry_fixture*|*smoke_prototype_dogfood*|*smoke_provider_call_guard*|*smoke_provider_usage_fixtures*|*smoke_runtime_status_api*|*smoke_session_api*|*smoke_small_model_tasks*|*smoke_spaghetti_api*|*smoke_spaghetti_fixture*|*smoke_termux_helper*)
            python=".venv/bin/python" ;;
        *)
            python="python" ;;
    esac
    echo "=== $script ==="
    PYTHONPATH=src/backend $python "$script" || exit 1
done
```
