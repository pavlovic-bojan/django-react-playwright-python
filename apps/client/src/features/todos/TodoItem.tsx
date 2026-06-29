import { Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import type { Todo } from "@/schemas/todo";
import { useDeleteTodo, useUpdateTodo } from "./hooks";

export function TodoItem({ todo }: { todo: Todo }) {
  const updateTodo = useUpdateTodo();
  const deleteTodo = useDeleteTodo();

  const handleToggle = (checked: boolean) => {
    updateTodo.mutate(
      { id: todo.id, patch: { completed: checked } },
      { onError: () => toast.error("Could not update todo.") },
    );
  };

  const handleDelete = () => {
    deleteTodo.mutate(todo.id, {
      onError: () => toast.error("Could not delete todo."),
    });
  };

  return (
    <li className="flex items-center gap-3 rounded-md border bg-card px-3 py-2.5">
      <Checkbox
        checked={todo.completed}
        onCheckedChange={(value) => handleToggle(value === true)}
        disabled={updateTodo.isPending}
        aria-label={todo.title}
      />
      <span
        className={cn(
          "flex-1 text-left text-sm",
          todo.completed && "text-muted-foreground line-through",
        )}
      >
        {todo.title}
      </span>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="text-muted-foreground hover:text-destructive"
        aria-label={`Delete ${todo.title}`}
        onClick={handleDelete}
        disabled={deleteTodo.isPending}
      >
        <Trash2 aria-hidden="true" />
      </Button>
    </li>
  );
}
