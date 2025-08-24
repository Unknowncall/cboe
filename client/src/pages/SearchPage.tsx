import React, { useRef } from 'react';
import SearchForm from '../components/SearchForm';
import StreamingPanel from '../components/StreamingPanel';
import ToolTrace from '../components/ToolTrace';
import TrailList from '../components/TrailList';
import SEOHead from '../components/SEOHead';
import { useTrailSearch } from '../hooks/useTrailSearch';
import { Search } from 'lucide-react';

const SearchPage: React.FC = () => {
	const {
		message,
		setMessage,
		streamContent,
		trails,
		toolTraces,
		showToolTrace,
		setShowToolTrace,
		isStreaming,
		requestId,
		availableAgents,
		selectedAgent,
		setSelectedAgent,
		handleSubmit,
		cancelStreaming,
	} = useTrailSearch();

	const streamingPanelRef = useRef<HTMLDivElement>(null);

	const scrollToResults = () => {
		setTimeout(() => {
			streamingPanelRef.current?.scrollIntoView({
				behavior: 'smooth',
				block: 'start',
				inline: 'nearest'
			});
		}, 100);
	};

	const handleSearchSubmit = (data: any) => {
		handleSubmit(data);
		scrollToResults();
	};

	return (
		<>
			<SEOHead
				title="Search Trails - Chicago Trail Explorer"
				description="Find your perfect hiking trail in Chicago. Use our AI-powered search to discover trails that match your preferences for difficulty, distance, and features."
				canonicalUrl="https://chicago-trail-explorer.com/search"
			/>
			<div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50 relative overflow-hidden">
				{/* Background decorative elements */}
				<div className="absolute inset-0 overflow-hidden pointer-events-none">
					<div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-green-200/20 to-transparent rounded-full blur-3xl"></div>
					<div className="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-tr from-blue-200/20 to-transparent rounded-full blur-3xl"></div>
					<div className="absolute top-1/3 left-1/2 w-64 h-64 bg-gradient-to-br from-purple-200/15 to-transparent rounded-full blur-2xl"></div>
				</div>

				<div className="relative z-10 w-full min-h-screen">
					<div className="w-full max-w-7xl mx-auto px-4 py-8">
						{/* Page Header */}
						<div className="text-center mb-12">
							<div className="flex items-center justify-center mb-4">
								<div className="p-3 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full shadow-lg">
									<Search className="h-8 w-8 text-white" />
								</div>
							</div>
							<h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
								Find Your Perfect Trail
							</h1>
							<p className="text-xl text-gray-700 max-w-3xl mx-auto">
								Describe your ideal hiking experience and let our AI find the perfect trails for you
							</p>
						</div>

						<SearchForm
							message={message}
							setMessage={setMessage}
							onSubmit={handleSearchSubmit}
							isStreaming={isStreaming}
							showToolTrace={showToolTrace}
							setShowToolTrace={setShowToolTrace}
							availableAgents={availableAgents}
							selectedAgent={selectedAgent}
							setSelectedAgent={setSelectedAgent}
						/>

						{/* Request ID */}
						{requestId && (
							<div className="mb-4 text-sm text-gray-500 text-center">
								Request ID: {requestId}
							</div>
						)}

						<div ref={streamingPanelRef}>
							<StreamingPanel
								streamContent={streamContent}
								isStreaming={isStreaming}
								onCancel={cancelStreaming}
							/>
						</div>

						<ToolTrace toolTraces={toolTraces} showToolTrace={showToolTrace} />

						<TrailList trails={trails} />
					</div>
				</div>
			</div>
		</>
	);
};

export default SearchPage;
