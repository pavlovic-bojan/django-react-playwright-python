import { describe, it, expect } from "vitest";
import { QueryClient } from "@tanstack/react-query";

import { queryClient } from "./query-client";

describe("queryClient", () => {
  it("is a QueryClient instance", () => {
    expect(queryClient).toBeInstanceOf(QueryClient);
  });

  it("has staleTime, retry, and refetchOnWindowFocus configured", () => {
    const defaultOptions = queryClient.getDefaultOptions();
    const queries = defaultOptions.queries ?? {};
    expect(queries.staleTime).toBe(5_000);
    expect(queries.retry).toBe(1);
    expect(queries.refetchOnWindowFocus).toBe(false);
  });
});
