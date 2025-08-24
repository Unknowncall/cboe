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
		"Free trails with parking and restrooms in Illinois",
		"Paved trails that are wheelchair accessible with no entry fees",
		"Dog-friendly trails with camping available in state parks",
		"Trails managed by National Park Service with water fountains",
		"Moderate trails with picnic areas and year-round access",
		"Boardwalk trails with beach access and free parking",
		"Loop trails under 5 miles in Cook County with restrooms",
		"Hard difficulty trails in Wisconsin state parks",
		"Trails that cost money but have good amenities near Chicago"
	];

	const handleExampleClick = (example: string) => {
		setQuery(example);
		setMessage(example);
		setError('');
	};

	const isValid = query.trim().length >= 3 && query.length <= 500;

	return (
		<div className="mb-12">
			{/* Main search container */}
			<div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
				<form onSubmit={handleSubmit}>
					<div className="flex flex-col gap-6">
						<div>
							<label htmlFor="search-query" className="block text-lg font-semibold text-gray-800 mb-3">
								🔍 What kind of trail adventure are you looking for?
							</label>
							<div className="relative">
								<textarea
									id="search-query"
									value={query}
									onChange={handleQueryChange}
									onKeyDown={handleKeyDown}
									placeholder="Try: Easy loop under 8 miles with waterfall near Chicago, or family-friendly trails with picnic areas..."
									className={`w-full p-5 border-2 rounded-xl resize-none transition-all duration-200 text-lg leading-relaxed placeholder:text-gray-400 focus:ring-4 focus:ring-emerald-500/20 focus:border-emerald-500 focus:outline-none ${error ? 'border-red-400 bg-red-50/50' : 'border-gray-200 bg-white/50 hover:border-gray-300'
										}`}
									rows={4}
									disabled={isStreaming}
									aria-label="Trail search query"
									aria-describedby={error ? "search-error" : "search-help"}
									aria-required="true"
									role="textbox"
									aria-invalid={error ? 'true' : 'false'}
								/>
								{/* Character count */}
								<div className="absolute bottom-3 right-3 text-xs text-gray-400">
									{query.length}/500
								</div>
							</div>
							{error && (
								<div id="search-error" className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg border border-red-200" role="alert">
									⚠️ {error}
								</div>
							)}
							<div id="search-help" className="sr-only">
								Enter your trail search criteria. Press Enter to search, Shift+Enter for new line.
							</div>
						</div>

						{/* Agent Selection */}
						<div className="flex items-center justify-between p-4 bg-gray-50/50 rounded-xl border border-gray-200">
							<div className="flex items-center gap-4">
								<label htmlFor="agent-select" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
									🤖 AI Assistant:
								</label>
								<select
									id="agent-select"
									value={selectedAgent}
									onChange={(e) => setSelectedAgent(e.target.value)}
									disabled={isStreaming}
									className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none disabled:opacity-50 transition-all duration-200"
									aria-label="Select AI agent type"
								>
									<option value="custom">⚡ Custom Agent</option>
									<option value="langchain">🧠 LangChain Agent</option>
								</select>
							</div>
							<div className="text-xs text-gray-600 max-w-xs">
								{selectedAgent === 'custom' ? '⚡ Fast, direct OpenAI implementation' : '🧠 Framework-based with memory'}
							</div>
						</div>

						<div className="w-full">
							<Button
								type="submit"
								disabled={!isValid || isStreaming}
								className="px-8 py-4 w-full text-lg font-semibold bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
								variant="outline"
								aria-describedby={isStreaming ? "search-status" : undefined}
							>
								{isStreaming ? (
									<div className="flex items-center gap-3">
										<div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
										Exploring trails...
									</div>
								) : (
									<div className="flex items-center gap-3">
										🥾 Discover Trails
									</div>
								)}
							</Button>
							{isStreaming && (
								<div id="search-status" className="sr-only" aria-live="polite">
									Search in progress
								</div>
							)}
						</div>
					</div>
				</form>
			</div>

			{/* Example queries section */}
			<div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-2xl p-6 border border-emerald-100">
				<h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
					💡 Popular Trail Searches
				</h3>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
					{exampleQueries.map((example, index) => (
						<button
							key={index}
							type="button"
							onClick={() => handleExampleClick(example)}
							disabled={isStreaming}
							className="group px-4 py-3 text-sm text-left bg-white/80 hover:bg-white hover:shadow-md text-gray-700 rounded-xl border border-gray-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:border-emerald-300"
							aria-label={`Use example query: ${example}`}
						>
							<div className="flex items-start gap-2">
								<span className="text-emerald-500 group-hover:text-emerald-600 transition-colors duration-200 mt-0.5">
									🥾
								</span>
								<span className="leading-relaxed group-hover:text-gray-900 transition-colors duration-200">
									{example}
								</span>
							</div>
						</button>
					))}
				</div>
				<p className="text-xs text-gray-600 mt-4 text-center">
					Click any example to get started, or write your own custom search above
				</p>
			</div>
		</div>
	);
};

export default SearchForm;
