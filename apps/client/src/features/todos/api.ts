import { apiFetch } from "@/lib/api";
import {
  todoSchema,
  todoListSchema,
  type CreateTodoInput,
  type Todo,
  type UpdateTodoInput,
} from "@/schemas/todo";

const TODOS = "/todos/";

/** GET /api/todos/ — newest first (server-ordered). */
export async function getTodos(): Promise<Todo[]> {
  return todoListSchema.parse(await apiFetch(TODOS));
}

/** POST /api/todos/ */
export async function createTodo(input: CreateTodoInput): Promise<Todo> {
  return todoSchema.parse(
    await apiFetch(TODOS, {
      method: "POST",
      body: JSON.stringify(input),
    }),
  );
}

/** PATCH /api/todos/{id}/ */
export async function updateTodo(
  id: number,
  patch: UpdateTodoInput,
): Promise<Todo> {
  return todoSchema.parse(
    await apiFetch(`${TODOS}${id}/`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),
  );
}

/** DELETE /api/todos/{id}/ — 204 No Content. */
export async function deleteTodo(id: number): Promise<void> {
  await apiFetch<void>(`${TODOS}${id}/`, { method: "DELETE" });
}
