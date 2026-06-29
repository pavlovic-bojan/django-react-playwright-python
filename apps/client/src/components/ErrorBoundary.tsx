import { Component, type ReactNode, type ErrorInfo } from "react";

interface Props {
  children: ReactNode;
  /**
   * Custom fallback rendered when an unhandled render error is caught.
   * Defaults to a generic message with a "Try again" button.
   */
  fallback?: ReactNode;
}

interface State {
  readonly hasError: boolean;
  readonly error: Error | null;
}

/**
 * Catches unhandled React render errors and presents a fallback UI.
 * Place near the root of the component tree (wrapping `<App />`).
 *
 * In production, replace the `console.error` inside `componentDidCatch`
 * with a call to your error-tracking service (e.g. Sentry).
 */
export class ErrorBoundary extends Component<Props, State> {
  override state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    // Replace with error-tracking service call in production.
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  private handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  override render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div
            role="alert"
            className="flex flex-col items-center gap-4 p-8 text-center"
          >
            <p className="text-destructive">
              Something went wrong. Please try again.
            </p>
            <button
              type="button"
              onClick={this.handleReset}
              className="font-medium underline underline-offset-4"
            >
              Try again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
