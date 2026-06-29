import { describe, it, expect } from "vitest";

import { envSchema, parseEnv, getApiBase } from "./env";

// ---------------------------------------------------------------------------
// envSchema
// ---------------------------------------------------------------------------
describe("envSchema", () => {
  it("accepts a valid VITE_API_URL string", () => {
    const result = envSchema.safeParse({ VITE_API_URL: "http://api.example.com" });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.VITE_API_URL).toBe("http://api.example.com");
    }
  });

  it("accepts an empty object (VITE_API_URL absent)", () => {
    const result = envSchema.safeParse({});
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.VITE_API_URL).toBeUndefined();
    }
  });

  it("rejects when VITE_API_URL is not a string", () => {
    const result = envSchema.safeParse({ VITE_API_URL: 42 });
    expect(result.success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// parseEnv
// ---------------------------------------------------------------------------
describe("parseEnv", () => {
  it("returns the VITE_API_URL from the provided object", () => {
    const parsed = parseEnv({ VITE_API_URL: "http://custom.api/" });
    expect(parsed.VITE_API_URL).toBe("http://custom.api/");
  });

  it("returns undefined VITE_API_URL when key is absent", () => {
    expect(parseEnv({}).VITE_API_URL).toBeUndefined();
  });

  it("throws when the env contains an invalid VITE_API_URL type", () => {
    expect(() =>
      parseEnv({ VITE_API_URL: 42 } as unknown as Record<string, unknown>),
    ).toThrow();
  });
});

// ---------------------------------------------------------------------------
// getApiBase
// ---------------------------------------------------------------------------
describe("getApiBase", () => {
  it("returns VITE_API_URL when the env has it set", () => {
    const e = parseEnv({ VITE_API_URL: "http://api.example.com" });
    expect(getApiBase(e)).toBe("http://api.example.com");
  });

  it("falls back to '/api' when VITE_API_URL is absent", () => {
    // Explicitly pass an env without VITE_API_URL to exercise the ?? "/api" branch.
    const e = parseEnv({});
    expect(getApiBase(e)).toBe("/api");
  });

  it("returns the runtime env value when called with no argument", () => {
    // In the test environment VITE_API_URL is set to "http://localhost/api"
    // (see vite.config.ts test.env), so getApiBase() must return that value.
    expect(getApiBase()).toBe("http://localhost/api");
  });
});
