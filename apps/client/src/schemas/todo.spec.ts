import { describe, it, expect } from "vitest";

import { createTodoSchema, todoSchema } from "./todo";

describe("createTodoSchema", () => {
  it("accepts a valid title and defaults completed to false", () => {
    const result = createTodoSchema.safeParse({ title: "Buy milk" });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data).toEqual({ title: "Buy milk", completed: false });
    }
  });

  it("trims surrounding whitespace from the title", () => {
    const result = createTodoSchema.safeParse({ title: "  Buy milk  " });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.title).toBe("Buy milk");
    }
  });

  it("rejects a blank title with 'Title is required'", () => {
    const result = createTodoSchema.safeParse({ title: "" });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe("Title is required");
    }
  });

  it("rejects a whitespace-only title with 'Title is required'", () => {
    const result = createTodoSchema.safeParse({ title: "   " });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe("Title is required");
    }
  });

  it("rejects a title longer than 255 characters", () => {
    const result = createTodoSchema.safeParse({ title: "a".repeat(256) });
    expect(result.success).toBe(false);
  });
});

describe("todoSchema", () => {
  it("parses a valid API todo object", () => {
    const apiTodo = {
      id: 1,
      title: "Buy milk",
      completed: false,
      created_at: "2026-06-29T10:00:00Z",
      updated_at: "2026-06-29T10:00:00Z",
    };
    const result = todoSchema.safeParse(apiTodo);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data).toEqual(apiTodo);
    }
  });

  it("rejects an object missing required fields", () => {
    const result = todoSchema.safeParse({ id: 1, title: "x" });
    expect(result.success).toBe(false);
  });

  it("rejects a non-numeric id", () => {
    const result = todoSchema.safeParse({
      id: "1",
      title: "x",
      completed: false,
      created_at: "2026-06-29T10:00:00Z",
      updated_at: "2026-06-29T10:00:00Z",
    });
    expect(result.success).toBe(false);
  });
});
