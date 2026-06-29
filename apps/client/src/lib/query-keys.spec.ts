import { describe, it, expect } from "vitest";

import { todoKeys } from "./query-keys";

describe("todoKeys", () => {
  it("all() returns the ['todos'] key array", () => {
    expect(todoKeys.all()).toEqual(["todos"]);
  });

  it("all() returns a new array reference each call (safe for mutation guards)", () => {
    expect(todoKeys.all()).not.toBe(todoKeys.all());
  });
});
