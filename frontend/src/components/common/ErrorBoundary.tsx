import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Unhandled error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950 p-8 text-white">
          <div className="max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
            <h2 className="text-xl font-semibold">Something went wrong</h2>
            <p className="mt-3 text-sm text-slate-400">
              The application hit an unexpected error. Please refresh and try again.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
