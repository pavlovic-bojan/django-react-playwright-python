import { http, HttpResponse } from "msw";

/** Shared sample Todo fixture used in default handlers and overridable per test. */
export const SAMPLE_TODO = {
  id: 1,
  title: "Buy milk",
  completed: false,
  created_at: "2026-06-29T10:00:00Z",
  updated_at: "2026-06-29T10:00:00Z",
} as const;

/**
 * Default MSW request handlers for the Todo API.
 *
 * These cover the happy path. Tests that need errors or different payloads
 * should add per-test handlers via `server.use(...)` — they take precedence
 * over these defaults and are reset after each test.
 */
export const handlers = [
  http.get("*/api/todos/", () => HttpResponse.json([SAMPLE_TODO])),

  http.post("*/api/todos/", () =>
    HttpResponse.json(SAMPLE_TODO, { status: 201 }),
  ),

  http.patch("*/api/todos/:id/", () => HttpResponse.json(SAMPLE_TODO)),

  http.delete("*/api/todos/:id/", () => new HttpResponse(null, { status: 204 })),
];
