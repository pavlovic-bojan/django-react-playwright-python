import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { todoKeys } from "@/lib/query-keys";
import type { CreateTodoInput, UpdateTodoInput } from "@/schemas/todo";
import * as api from "./api";

export function useTodos() {
  return useQuery({
    queryKey: todoKeys.all(),
    queryFn: api.getTodos,
  });
}

export function useCreateTodo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateTodoInput) => api.createTodo(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: todoKeys.all() }),
  });
}

export function useUpdateTodo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: number; patch: UpdateTodoInput }) =>
      api.updateTodo(vars.id, vars.patch),
    onSuccess: () => qc.invalidateQueries({ queryKey: todoKeys.all() }),
  });
}

export function useDeleteTodo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteTodo(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: todoKeys.all() }),
  });
}
