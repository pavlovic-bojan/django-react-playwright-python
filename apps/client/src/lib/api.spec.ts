import { describe, it, expect } from "vitest";
import { http, HttpResponse } from "msw";

import { server } from "@/test/server";
import { apiFetch, ApiError } from "./api";

// ---------------------------------------------------------------------------
// ApiError
// ---------------------------------------------------------------------------
describe("ApiError", () => {
  it("is an Error subclass with the right name, status, body, and message", () => {
    const body = { detail: "Not found" };
    const err = new ApiError(404, body);

    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.name).toBe("ApiError");
    expect(err.status).toBe(404);
    expect(err.body).toStrictEqual(body);
    expect(err.message).toBe("API 404");
  });

  it("accepts null as body", () => {
    const err = new ApiError(500, null);
    expect(err.body).toBeNull();
    expect(err.status).toBe(500);
  });
});

// ---------------------------------------------------------------------------
// apiFetch — all tests use MSW to intercept at the HTTP boundary
// ---------------------------------------------------------------------------
describe("apiFetch", () => {
  it("returns parsed JSON for a 200 OK response", async () => {
    const data = { id: 1, title: "Test" };
    server.use(http.get("*/api/ping/", () => HttpResponse.json(data)));

    const result = await apiFetch<typeof data>("/ping/");
    expect(result).toEqual(data);
  });

  it("returns undefined for a 204 No Content response", async () => {
    server.use(
      http.delete("*/api/todos/1/", () => new HttpResponse(null, { status: 204 })),
    );

    const result = await apiFetch<void>("/todos/1/", { method: "DELETE" });
    expect(result).toBeUndefined();
  });

  it("throws ApiError with the parsed body for a non-ok JSON response", async () => {
    const errorBody = { title: ["This field is required."] };
    server.use(
      http.post("*/api/todos/", () =>
        HttpResponse.json(errorBody, { status: 400 }),
      ),
    );

    try {
      await apiFetch("/todos/", { method: "POST", body: JSON.stringify({}) });
      expect.fail("expected ApiError to be thrown");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      const apiErr = e as ApiError;
      expect(apiErr.status).toBe(400);
      expect(apiErr.body).toEqual(errorBody);
    }
  });

  it("throws ApiError with null body when the error response is not JSON", async () => {
    server.use(
      http.get(
        "*/api/oops/",
        () =>
          new HttpResponse("Internal Server Error", {
            status: 500,
            headers: { "Content-Type": "text/plain" },
          }),
      ),
    );

    try {
      await apiFetch("/oops/");
      expect.fail("expected ApiError to be thrown");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      const apiErr = e as ApiError;
      expect(apiErr.status).toBe(500);
      expect(apiErr.body).toBeNull();
    }
  });

  it("sends Content-Type: application/json and merges caller headers", async () => {
    let capturedContentType: string | null = null;
    let capturedCustomHeader: string | null = null;

    server.use(
      http.post("*/api/todos/", ({ request }) => {
        capturedContentType = request.headers.get("Content-Type");
        capturedCustomHeader = request.headers.get("X-Custom");
        return HttpResponse.json({ ok: true });
      }),
    );

    await apiFetch("/todos/", {
      method: "POST",
      headers: { "X-Custom": "yes" },
      body: JSON.stringify({}),
    });

    expect(capturedContentType).toBe("application/json");
    expect(capturedCustomHeader).toBe("yes");
  });
});
