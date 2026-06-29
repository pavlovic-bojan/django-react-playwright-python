import { LoaderCircle } from "lucide-react";

import { useTodos } from "./hooks";
import { TodoItem } from "./TodoItem";

export function TodoList() {
  const { data: todos, isPending, isError, error, refetch } = useTodos();

  if (isPending) {
    return (
      <div
        className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground"
        role="status"
        aria-live="polite"
      >
        <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
        Loading todos…
      </div>
    );
  }

  if (isError) {
    return (
      <div
        role="alert"
        className="flex flex-col items-center gap-3 rounded-md border border-destructive/40 bg-destructive/5 px-4 py-8 text-center text-sm text-destructive"
      >
        <p>Failed to load todos. {error instanceof Error ? error.message : ""}</p>
        <button
          type="button"
          onClick={() => refetch()}
          className="font-medium underline underline-offset-4"
        >
          Retry
        </button>
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No todos yet. Add your first one above.
      </p>
    );
  }

  return (
    <ul role="list" className="flex flex-col gap-2">
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </ul>
  );
}
