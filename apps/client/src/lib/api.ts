import { getApiBase } from "./env";

/** Normalized error thrown for any non-2xx API response. */
export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown) {
    super(`API ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

/**
 * Typed fetch wrapper used by every feature API module.
 *
 * - Sends `Content-Type: application/json` on every request.
 * - Returns `undefined` (typed as `T`) for 204 No Content.
 * - Throws `ApiError` for any non-2xx status.
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${getApiBase()}${path}`, {
    ...init,
    // headers must come AFTER ...init so the merged set is never overwritten
    // when the caller supplies its own headers key inside init.
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, body);
  }

  // 204 No Content (DELETE) carries no body to parse.
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}
