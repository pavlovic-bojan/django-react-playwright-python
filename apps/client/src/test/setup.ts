import "@testing-library/jest-dom/vitest";
import { beforeAll, afterEach, afterAll } from "vitest";
import { cleanup } from "@testing-library/react";

import { server } from "./server";

// Start the MSW server before all tests in a file.
// "warn" logs unhandled requests without failing — prevents false failures
// from libraries making internal fetch calls (e.g. error reporting).
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));

// Reset per-test handler overrides so they don't bleed into the next test.
afterEach(() => {
  server.resetHandlers();
  cleanup();
});

// Shut down the MSW server cleanly after all tests in the file.
afterAll(() => server.close());
