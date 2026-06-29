import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";

import { server } from "@/test/server";
import { ApiError } from "@/lib/api";
import { getTodos, createTodo, updateTodo, deleteTodo } from "./api";

const SAMPLE_TODO = {
  id: 1,
  title: "Buy milk",
  completed: false,
  created_at: "2026-06-29T10:00:00Z",
  updated_at: "2026-06-29T10:00:00Z",
} as const;

// ---------------------------------------------------------------------------
// getTodos
// ---------------------------------------------------------------------------
describe("getTodos", () => {
  it("fetches /todos/ and returns a validated list", async () => {
    server.use(http.get("*/api/todos/", () => HttpResponse.json([SAMPLE_TODO])));

    const result = await getTodos();
    expect(result).toEqual([SAMPLE_TODO]);
  });

  it("returns an empty list when there are no todos", async () => {
    server.use(http.get("*/api/todos/", () => HttpResponse.json([])));

    expect(await getTodos()).toEqual([]);
  });

  it("throws a ZodError when the server returns an invalid shape", async () => {
    server.use(
      http.get("*/api/todos/", () => HttpResponse.json([{ wrong: "shape" }])),
    );

    await expect(getTodos()).rejects.toThrow();
  });

  it("propagates ApiError from the server", async () => {
    server.use(
      http.get("*/api/todos/", () =>
        HttpResponse.json({ detail: "Server error" }, { status: 500 }),
      ),
    );

    await expect(getTodos()).rejects.toBeInstanceOf(ApiError);
  });
});

// ---------------------------------------------------------------------------
// createTodo
// ---------------------------------------------------------------------------
describe("createTodo", () => {
  it("POSTs to /todos/ with the input body and returns the validated todo", async () => {
    let captured: unknown;
    server.use(
      http.post("*/api/todos/", async ({ request }) => {
        captured = await request.json();
        return HttpResponse.json(SAMPLE_TODO, { status: 201 });
      }),
    );

    const input = { title: "Buy milk", completed: false };
    const result = await createTodo(input);

    expect(captured).toEqual(input);
    expect(result).toEqual(SAMPLE_TODO);
  });

  it("throws a ZodError when the server returns an invalid shape", async () => {
    server.use(
      http.post("*/api/todos/", () =>
        HttpResponse.json({ wrong: "shape" }, { status: 201 }),
      ),
    );

    await expect(
      createTodo({ title: "Buy milk", completed: false }),
    ).rejects.toThrow();
  });
});

// ---------------------------------------------------------------------------
// updateTodo
// ---------------------------------------------------------------------------
describe("updateTodo", () => {
  it("PATCHes /todos/{id}/ and returns the validated updated todo", async () => {
    const updated = { ...SAMPLE_TODO, completed: true };
    let capturedBody: unknown;

    server.use(
      http.patch("*/api/todos/1/", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(updated);
      }),
    );

    const result = await updateTodo(1, { completed: true });

    expect(capturedBody).toEqual({ completed: true });
    expect(result).toEqual(updated);
  });

  it("throws a ZodError when the server returns an invalid shape", async () => {
    server.use(
      http.patch("*/api/todos/1/", () =>
        HttpResponse.json({ wrong: "shape" }),
      ),
    );

    await expect(updateTodo(1, { completed: true })).rejects.toThrow();
  });
});

// ---------------------------------------------------------------------------
// deleteTodo
// ---------------------------------------------------------------------------
describe("deleteTodo", () => {
  it("DELETEs /todos/{id}/ and resolves with undefined", async () => {
    server.use(
      http.delete(
        "*/api/todos/1/",
        () => new HttpResponse(null, { status: 204 }),
      ),
    );

    await expect(deleteTodo(1)).resolves.toBeUndefined();
  });

  it("propagates ApiError from a 404 response", async () => {
    server.use(
      http.delete("*/api/todos/99/", () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 }),
      ),
    );

    await expect(deleteTodo(99)).rejects.toBeInstanceOf(ApiError);
  });
});
