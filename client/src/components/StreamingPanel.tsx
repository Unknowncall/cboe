import React, { useRef, useEffect } from 'react';

interface StreamingPanelProps {
	streamContent: string;
	isStreaming: boolean;
	onCancel?: () => void;
}

const StreamingPanel: React.FC<StreamingPanelProps> = ({ streamContent, isStreaming, onCancel }) => {
	const streamPanelRef = useRef<HTMLDivElement>(null);

	// Auto-scroll to bottom when content updates
	useEffect(() => {
		if (streamPanelRef.current) {
			streamPanelRef.current.scrollTop = streamPanelRef.current.scrollHeight;
		}
	}, [streamContent]);

	if (!streamContent && !isStreaming) {
		return null;
	}

	return (
		<div className="mb-8">
			<div
				ref={streamPanelRef}
				className="relative bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/40 rounded-2xl border border-blue-100/60 shadow-lg shadow-blue-100/25 p-5 max-h-96 overflow-y-auto backdrop-blur-sm"
				aria-live="polite"
				aria-label="AI Agent response"
			>
				{/* Header with AI icon */}
				<div className="flex items-start gap-3 mb-2">
					<div className="relative mt-0.5">
						{/* AI Icon - simplified */}
						<div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center shadow-md">
							<svg
								className="w-4 h-4 text-white"
								viewBox="0 0 24 24"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M9.5 2A1.5 1.5 0 0 0 8 3.5v1A1.5 1.5 0 0 0 9.5 6h5A1.5 1.5 0 0 0 16 4.5v-1A1.5 1.5 0 0 0 14.5 2h-5ZM6.5 6A1.5 1.5 0 0 0 5 7.5V20a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7.5A1.5 1.5 0 0 0 17.5 6h-11ZM9 11a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm6-1a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-3 5a3 3 0 0 1-3-3h6a3 3 0 0 1-3 3Z"
									fill="currentColor"
								/>
							</svg>
						</div>
						{/* Streaming indicator */}
						{isStreaming && (
							<div className="absolute -inset-0.5 bg-blue-400/30 rounded-lg animate-pulse" />
						)}
					</div>

					<div className="flex-1 min-w-0">
						<div className="flex items-center justify-between">
							<h2 className="text-lg font-semibold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
								AI Trail Assistant
							</h2>
							<div className="flex items-center gap-2 ml-4">
								{isStreaming ? (
									<>
										<div className="flex gap-1">
											<div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0ms]" />
											<div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:150ms]" />
											<div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:300ms]" />
										</div>
										<span className="text-xs text-blue-600 font-medium whitespace-nowrap">Analyzing trails...</span>
										{onCancel && (
											<button
												onClick={onCancel}
												className="ml-2 px-2 py-1 text-xs bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-md transition-colors duration-150 flex items-center gap-1"
												aria-label="Cancel streaming request"
											>
												<svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
													<path d="M6 6L18 18M6 18L18 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
												</svg>
												Stop
											</button>
										)}
									</>
								) : (
									<>
										<div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
										<span className="text-xs text-emerald-600 font-medium whitespace-nowrap">Analysis complete</span>
									</>
								)}
							</div>
						</div>
					</div>
				</div>

				{/* Content area */}
				<div className="relative">
					<div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
						{streamContent}
						{isStreaming && (
							<span className="inline-flex items-center ml-1">
								<span className="w-0.5 h-4 bg-blue-500 animate-pulse rounded-full" />
							</span>
						)}
					</div>
				</div>
			</div>
		</div>
	);
};

export default StreamingPanel;
