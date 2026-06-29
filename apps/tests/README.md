# apps/tests - Playwright (Python) E2E & API suite

The end-to-end test suite for the Todo app, written with Playwright and `pytest`. UI
tests drive a real browser through a **Page Object Model**; API tests hit the REST
endpoints directly and validate every response against a **JSON Schema**.

For the cross-cutting picture (Docker pipeline, CI, Allure), see the
[root README](../../README.md).

## Layout

```
apps/tests/
  config.py                  # BASE_URL / API_URL read from the environment
  conftest.py                # root fixtures: base_url, api_url, api_context, todo_page, …
  pytest.ini                 # markers + trace/screenshot/video on failure
  requirements.txt           # playwright, pytest-playwright, jsonschema, allure-pytest
  pages/
    base_page.py             # shared Page Object helpers
    todo_page.py             # TodoPage - locators, actions, and assertions
  schemas/
    todo_schemas.py          # JSON Schemas: Todo, Todo[], health, 400/404 errors
  tests/
    api/                     # REST contract tests (Playwright APIRequestContext)
      test_health.py
      test_schema_validation.py
      test_todos_crud.py
      test_todos_error_cases.py
      test_todos_validation.py
    ui/                      # browser-driven flows (through TodoPage)
      test_create_todo.py
      test_validation.py
      test_edge_cases.py
      test_complete_todo.py
      test_delete_todo.py
      test_ordering.py
      test_ui_states.py
```

## Principles

- **Page Object Model.** UI tests never touch raw locators. `pages/todo_page.py` exposes
  semantic locators (by role, label, and text), high-level actions (`add_todo`, `toggle`,
  `delete`, `click_retry`), and assertions (`expect_completed`, `expect_empty_state`,
  `expect_error_state`, …). Tests read as behavior.
- **JSON-Schema validation.** `schemas/todo_schemas.py` is the JSON-Schema referee. Every
  successful API response is validated against it; error responses are validated against
  the `400`/`404` shapes. The schemas mirror the shared API contract.
- **Data isolation.** Each test creates and cleans its own data through the API using
  unique title suffixes. Tests never depend on the seeded demo todos and can run in any
  order.
- **Web-first assertions.** No `time.sleep`/hard waits - Playwright's auto-waiting
  assertions only.
- **Debuggable failures.** Trace, screenshot, and video are retained only on failure
  (see `pytest.ini`) and surface in the Allure report.

## Coverage

**36 tests** - 22 API + 14 UI - covering every UI flow and every endpoint × status code:

- **UI:** add (success, blank, whitespace, trim, 255-char, duplicates), toggle
  complete/uncomplete, completed persistence after reload, delete, newest-first ordering,
  empty state, error state, and retry recovery.
- **API:** health; list (plain array, ordering, schema); create (`201`, `400` ×3,
  default `completed=false`); retrieve (`200`/`404`); PATCH and PUT (`200`/`400`/`404`);
  delete (`204`/`404`) - each success validated against the JSON Schema.

> Known gap: the brief `role="status"` loading spinner is too short-lived to assert
> deterministically without injecting an artificial delay (which would add flakiness).
> The locator exists in the Page Object for when a delay-injection hook is added.

## Running locally

The suite needs a running server. The simplest target is the container
(`docker compose up` from the repo root) or the local dev server on `:8000`.

```bash
cd apps/tests

# first time: create an isolated venv and install
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m playwright install chromium

# run against http://localhost:8000 (defaults)
.venv/Scripts/python.exe -m pytest

# or point at another host
BASE_URL=http://localhost:8000 API_URL=http://localhost:8000/api \
  .venv/Scripts/python.exe -m pytest

# only one layer
.venv/Scripts/python.exe -m pytest -m ui
.venv/Scripts/python.exe -m pytest -m api
```

On macOS/Linux use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

### Configuration

| Variable   | Default                        | Purpose                         |
|------------|--------------------------------|---------------------------------|
| `BASE_URL` | `http://localhost:8000`        | UI origin the browser navigates |
| `API_URL`  | `http://localhost:8000/api`    | REST API root for API tests     |

Results are written for Allure via `allure-pytest`, with `ui` / `api` markers surfaced as
report labels.
