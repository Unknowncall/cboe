import { useState } from 'react';
import type { Trail, ParsedFilters, ToolTrace, StreamEvent, TrailDetails } from '../types';

// Type for form data from SearchForm
export interface SearchFormData {
	query: string;
	showToolTrace: boolean;
	agentType: string;
}

export const useTrailSearch = () => {
	const [message, setMessage] = useState('');
	const [streamContent, setStreamContent] = useState('');
	const [trails, setTrails] = useState<Trail[]>([]);
	const [parsedFilters, setParsedFilters] = useState<ParsedFilters | null>(null);
	const [toolTraces, setToolTraces] = useState<ToolTrace[]>([]);
	const [showToolTrace, setShowToolTrace] = useState(false);
	const [isStreaming, setIsStreaming] = useState(false);
	const [requestId, setRequestId] = useState<string | null>(null);
	const [expandedTrails, setExpandedTrails] = useState<Set<number>>(new Set());
	const [trailDetails, setTrailDetails] = useState<Map<number, TrailDetails>>(new Map());
	const [availableAgents, setAvailableAgents] = useState<any>(null);
	const [selectedAgent, setSelectedAgent] = useState('custom');
	const [abortController, setAbortController] = useState<AbortController | null>(null);

	const handleSubmit = async (data: SearchFormData) => {
		if (!data.query.trim() || isStreaming) return;

		// Update state from form data
		setMessage(data.query);
		setShowToolTrace(data.showToolTrace);

		// Clear previous results
		setStreamContent('');
		setTrails([]);
		setParsedFilters(null);
		setToolTraces([]);
		setRequestId(null);
		setIsStreaming(true);

		// Create AbortController for timeout
		const controller = new AbortController();
		setAbortController(controller);
		const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

		try {
			const response = await fetch('/api/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					message: data.query,
					agent_type: data.agentType
				}),
				signal: controller.signal
			});

			clearTimeout(timeoutId);

			if (!response.body) {
				throw new Error('No response body');
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value);
				const lines = chunk.split('\n');

				for (const line of lines) {
					if (line.startsWith('data: ')) {
						try {
							const data: StreamEvent = JSON.parse(line.substring(6));

							if (data.type === 'start') {
								setRequestId(data.request_id || null);
							} else if (data.type === 'token') {
								setStreamContent(prev => prev + (data.content || ''));
							} else if (data.type === 'tool_trace') {
								// Handle real-time tool trace updates
								if (data.tool_trace) {
									const trace = data.tool_trace;
									setToolTraces(prev => [...prev, trace]);
								}
							} else if (data.type === 'done') {
								setTrails(data.results || []);
								setParsedFilters(data.parsed_filters || null);
								// Keep accumulated tool traces from streaming, but merge with final ones if provided
								if (data.tool_traces && data.tool_traces.length > 0) {
									setToolTraces(data.tool_traces);
								}
								setIsStreaming(false);
								setAbortController(null);
							}
						} catch (parseError) {
							console.error('Failed to parse SSE data:', parseError, 'Raw line:', line);
							// Continue processing other lines instead of breaking
							continue;
						}
					}
				}
			}
		} catch (error) {
			clearTimeout(timeoutId);
			console.error('Error:', error);

			if (error instanceof Error && error.name === 'AbortError') {
				setStreamContent('Request timed out. Please try again.');
			} else {
				setStreamContent('Error connecting to server. Please try again.');
			}
			setIsStreaming(false);
			setAbortController(null);
		}
	};

	const cancelStreaming = () => {
		if (abortController) {
			abortController.abort();
			setAbortController(null);
			setIsStreaming(false);
			setStreamContent(prev => prev + '\n\n[Request cancelled by user]');
		}
	};

	const toggleTrailDetails = async (trail: Trail) => {
		if (expandedTrails.has(trail.id)) {
			setExpandedTrails(prev => {
				const newSet = new Set(prev);
				newSet.delete(trail.id);
				return newSet;
			});
		} else {
			// Fetch details if not already loaded
			if (!trailDetails.has(trail.id)) {
				try {
					const response = await fetch(`/api/trail/${trail.id}`);
					if (response.ok) {
						const details: TrailDetails = await response.json();
						setTrailDetails(prev => new Map(prev).set(trail.id, details));
					}
				} catch (error) {
					console.error('Error fetching trail details:', error);
				}
			}

			setExpandedTrails(prev => new Set(prev).add(trail.id));
		}
	};

	return {
		message,
		setMessage,
		streamContent,
		trails,
		parsedFilters,
		toolTraces,
		showToolTrace,
		setShowToolTrace,
		isStreaming,
		requestId,
		expandedTrails,
		trailDetails,
		availableAgents,
		setAvailableAgents,
		selectedAgent,
		setSelectedAgent,
		handleSubmit,
		toggleTrailDetails,
		cancelStreaming,
	};
};
