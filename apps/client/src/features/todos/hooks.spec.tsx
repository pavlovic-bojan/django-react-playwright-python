import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { todoKeys } from "@/lib/query-keys";
import * as api from "./api";
import { useTodos, useCreateTodo, useUpdateTodo, useDeleteTodo } from "./hooks";

// Auto-mock the todos API layer so hooks are tested in isolation.
vi.mock("./api");

const SAMPLE_TODO = {
  id: 1,
  title: "Buy milk",
  completed: false,
  created_at: "2026-06-29T10:00:00Z",
  updated_at: "2026-06-29T10:00:00Z",
} as const;

/** Creates a fresh QueryClient + wrapper per test to avoid state leakage. */
function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
  return { qc, wrapper };
}

beforeEach(() => {
  vi.resetAllMocks();
});

// ---------------------------------------------------------------------------
// useTodos
// ---------------------------------------------------------------------------
describe("useTodos", () => {
  it("returns data from api.getTodos on success", async () => {
    vi.mocked(api.getTodos).mockResolvedValue([SAMPLE_TODO]);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useTodos(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([SAMPLE_TODO]);
    expect(api.getTodos).toHaveBeenCalledTimes(1);
  });

  it("surfaces the error when api.getTodos rejects", async () => {
    vi.mocked(api.getTodos).mockRejectedValue(new Error("Network error"));

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useTodos(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeInstanceOf(Error);
  });
});

// ---------------------------------------------------------------------------
// useCreateTodo
// ---------------------------------------------------------------------------
describe("useCreateTodo", () => {
  it("calls api.createTodo with the provided input", async () => {
    vi.mocked(api.createTodo).mockResolvedValue({ ...SAMPLE_TODO });

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useCreateTodo(), { wrapper });

    result.current.mutate({ title: "Buy milk", completed: false });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.createTodo).toHaveBeenCalledWith({
      title: "Buy milk",
      completed: false,
    });
  });

  it("invalidates the todos query on success", async () => {
    vi.mocked(api.createTodo).mockResolvedValue({ ...SAMPLE_TODO });

    const { qc, wrapper } = createWrapper();
    const spy = vi.spyOn(qc, "invalidateQueries");

    const { result } = renderHook(() => useCreateTodo(), { wrapper });
    result.current.mutate({ title: "Buy milk", completed: false });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(spy).toHaveBeenCalledWith({ queryKey: todoKeys.all() });
  });

  it("surfaces the error when api.createTodo rejects", async () => {
    vi.mocked(api.createTodo).mockRejectedValue(new Error("Server error"));

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useCreateTodo(), { wrapper });

    result.current.mutate({ title: "Buy milk", completed: false });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeInstanceOf(Error);
  });
});

// ---------------------------------------------------------------------------
// useUpdateTodo
// ---------------------------------------------------------------------------
describe("useUpdateTodo", () => {
  it("calls api.updateTodo with id and patch", async () => {
    const updated = { ...SAMPLE_TODO, completed: true };
    vi.mocked(api.updateTodo).mockResolvedValue(updated);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useUpdateTodo(), { wrapper });

    result.current.mutate({ id: 1, patch: { completed: true } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateTodo).toHaveBeenCalledWith(1, { completed: true });
  });

  it("invalidates the todos query on success", async () => {
    vi.mocked(api.updateTodo).mockResolvedValue({ ...SAMPLE_TODO });

    const { qc, wrapper } = createWrapper();
    const spy = vi.spyOn(qc, "invalidateQueries");

    const { result } = renderHook(() => useUpdateTodo(), { wrapper });
    result.current.mutate({ id: 1, patch: { completed: true } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(spy).toHaveBeenCalledWith({ queryKey: todoKeys.all() });
  });

  it("surfaces the error when api.updateTodo rejects", async () => {
    vi.mocked(api.updateTodo).mockRejectedValue(new Error("Not found"));

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useUpdateTodo(), { wrapper });

    result.current.mutate({ id: 99, patch: { completed: true } });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});

// ---------------------------------------------------------------------------
// useDeleteTodo
// ---------------------------------------------------------------------------
describe("useDeleteTodo", () => {
  it("calls api.deleteTodo with the todo id", async () => {
    vi.mocked(api.deleteTodo).mockResolvedValue(undefined);

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useDeleteTodo(), { wrapper });

    result.current.mutate(1);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteTodo).toHaveBeenCalledWith(1);
  });

  it("invalidates the todos query on success", async () => {
    vi.mocked(api.deleteTodo).mockResolvedValue(undefined);

    const { qc, wrapper } = createWrapper();
    const spy = vi.spyOn(qc, "invalidateQueries");

    const { result } = renderHook(() => useDeleteTodo(), { wrapper });
    result.current.mutate(1);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(spy).toHaveBeenCalledWith({ queryKey: todoKeys.all() });
  });

  it("surfaces the error when api.deleteTodo rejects", async () => {
    vi.mocked(api.deleteTodo).mockRejectedValue(new Error("Not found"));

    const { wrapper } = createWrapper();
    const { result } = renderHook(() => useDeleteTodo(), { wrapper });

    result.current.mutate(99);

    await waitFor(() => expect(result.current.isError).toBe(true));
  });
});
