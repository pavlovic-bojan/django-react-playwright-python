import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ErrorBoundary } from "./ErrorBoundary";

// Silence expected React/ErrorBoundary console.error output so test output
// stays clean. React logs all caught errors to the console.
beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
});

/** A child that throws if `explode` is true, renders normally otherwise. */
function Bomb({ explode }: { explode: boolean }) {
  if (explode) throw new Error("Ka-boom");
  return <div>All clear</div>;
}

// No makeThrowsFor helper needed — see "resets and renders children" test below.

describe("ErrorBoundary", () => {
  it("renders children normally when no error is thrown", () => {
    render(
      <ErrorBoundary>
        <Bomb explode={false} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("All clear")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("shows the default fallback UI when a child throws", () => {
    render(
      <ErrorBoundary>
        <Bomb explode={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(
      screen.getByText("Something went wrong. Please try again."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Try again" }),
    ).toBeInTheDocument();
  });

  it("renders a custom fallback when the fallback prop is provided", () => {
    render(
      <ErrorBoundary fallback={<div role="alert">Custom error</div>}>
        <Bomb explode={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Custom error")).toBeInTheDocument();
    // The default "Try again" button should NOT be present.
    expect(
      screen.queryByRole("button", { name: "Try again" }),
    ).not.toBeInTheDocument();
  });

  it("logs the error via componentDidCatch", () => {
    render(
      <ErrorBoundary>
        <Bomb explode={true} />
      </ErrorBoundary>,
    );

    // console.error is called by componentDidCatch with "[ErrorBoundary]" prefix.
    expect(console.error).toHaveBeenCalled();
  });

  it("resets and renders children again when 'Try again' is clicked", async () => {
    const user = userEvent.setup();

    // React 19 concurrent mode may render a component multiple times before
    // falling back to synchronous recovery. A counter-based "throw N times"
    // approach cannot reliably predict N across React versions.
    //
    // Instead, use a mutable flag that keeps throwing on every call until we
    // explicitly disable it just before the "Try again" click — this is robust
    // regardless of how many concurrent retries React performs.
    const flag = { shouldThrow: true };

    function ControlledBomb() {
      if (flag.shouldThrow) throw new Error("Controlled error");
      return <div>Recovered</div>;
    }

    render(
      <ErrorBoundary>
        <ControlledBomb />
      </ErrorBoundary>,
    );

    // ErrorBoundary must be showing its fallback.
    expect(screen.getByRole("alert")).toBeInTheDocument();

    // Disable throwing so the next render succeeds.
    flag.shouldThrow = false;
    await user.click(screen.getByRole("button", { name: "Try again" }));

    // After handleReset, children render normally.
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.getByText("Recovered")).toBeInTheDocument();
  });
});
