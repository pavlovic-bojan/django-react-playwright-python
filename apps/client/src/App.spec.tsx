import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import App from "./App";

// Mock child feature components to isolate App from hook/query/HTTP dependencies.
vi.mock("@/features/todos/TodoForm", () => ({
  TodoForm: () => <div data-testid="todo-form" />,
}));

vi.mock("@/features/todos/TodoList", () => ({
  TodoList: () => <div data-testid="todo-list" />,
}));

describe("App", () => {
  it("renders the main heading", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { level: 1, name: "Todos" }),
    ).toBeInTheDocument();
  });

  it("renders the card title and description", () => {
    render(<App />);
    expect(screen.getByText("Add a todo")).toBeInTheDocument();
    expect(
      screen.getByText("Keep track of what needs to get done."),
    ).toBeInTheDocument();
  });

  it("renders the TodoForm component", () => {
    render(<App />);
    expect(screen.getByTestId("todo-form")).toBeInTheDocument();
  });

  it("renders the TodoList component", () => {
    render(<App />);
    expect(screen.getByTestId("todo-list")).toBeInTheDocument();
  });
});
