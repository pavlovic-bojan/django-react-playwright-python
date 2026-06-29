import { describe, it, expect } from "vitest";

import { cn } from "./utils";

describe("cn", () => {
  it("joins class names with a space", () => {
    expect(cn("a", "b", "c")).toBe("a b c");
  });

  it("skips falsy values (undefined, null, false)", () => {
    // Pass falsy values directly — clsx/twMerge silently drops them.
    expect(cn("a", undefined, null, false, "c")).toBe("a c");
  });

  it("resolves Tailwind conflicts — last class wins", () => {
    // tailwind-merge removes the earlier conflicting utility.
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("handles an empty call", () => {
    expect(cn()).toBe("");
  });

  it("handles an array of class names", () => {
    expect(cn(["a", "b"])).toBe("a b");
  });
});
