import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { TodoList } from "./TodoList";
import type { Todo } from "@/schemas/todo";

const { useTodosMock } = vi.hoisted(() => ({ useTodosMock: vi.fn() }));

vi.mock("./hooks", () => ({
  useTodos: useTodosMock,
  useUpdateTodo: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteTodo: () => ({ mutate: vi.fn(), isPending: false }),
}));

// Prevent sonner portal renders in jsdom (needed when TodoItem calls toast).
vi.mock("sonner", () => ({ toast: { error: vi.fn() } }));

const todos: Todo[] = [
  {
    id: 1,
    title: "Buy milk",
    completed: false,
    created_at: "2026-06-29T10:00:00Z",
    updated_at: "2026-06-29T10:00:00Z",
  },
  {
    id: 2,
    title: "Walk the dog",
    completed: true,
    created_at: "2026-06-29T09:00:00Z",
    updated_at: "2026-06-29T09:00:00Z",
  },
];

describe("TodoList", () => {
  beforeEach(() => {
    useTodosMock.mockReset();
  });

  it("renders one listitem per todo", () => {
    useTodosMock.mockReturnValue({
      data: todos,
      isPending: false,
      isError: false,
    });
    render(<TodoList />);

    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("Buy milk")).toBeInTheDocument();
    expect(screen.getByText("Walk the dog")).toBeInTheDocument();
  });

  it("shows the empty state when there are no todos", () => {
    useTodosMock.mockReturnValue({
      data: [],
      isPending: false,
      isError: false,
    });
    render(<TodoList />);

    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
    expect(
      screen.getByText("No todos yet. Add your first one above."),
    ).toBeInTheDocument();
  });

  it("shows a loading state while pending", () => {
    useTodosMock.mockReturnValue({ isPending: true, isError: false });
    render(<TodoList />);

    expect(screen.getByRole("status")).toHaveTextContent("Loading todos");
  });

  it("shows an error state with a retry control", () => {
    useTodosMock.mockReturnValue({
      isPending: false,
      isError: true,
      error: new Error("boom"),
      refetch: vi.fn(),
    });
    render(<TodoList />);

    expect(screen.getByRole("alert")).toHaveTextContent("Failed to load todos");
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("calls refetch when the Retry button is clicked", async () => {
    const user = userEvent.setup();
    const refetch = vi.fn();
    useTodosMock.mockReturnValue({
      isPending: false,
      isError: true,
      error: new Error("boom"),
      refetch,
    });
    render(<TodoList />);

    await user.click(screen.getByRole("button", { name: "Retry" }));

    expect(refetch).toHaveBeenCalledTimes(1);
  });

  it("shows an empty error message when the error is not an Error instance", () => {
    // Covers the `error instanceof Error ? error.message : ""` false branch.
    useTodosMock.mockReturnValue({
      isPending: false,
      isError: true,
      error: "plain string error",
      refetch: vi.fn(),
    });
    render(<TodoList />);

    // Alert is present; no Error.message is appended.
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to load todos.");
  });
});
