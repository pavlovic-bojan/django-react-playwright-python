import "@testing-library/jest-dom/vitest";
import { beforeAll, beforeEach, afterEach, afterAll } from "vitest";
import { cleanup } from "@testing-library/react";
import { epic, parentSuite } from "allure-js-commons";

import { server } from "./server";

// Spec files that render React components (Testing Library). Everything else
// (zod schemas, the fetch client, env, query keys, query hooks) is a pure unit test.
const COMPONENT_SPECS = new Set([
  "App.spec.tsx",
  "ErrorBoundary.spec.tsx",
  "TodoForm.spec.tsx",
  "TodoItem.spec.tsx",
  "TodoList.spec.tsx",
]);

// Put every test under one of two top-level Allure categories so the report reads
// as "React unit tests" and "React component tests" instead of one flat list.
beforeEach(async (ctx) => {
  const fileName = (ctx.task.file?.name ?? "").replace(/\\/g, "/").split("/").pop() ?? "";
  const category = COMPONENT_SPECS.has(fileName)
    ? "React component tests"
    : "React unit tests";
  await parentSuite(category);
  await epic(category);
});

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
