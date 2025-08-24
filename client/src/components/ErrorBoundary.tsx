import React, { Component, ReactNode } from 'react';

interface Props {
	children: ReactNode;
	fallback?: ReactNode;
}

interface State {
	hasError: boolean;
	error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
	constructor(props: Props) {
		super(props);
		this.state = { hasError: false };
	}

	static getDerivedStateFromError(error: Error): State {
		return { hasError: true, error };
	}

	componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		console.error('Error caught by boundary:', error, errorInfo);
	}

	render() {
		if (this.state.hasError) {
			return this.props.fallback || (
				<div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
					<div className="max-w-md w-full bg-white rounded-lg shadow-md p-6 text-center">
						<div className="text-red-500 text-6xl mb-4">⚠️</div>
						<h2 className="text-2xl font-bold text-gray-900 mb-2">
							Something went wrong
						</h2>
						<p className="text-gray-600 mb-4">
							We encountered an unexpected error. Please refresh the page to try again.
						</p>
						<button
							onClick={() => window.location.reload()}
							className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
						>
							Refresh Page
						</button>
					</div>
				</div>
			);
		}

		return this.props.children;
	}
}

export default ErrorBoundary;
