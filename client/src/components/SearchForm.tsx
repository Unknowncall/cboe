import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import type { SearchFormData } from '../hooks/useTrailSearch';

interface SearchFormProps {
	message: string;
	setMessage: (message: string) => void;
	onSubmit: (data: SearchFormData) => void;
	isStreaming: boolean;
	showToolTrace: boolean;
	setShowToolTrace: (show: boolean) => void;
	availableAgents?: any;
	selectedAgent: string;
	setSelectedAgent: (agent: string) => void;
}

const SearchForm: React.FC<SearchFormProps> = ({
	message,
	setMessage,
	onSubmit,
	isStreaming,
	showToolTrace,
	availableAgents,
	selectedAgent,
	setSelectedAgent,
}) => {
	const [query, setQuery] = useState(message);
	const [error, setError] = useState<string>('');

	// Sync with parent message
	useEffect(() => {
		setQuery(message);
	}, [message]);

	// Validate query
	const validateQuery = (value: string): string => {
		if (!value.trim()) {
			return 'Search query is required';
		}
		if (value.trim().length < 3) {
			return 'Search query must be at least 3 characters long';
		}
		if (value.length > 500) {
			return 'Search query must be less than 500 characters';
		}
		return '';
	};

	const handleQueryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		const value = e.target.value;
		setQuery(value);
		setMessage(value);
		setError(validateQuery(value));
	};

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		const validationError = validateQuery(query);
		if (validationError) {
			setError(validationError);
			return;
		}

		onSubmit({
			query: query.trim(),
			showToolTrace,
			agentType: selectedAgent
		});
	};

	const handleKeyDown = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	const exampleQueries = [
		"Easy loop trail under 3 miles with lake views near Chicago",
		"Moderate out and back trail with waterfall and forest features near Chicago",
		"Dog-friendly trail with boardwalk and urban access in Illinois",
		"Short trail under 2 miles with minimal elevation gain for families",
		"Prairie trail with wildflowers and hills near Chicago suburbs"
	];

	const handleExampleClick = (example: string) => {
		setQuery(example);
		setMessage(example);
		setError('');
	};

	const isValid = query.trim().length >= 3 && query.length <= 500;

	return (
		<div className="mb-8">
			<form onSubmit={handleSubmit}>
				<div className="flex flex-col gap-4">
					<div>
						<label htmlFor="search-query" className="sr-only">
							Trail search query
						</label>
						<textarea
							id="search-query"
							value={query}
							onChange={handleQueryChange}
							onKeyDown={handleKeyDown}
							placeholder="Try: Easy loop under 8 km with waterfall near Chicago"
							className={`w-full p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${error ? 'border-red-500' : 'border-gray-300'
								}`}
							rows={3}
							disabled={isStreaming}
							aria-label="Trail search query"
							aria-describedby={error ? "search-error" : "search-help"}
							aria-required="true"
							role="textbox"
							aria-invalid={error ? 'true' : 'false'}
						/>
						{error && (
							<div id="search-error" className="mt-1 text-sm text-red-600" role="alert">
								{error}
							</div>
						)}
						<div id="search-help" className="sr-only">
							Enter your trail search criteria. Press Enter to search, Shift+Enter for new line.
						</div>
					</div>

					{/* Agent Selection */}
					<div className="flex items-center gap-4">
						<label htmlFor="agent-select" className="text-sm font-medium text-gray-700">
							AI Agent:
						</label>
						<select
							id="agent-select"
							value={selectedAgent}
							onChange={(e) => setSelectedAgent(e.target.value)}
							disabled={isStreaming}
							className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
							aria-label="Select AI agent type"
						>
							<option value="custom">Custom Agent</option>
							<option value="langchain">LangChain Agent</option>
						</select>
						<span className="text-xs text-gray-500">
							{selectedAgent === 'custom' ? 'Fast, direct OpenAI implementation' : 'Framework-based with memory'}
						</span>
					</div>

					<div className="w-full">
						<Button
							type="submit"
							disabled={!isValid || isStreaming}
							className="px-6 py-2 w-full"
							variant="outline"
							aria-describedby={isStreaming ? "search-status" : undefined}
						>
							{isStreaming ? 'Searching...' : 'Search'}
						</Button>
						{isStreaming && (
							<div id="search-status" className="sr-only" aria-live="polite">
								Search in progress
							</div>
						)}
					</div>
				</div>
			</form>

			{/* Example queries section */}
			<div className="mt-4">
				<h3 className="text-sm font-medium text-gray-700 mb-2">Try these examples:</h3>
				<div className="flex flex-wrap gap-2">
					{exampleQueries.map((example, index) => (
						<button
							key={index}
							type="button"
							onClick={() => handleExampleClick(example)}
							disabled={isStreaming}
							className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full border border-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							aria-label={`Use example query: ${example}`}
						>
							{example}
						</button>
					))}
				</div>
			</div>
		</div>
	);
};

export default SearchForm;
