/**
 * Centralized TanStack Query key factory for Todo resources.
 *
 * Using factory functions (instead of bare arrays) prevents typos, keeps keys
 * consistent across queries and cache invalidation, and makes key shapes
 * discoverable in one place.
 */
export const todoKeys = {
  /** Matches all todo-related cache entries — used to invalidate after writes. */
  all: () => ["todos"] as const,
} as const;
