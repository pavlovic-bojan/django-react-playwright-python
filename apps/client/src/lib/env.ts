import { z } from "zod";

/** Zod schema for application environment variables. */
export const envSchema = z.object({
  /**
   * Optional API base URL override.
   * Falls back to same-origin `/api` when absent (production container and
   * Vite dev proxy both satisfy this).
   */
  VITE_API_URL: z.string().optional(),
});

export type Env = z.infer<typeof envSchema>;

/**
 * Parses and validates a raw env object against `envSchema`.
 * Throws a descriptive ZodError if validation fails.
 *
 * @param rawEnv - Raw environment variables. Defaults to `import.meta.env`.
 */
export function parseEnv(rawEnv: Record<string, unknown> = import.meta.env as Record<string, unknown>): Env {
  return envSchema.parse(rawEnv);
}

/** Validated runtime environment variables. */
export const env: Env = parseEnv();

/**
 * Returns the API base URL.
 * Exposed as a function so both branches of the `?? "/api"` fallback can be
 * exercised in tests by passing different `Env` objects.
 *
 * @param e - Env to read from. Defaults to the runtime env singleton.
 */
export function getApiBase(e: Env = env): string {
  return e.VITE_API_URL ?? "/api";
}
