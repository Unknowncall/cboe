import Header from './components/Header';
import Footer from './components/Footer';
import SearchForm from './components/SearchForm';
import StreamingPanel from './components/StreamingPanel';
import ToolTrace from './components/ToolTrace';
import TrailList from './components/TrailList';
import ErrorBoundary from './components/ErrorBoundary';
import { useTrailSearch } from './hooks/useTrailSearch';
import './App.css';

function App() {
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

	return (
		<ErrorBoundary>
			<div className="min-h-screen p-4">
				<div className="max-w-4xl mx-auto">
					<Header />

					<SearchForm
						message={message}
						setMessage={setMessage}
						onSubmit={handleSubmit}
						isStreaming={isStreaming}
						showToolTrace={showToolTrace}
						setShowToolTrace={setShowToolTrace}
						availableAgents={availableAgents}
						selectedAgent={selectedAgent}
						setSelectedAgent={setSelectedAgent}
					/>

					{/* Request ID */}
					{requestId && (
						<div className="mb-4 text-sm text-gray-500">
							Request ID: {requestId}
						</div>
					)}

					<StreamingPanel
						streamContent={streamContent}
						isStreaming={isStreaming}
						onCancel={cancelStreaming}
					/>

					<ToolTrace toolTraces={toolTraces} showToolTrace={showToolTrace} />

					<TrailList
						trails={trails}
					/>

					<Footer />
				</div>
			</div>
		</ErrorBoundary>
	);
}

export default App;
