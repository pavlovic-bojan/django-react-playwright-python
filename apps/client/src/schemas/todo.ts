import { z } from "zod";

/**
 * Todo resource — mirrors the api-contract exactly.
 *
 * | Field      | Type              | Read/Write |
 * |------------|-------------------|------------|
 * | id         | integer           | read-only  |
 * | title      | string (1–255)    | read/write |
 * | completed  | boolean           | read/write |
 * | created_at | string (ISO 8601) | read-only  |
 * | updated_at | string (ISO 8601) | read-only  |
 */
export const todoSchema = z.object({
  id: z.number().int(),
  title: z.string(),
  completed: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const todoListSchema = z.array(todoSchema);

/** Create/write input — enforces the contract's write rules client-side. */
export const createTodoSchema = z.object({
  title: z.string().trim().min(1, "Title is required").max(255),
  completed: z.boolean().default(false),
});

/** Partial update — every writable field is optional. */
export const updateTodoSchema = createTodoSchema.partial();

export type Todo = z.infer<typeof todoSchema>;
export type CreateTodoInput = z.infer<typeof createTodoSchema>;
export type UpdateTodoInput = z.infer<typeof updateTodoSchema>;
