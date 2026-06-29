import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { toast } from "sonner";

import { TodoItem } from "./TodoItem";
import type { Todo } from "@/schemas/todo";

// Prevent sonner from attempting portal renders in jsdom.
vi.mock("sonner", () => ({
  toast: { error: vi.fn() },
}));

const { updateMutate, deleteMutate } = vi.hoisted(() => ({
  updateMutate: vi.fn(),
  deleteMutate: vi.fn(),
}));

vi.mock("./hooks", () => ({
  useUpdateTodo: () => ({ mutate: updateMutate, isPending: false }),
  useDeleteTodo: () => ({ mutate: deleteMutate, isPending: false }),
}));

const todo: Todo = {
  id: 1,
  title: "Buy milk",
  completed: false,
  created_at: "2026-06-29T10:00:00Z",
  updated_at: "2026-06-29T10:00:00Z",
};

type MutateCallbacks = { onError: () => void };

describe("TodoItem", () => {
  beforeEach(() => {
    updateMutate.mockReset();
    deleteMutate.mockReset();
    vi.mocked(toast.error).mockReset();
  });

  it("renders as a listitem exposing the title, a named checkbox and delete button", () => {
    render(<TodoItem todo={todo} />);

    expect(screen.getByRole("listitem")).toHaveTextContent("Buy milk");
    expect(
      screen.getByRole("checkbox", { name: "Buy milk" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Delete Buy milk" }),
    ).toBeInTheDocument();
  });

  it("toggles completion when the checkbox is clicked", async () => {
    const user = userEvent.setup();
    render(<TodoItem todo={todo} />);

    await user.click(screen.getByRole("checkbox", { name: "Buy milk" }));

    expect(updateMutate).toHaveBeenCalledWith(
      { id: 1, patch: { completed: true } },
      expect.anything(),
    );
  });

  it("shows an error toast when the toggle update fails (onError callback)", async () => {
    const user = userEvent.setup();
    render(<TodoItem todo={todo} />);

    await user.click(screen.getByRole("checkbox", { name: "Buy milk" }));

    // Extract and invoke the onError callback passed to updateMutate.
    const callbacks = updateMutate.mock.calls[0]?.[1] as MutateCallbacks | undefined;
    expect(callbacks?.onError).toBeDefined();
    callbacks?.onError();

    expect(toast.error).toHaveBeenCalledWith("Could not update todo.");
  });

  it("deletes the todo when the delete button is clicked", async () => {
    const user = userEvent.setup();
    render(<TodoItem todo={todo} />);

    await user.click(screen.getByRole("button", { name: "Delete Buy milk" }));

    expect(deleteMutate).toHaveBeenCalledWith(1, expect.anything());
  });

  it("shows an error toast when the delete fails (onError callback)", async () => {
    const user = userEvent.setup();
    render(<TodoItem todo={todo} />);

    await user.click(screen.getByRole("button", { name: "Delete Buy milk" }));

    // Extract and invoke the onError callback passed to deleteMutate.
    const callbacks = deleteMutate.mock.calls[0]?.[1] as MutateCallbacks | undefined;
    expect(callbacks?.onError).toBeDefined();
    callbacks?.onError();

    expect(toast.error).toHaveBeenCalledWith("Could not delete todo.");
  });
});
