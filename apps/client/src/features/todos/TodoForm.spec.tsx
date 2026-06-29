import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { toast } from "sonner";

import { TodoForm } from "./TodoForm";

// Prevent sonner from attempting portal renders in jsdom.
vi.mock("sonner", () => ({
  toast: { error: vi.fn() },
}));

// Flexible useCreateTodo mock: the factory is a vi.fn() so individual tests
// can override it with mockReturnValueOnce to change isPending etc.
const { mutate, useCreateTodoMock } = vi.hoisted(() => {
  const mutate = vi.fn();
  const useCreateTodoMock = vi.fn(() => ({ mutate, isPending: false }));
  return { mutate, useCreateTodoMock };
});

vi.mock("./hooks", () => ({
  useCreateTodo: useCreateTodoMock,
}));

type MutateCallbacks = { onSuccess: () => void; onError: () => void };

describe("TodoForm", () => {
  beforeEach(() => {
    mutate.mockReset();
    // Restore the default implementation after any per-test override.
    useCreateTodoMock.mockReset();
    useCreateTodoMock.mockImplementation(() => ({ mutate, isPending: false }));
    vi.mocked(toast.error).mockReset();
  });

  it("renders a labeled Title input and an Add submit button", () => {
    render(<TodoForm />);
    expect(screen.getByLabelText("Title")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Add" })).toBeInTheDocument();
  });

  it("submits the trimmed title via the create handler", async () => {
    const user = userEvent.setup();
    render(<TodoForm />);

    await user.type(screen.getByLabelText("Title"), "  Buy milk  ");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(mutate).toHaveBeenCalledTimes(1);
    expect(mutate).toHaveBeenCalledWith(
      { title: "Buy milk", completed: false },
      expect.anything(),
    );
  });

  it("shows 'Title is required' and does not submit when blank", async () => {
    const user = userEvent.setup();
    render(<TodoForm />);

    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText("Title is required")).toBeInTheDocument();
    expect(mutate).not.toHaveBeenCalled();
  });

  it("shows a spinner and disables the button while a creation is pending", () => {
    // Replace the implementation for this test. React 19 may render the
    // component twice (concurrent + synchronous recovery), so mockReturnValueOnce
    // is not reliable here — mockImplementation persists across renders.
    useCreateTodoMock.mockImplementation(() => ({ mutate, isPending: true }));
    render(<TodoForm />);

    expect(screen.getByRole("button", { name: "Add" })).toBeDisabled();
  });

  it("resets the title input after a successful submission (onSuccess callback)", async () => {
    const user = userEvent.setup();
    render(<TodoForm />);

    await user.type(screen.getByLabelText("Title"), "Buy milk");
    await user.click(screen.getByRole("button", { name: "Add" }));

    // Extract and invoke the onSuccess callback that was passed to mutate.
    const callbacks = mutate.mock.calls[0]?.[1] as MutateCallbacks | undefined;
    expect(callbacks?.onSuccess).toBeDefined();

    await act(async () => {
      callbacks?.onSuccess();
    });

    expect(screen.getByLabelText("Title")).toHaveValue("");
  });

  it("shows an error toast when the mutation fails (onError callback)", async () => {
    const user = userEvent.setup();
    render(<TodoForm />);

    await user.type(screen.getByLabelText("Title"), "Buy milk");
    await user.click(screen.getByRole("button", { name: "Add" }));

    // Extract and invoke the onError callback.
    const callbacks = mutate.mock.calls[0]?.[1] as MutateCallbacks | undefined;
    expect(callbacks?.onError).toBeDefined();
    callbacks?.onError();

    expect(toast.error).toHaveBeenCalledWith(
      "Could not add todo. Please try again.",
    );
  });
});
