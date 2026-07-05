import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex items-center justify-center min-h-[60vh] p-8">
          <div className="max-w-lg w-full rounded-2xl border border-red-200/50 dark:border-red-800/40 bg-red-50/80 dark:bg-red-950/30 backdrop-blur-sm p-6 space-y-4">
            <h2 className="text-lg font-bold text-red-800 dark:text-red-200">Something went wrong</h2>
            <pre className="text-sm text-red-600 dark:text-red-400 whitespace-pre-wrap break-all font-mono bg-red-100/50 dark:bg-red-900/20 rounded-xl p-4 max-h-48 overflow-auto">
              {this.state.error.message}
            </pre>
            <button
              onClick={() => { this.setState({ error: null }); }}
              className="px-4 py-2 text-sm font-semibold text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/40 hover:bg-red-200 dark:hover:bg-red-900/60 rounded-xl transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
