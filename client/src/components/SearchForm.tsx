import React, { useCallback } from 'react';
import { Button } from './ui/button';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { searchSchema, type SearchFormData } from '../schemas';
import { SEARCH_QUERY_MAX_LENGTH } from '../constants/validation';
import { useSearchState, useResults } from '../contexts';
import ExampleQueries from './ExampleQueries';
import AgentSelector from './AgentSelector';

// Simplified SearchForm without complex sync logic
const SearchForm: React.FC = () => {
	const { message, selectedAgent, setMessage, setSelectedAgent } = useSearchState();
	const { handleSubmit: onSubmit, isStreaming } = useResults();

	const {
		control,
		handleSubmit,
		formState: { errors },
		setValue,
		watch,
		trigger
	} = useForm<SearchFormData>({
		resolver: zodResolver(searchSchema),
		defaultValues: {
			query: message || '',
			showToolTrace: false,
			agentType: selectedAgent
		},
		mode: 'onChange'
	});

	const watchedQuery = watch('query');
	const watchedAgentType = watch('agentType');

	// Memoized callbacks to prevent unnecessary re-renders
	const onFormSubmit = useCallback((data: SearchFormData) => {
		// Update state only on submit
		setMessage(data.query);
		setSelectedAgent(data.agentType);
		onSubmit(data);
	}, [onSubmit, setMessage, setSelectedAgent]);

	const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(onFormSubmit)();
		}
	}, [handleSubmit, onFormSubmit]);

	const handleExampleClick = useCallback((example: string) => {
		setValue('query', example);
		trigger('query'); // Trigger validation
	}, [setValue, trigger]);

	const isValid = watchedQuery && watchedQuery.trim().length >= 3 && !errors.query;

	return (
		<div className="mb-12">
			{/* Main search container */}
			<div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
				<form onSubmit={handleSubmit(onFormSubmit)}>
					<div className="flex flex-col gap-6">
						<div>
							<label htmlFor="search-query" className="block text-lg font-semibold text-gray-800 mb-3">
								🔍 What kind of trail adventure are you looking for?
							</label>
							<div className="relative">
								<Controller
									name="query"
									control={control}
									render={({ field }) => (
										<textarea
											{...field}
											id="search-query"
											onKeyDown={handleKeyDown}
											placeholder="Try: Easy loop under 8 miles with waterfall near Chicago, or family-friendly trails with picnic areas..."
											className={`w-full p-5 border-2 rounded-xl resize-none transition-all duration-200 text-lg leading-relaxed placeholder:text-gray-400 focus:ring-4 focus:ring-emerald-500/20 focus:border-emerald-500 focus:outline-none ${errors.query ? 'border-red-400 bg-red-50/50' : 'border-gray-200 bg-white/50 hover:border-gray-300'
												}`}
											rows={4}
											disabled={isStreaming}
											aria-label="Trail search query"
											aria-describedby={errors.query ? "search-error" : "search-help"}
											aria-required="true"
											role="textbox"
											aria-invalid={errors.query ? 'true' : 'false'}
										/>
									)}
								/>
								{/* Character count */}
								<div className="absolute bottom-3 right-3 text-xs text-gray-400">
									{watchedQuery?.length || 0}/{SEARCH_QUERY_MAX_LENGTH}
								</div>
							</div>
							{errors.query && (
								<div id="search-error" className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg border border-red-200" role="alert">
									⚠️ {errors.query.message}
								</div>
							)}
							<div id="search-help" className="sr-only">
								Enter your trail search criteria. Press Enter to search, Shift+Enter for new line.
							</div>
						</div>

						{/* Agent Selection */}
						<AgentSelector
							control={control}
							isStreaming={isStreaming}
							watchedAgentType={watchedAgentType}
						/>

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
			<ExampleQueries onExampleClick={handleExampleClick} disabled={isStreaming} />
		</div>
	);
};

export default SearchForm;
