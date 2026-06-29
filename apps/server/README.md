# apps/server - Django + DRF API

The backend for the Todo app: a Django project exposing a small REST API through Django
REST Framework. It also serves the built React SPA same-origin via WhiteNoise, so in the
container a single origin (`:8000`) hosts both the UI and the API.

For the cross-cutting picture (Docker pipeline, CI, Allure), see the
[root README](../../README.md).

## Architecture

The code is organised in thin, single-responsibility layers rather than fat views:

```
config/
  settings.py        # env-driven configuration, logging, DRF + WhiteNoise wiring
  urls.py            # /api/ router include + health endpoint
  wsgi.py / asgi.py  # production gateways (gunicorn serves config.wsgi:application)
todos/
  models.py          # the Todo model (title, completed, created_at, updated_at)
  serializers.py     # DRF serialization + validation (single validation point)
  selectors.py       # read layer  - get_todo_list, get_todo_by_pk
  services.py        # write layer - create_todo, update_todo, delete_todo
  exceptions.py      # custom DRF exception handler (logs, delegates to default)
  views.py           # thin ViewSet delegating to selectors/services
  urls.py            # DRF router registration
  admin.py           # Django admin registration
  management/commands/seed_todos.py   # seeds N demo todos (default 10, clears first)
  migrations/
  tests/
    unit/            # models, serializers, selectors, services, exceptions, settings
    integration/     # full request/response through DRF + the seed command
    factories.py     # factory_boy TodoFactory
```

- **Views stay thin.** `get_queryset` calls a selector; `perform_create/update/destroy`
  call services. Business logic lives in `services.py` / `selectors.py`, not in HTTP
  handlers.
- **One validation point.** The serializer disables DRF's implicit blank-stripping
  (`trim_whitespace=False`) so `validate_title` is the single explicit place that rejects
  blank/whitespace-only titles.
- **Consistent errors.** `exceptions.py` registers a custom handler that logs the failure
  and delegates to DRF's default renderer, keeping the contract's error shapes intact.

## API

| Method | Path                | Success                          | Errors        |
|--------|---------------------|----------------------------------|---------------|
| GET    | `/api/health/`      | `200 {"status":"ok"}`            | -             |
| GET    | `/api/todos/`       | `200 Todo[]` (plain array, ordered `-created_at,-id`) | - |
| POST   | `/api/todos/`       | `201 Todo`                       | `400`         |
| GET    | `/api/todos/{id}/`  | `200 Todo`                       | `404`         |
| PATCH  | `/api/todos/{id}/`  | `200 Todo`                       | `400`, `404`  |
| PUT    | `/api/todos/{id}/`  | `200 Todo`                       | `400`, `404`  |
| DELETE | `/api/todos/{id}/`  | `204`                            | `404`         |

The list endpoint returns a **plain array** (no pagination wrapper) by deliberate
contract choice.

## Local development

A virtual environment lives at `apps/server/.venv`. On this machine the system Python is
unavailable, so always use the venv interpreter. Commands below use the Windows path;
on macOS/Linux use `.venv/bin/python`.

```bash
cd apps/server

# install (first time)
.venv/Scripts/python.exe -m pip install -r requirements.txt

# database
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py seed_todos --count 10

# run the API at http://localhost:8000
.venv/Scripts/python.exe manage.py runserver
```

### Configuration (environment variables)

| Variable                 | Default              | Purpose                            |
|--------------------------|----------------------|------------------------------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings`    | settings module                    |
| `DEBUG`                  | `0` in the image     | Django debug mode                  |
| `ALLOWED_HOSTS`          | `*` in the image     | comma-separated allowed hosts      |
| `DB_PATH`                | project SQLite file  | SQLite database location           |

## Tests & coverage

The suite is split into `unit` and `integration` markers and enforces **100% coverage**.

```bash
cd apps/server

# run everything (coverage is configured in pytest.ini + pyproject.toml)
.venv/Scripts/python.exe -m pytest

# only one layer
.venv/Scripts/python.exe -m pytest -m unit
.venv/Scripts/python.exe -m pytest -m integration
```

- **70 tests** - 51 unit + 19 integration.
- Coverage is measured over `config` + `todos` (see `[tool.coverage]` in
  `pyproject.toml`); `fail_under = 100` makes the run fail below 100%.
- Omitted from coverage (with rationale in `pyproject.toml`): `manage.py`, `wsgi.py`,
  `asgi.py`, `migrations/`, and the tests themselves.
- Test data is built with `factory_boy` (`tests/factories.py`).
- Results are written for Allure via `allure-pytest`.

## Linting & formatting

```bash
cd apps/server
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m black --check .
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

`ruff` and `black` are configured in `pyproject.toml` (line length 88, migrations and
`.venv` excluded).
