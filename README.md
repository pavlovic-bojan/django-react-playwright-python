# Todo App - Full-Stack Monorepo with End-to-End Test Framework

A small Todo application built as a **reference architecture** for a complete,
thoroughly tested full-stack project. It pairs a Django + DRF backend, a React +
TypeScript frontend, and a Playwright (Python) end-to-end suite, then ships all three in
a **single Docker image** that runs the entire test pipeline and publishes an **Allure**
report.

The point of the project is not the Todo domain - it is the surrounding engineering:
end-to-end type safety, a single source-of-truth API contract, 100% unit/component
coverage on both client and server, a Page-Object E2E suite with JSON-Schema validation,
and one reproducible command that builds, migrates, seeds, tests, and reports.

---

## Architecture at a glance

```
                       ┌──────────────────────────────────────────┐
   Browser  ──────────▶│  Django (gunicorn) on :8000              │
                       │   ├─ /          → React SPA (WhiteNoise)  │
                       │   └─ /api/      → DRF REST API            │
                       └──────────────────────────────────────────┘
                                          ▲
   Playwright (Python)  ──── UI + API ────┘   same-origin in the image

   apps/client  ──build──▶  static SPA  ──served by──▶  apps/server
   apps/tests   ──drives──▶  the running server (UI through the browser, API directly)
```

In the container the SPA and API are **same-origin** (`http://localhost:8000`), so the
E2E suite targets a single base URL and no CORS is needed. CORS for the Vite dev server
(`http://localhost:5173`) stays configured for local development only.

## Tech stack

| Layer        | Technology                                                          |
|--------------|---------------------------------------------------------------------|
| Backend      | Python 3.12, Django, Django REST Framework, gunicorn, WhiteNoise    |
| Frontend     | React 19, TypeScript, Vite, shadcn/ui (Radix), Tailwind CSS         |
| Validation   | Zod (frontend) · DRF serializers (backend) · JSON Schema (E2E)      |
| Data fetching| TanStack Query (React Query) + a typed `fetch` client               |
| Forms        | react-hook-form + `@hookform/resolvers` (zod)                       |
| E2E testing  | Playwright with **Python** (`pytest-playwright`), Page Object Model |
| Unit testing | Vitest + Testing Library (client) · pytest-django (server)          |
| Reporting    | Allure - one unified report across client, server, and E2E results  |
| Tooling      | ruff + black (Python) · oxlint + TypeScript strict (frontend)       |

## Monorepo layout

```
.
├── apps/
│   ├── server/   # Django project + DRF API        → apps/server/README.md
│   ├── client/   # React + Vite single-page app     → apps/client/README.md
│   └── tests/    # Playwright (Python) E2E + API     → apps/tests/README.md
├── docker/
│   └── entrypoint.sh        # migrate → seed → serve → unit → e2e → allure
├── Dockerfile               # single multi-stage image (client build + server + tests)
├── docker-compose.yml       # convenience wrapper for a local pipeline run
├── run-local.ps1            # same, for PowerShell
└── .github/workflows/ci.yml # build image → run pipeline → publish Allure to Pages
```

Each application is documented in depth in its own README - start here, then follow the
links:

- **[apps/server/README.md](apps/server/README.md)** - Django + DRF API, layered
  architecture (selectors / services / exceptions), migrations, the `seed_todos`
  command, and 100%-covered pytest suite.
- **[apps/client/README.md](apps/client/README.md)** - React + TypeScript SPA,
  schemas-as-source-of-truth, the typed fetch client, TanStack Query hooks, and a
  100%-covered Vitest suite (with MSW).
- **[apps/tests/README.md](apps/tests/README.md)** - Playwright Python E2E with the Page
  Object Model and JSON-Schema API validation.

---

## Quick start

### Option A - run the whole pipeline in Docker (recommended)

One command builds the image, runs migrations, seeds data, runs every test suite, and
generates the Allure report:

```bash
docker compose up --build
```

When it finishes, open the rendered report:

```
./allure-report/index.html
```

The container runs the pipeline once and exits; `./allure-results` and `./allure-report`
are mounted to the host.

### Option B - run each app locally for development

See each app's README for full instructions. In short:

```bash
# Backend  → http://localhost:8000
cd apps/server && python manage.py migrate && python manage.py runserver

# Frontend → http://localhost:5173 (proxies /api to :8000)
cd apps/client && npm install && npm run dev

# E2E (against a running server)
cd apps/tests && pytest
```

## The in-container pipeline

Running the image executes [`docker/entrypoint.sh`](docker/entrypoint.sh):

1. `python manage.py migrate`
2. `python manage.py seed_todos --count 10`
3. start gunicorn and wait until `/api/health/` is healthy
4. **backend** unit + integration tests → `pytest` (`apps/server`)
5. **E2E** UI + API tests → `pytest` (`apps/tests`)
6. `allure generate` → one unified report

Client unit/component (Vitest) results are produced during the image build and merged
into the same Allure report.

## API contract (single source of truth)

The REST contract is shared by all three apps and kept in sync across the DRF serializer,
the zod schema, and the E2E JSON schemas. Base URL: `/api/` (same-origin in the image,
`http://localhost:8000/api/` in dev).

| Method | Path                | Success         | Errors            |
|--------|---------------------|-----------------|-------------------|
| GET    | `/api/health/`      | `200 {"status":"ok"}` | -           |
| GET    | `/api/todos/`       | `200 Todo[]` (plain array, no pagination, ordered `-created_at,-id`) | - |
| POST   | `/api/todos/`       | `201 Todo`      | `400` validation  |
| GET    | `/api/todos/{id}/`  | `200 Todo`      | `404`             |
| PATCH  | `/api/todos/{id}/`  | `200 Todo`      | `400`, `404`      |
| PUT    | `/api/todos/{id}/`  | `200 Todo`      | `400`, `404`      |
| DELETE | `/api/todos/{id}/`  | `204`           | `404`             |

`Todo` = `{ id: number, title: string (1-255, trimmed), completed: boolean,
created_at: string (ISO), updated_at: string (ISO) }`.

## Testing summary

| Suite              | Tests | Coverage                         |
|--------------------|-------|----------------------------------|
| Client (Vitest)    | 80    | 100% statements/branches/functions/lines |
| Server (pytest)    | 70    | 100% (`--cov-fail-under=100`)    |
| E2E (Playwright)   | 36    | every UI flow + every endpoint × status code |

## Continuous integration & the Allure report

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push: it builds the
image, runs the full pipeline, and uploads `allure-results`/`allure-report` as workflow
artifacts. On the `main` branch it also publishes the rendered report to **GitHub Pages**
(via the `gh-pages` branch, under `/allure`).

To enable it once: **repo Settings → Pages → Source: “Deploy from a branch” → Branch:
`gh-pages` / root**. The report is then served at:

```
https://pavlovic-bojan.github.io/django-react-playwright-python/allure/
```

## Conventions

- **Type safety end-to-end.** DRF serializer fields ↔ zod schema fields ↔ TS types ↔ E2E
  JSON schemas must agree. The API contract is the referee.
- **Validate on both sides** - zod on the client, DRF serializers on the server.
- **Tests describe behavior**, use Page Objects and semantic locators, and are isolated:
  they create and clean their own data and never depend on the seeded demo todos.
- Python: 4-space indentation, type hints, `ruff` + `black` clean.
- TypeScript: no `any`, strict compiler options, oxlint clean.
