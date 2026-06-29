# apps/client - React + TypeScript SPA

The frontend for the Todo app: a React 19 single-page application built with Vite and
TypeScript (strict). It validates with zod, fetches with TanStack Query over a typed
`fetch` client, and uses shadcn/ui (Radix) components styled with Tailwind CSS.

For the cross-cutting picture (Docker pipeline, CI, Allure), see the
[root README](../../README.md).

## Architecture

```
src/
  main.tsx                 # DOM bootstrap
  App.tsx                  # ErrorBoundary + QueryClientProvider + Toaster + page
  components/
    ErrorBoundary.tsx      # catches render errors, shows a recoverable fallback
    ui/                    # shadcn/ui primitives (generated)
  features/todos/
    api.ts                 # getTodos / createTodo / updateTodo / deleteTodo (zod-parsed)
    hooks.ts               # TanStack Query hooks (queries + mutations, cache invalidation)
    TodoForm.tsx           # add-todo form (react-hook-form + zod resolver)
    TodoItem.tsx           # one todo row (toggle + delete)
    TodoList.tsx           # list with loading / empty / error + retry states
  lib/
    api.ts                 # apiFetch + ApiError (typed fetch wrapper)
    env.ts                 # zod-validated environment access (getApiBase)
    query-client.ts        # the QueryClient instance
    query-keys.ts          # todoKeys query-key factory
    utils.ts               # cn() class-name helper
  schemas/
    todo.ts                # createTodoSchema + todoSchema - validation source of truth
  test/
    setup.ts               # Testing Library + MSW lifecycle
    server.ts              # MSW setupServer
    handlers.ts            # default happy-path API handlers
```

### Principles

- **Schemas are the source of truth.** `src/schemas/todo.ts` defines the zod schemas;
  TypeScript types are inferred from them and the API layer parses every server response
  through them, so a contract drift surfaces as a validation error rather than a silent
  bug.
- **Layered data access.** Components call hooks (`features/todos/hooks.ts`); hooks call
  the typed API functions (`features/todos/api.ts`); those call the generic
  `apiFetch` client (`lib/api.ts`). Query keys come from a single factory
  (`lib/query-keys.ts`).
- **Configuration is validated.** Environment access goes through `lib/env.ts` instead of
  reading `import.meta.env` ad hoc.
- **Resilient UI.** An `ErrorBoundary` wraps the app, and the list renders explicit
  loading, empty, and error (with retry) states.

The API base URL comes from `VITE_API_URL` (defaults to `/api`, same-origin). In dev,
Vite proxies `/api` to the Django server on `:8000`.

## Local development

```bash
cd apps/client

npm install
npm run dev        # http://localhost:5173  (proxies /api → :8000)
npm run build      # type-check (tsc -b) + production build → dist/
npm run preview    # serve the production build locally
npm run lint       # oxlint
```

## Tests & coverage

Unit and component tests run on **Vitest** with Testing Library and a **jsdom**
environment. Network is mocked at the HTTP boundary with **MSW**, so the API and hook
layers are exercised for real rather than stubbed.

```bash
cd apps/client

npm test            # vitest run (one-shot)
npm run test:watch  # watch mode
npm run test:coverage
```

- **80 tests** across 13 spec files (`*.spec.ts` / `*.spec.tsx`).
- **100% coverage** - statements, branches, functions, and lines - enforced by v8
  coverage thresholds in `vite.config.ts`.
- Excluded from coverage (with rationale): `main.tsx` (DOM bootstrap),
  `components/ui/**` (generated shadcn primitives), and `test/**` (test infrastructure).
- Results are written for Allure via `allure-vitest`.

## Tech notes

- React 19, Vite 8, TypeScript ~6 (strict, `noUncheckedIndexedAccess`,
  `noImplicitOverride`).
- State/data: `@tanstack/react-query` v5. Forms: `react-hook-form` +
  `@hookform/resolvers` (zod). Toasts: `sonner`.
- UI: shadcn/ui on Radix primitives, Tailwind CSS v4. Linting: oxlint.
