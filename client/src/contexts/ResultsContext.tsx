import React, { createContext, useContext, ReactNode, useState, useRef, useEffect, useCallback } from 'react';
import type { Trail, ParsedFilters, ToolTrace, TrailDetails, StreamEvent } from '../types';
import type { SearchFormData } from '../schemas';
import { STREAM_TIMEOUT_MS } from '../constants/validation';

// Results context - only search results and streaming content
interface ResultsContextType {
	streamContent: string;
	setStreamContent: (content: string | ((prev: string) => string)) => void;
	trails: Trail[];
	setTrails: (trails: Trail[]) => void;
	parsedFilters: ParsedFilters | null;
	setParsedFilters: (filters: ParsedFilters | null) => void;
	toolTraces: ToolTrace[];
	setToolTraces: (traces: ToolTrace[] | ((prev: ToolTrace[]) => ToolTrace[])) => void;
	requestId: string | null;
	setRequestId: (id: string | null) => void;
	expandedTrails: Set<number>;
	trailDetails: Map<number, any>;
	toggleTrailDetails: (trail: Trail) => Promise<void>;
	handleSubmit: (data: SearchFormData) => Promise<void>;
	cancelStreaming: () => void;
	isStreaming: boolean;
}

const ResultsContext = createContext<ResultsContextType | null>(null);

interface ResultsProviderProps {
	children: ReactNode;
}

export const ResultsProvider: React.FC<ResultsProviderProps> = ({ children }) => {
	const [streamContent, setStreamContent] = useState('');
	const [trails, setTrails] = useState<Trail[]>([]);
	const [parsedFilters, setParsedFilters] = useState<ParsedFilters | null>(null);
	const [toolTraces, setToolTraces] = useState<ToolTrace[]>([]);
	const [requestId, setRequestId] = useState<string | null>(null);
	const [expandedTrails, setExpandedTrails] = useState<Set<number>>(new Set());
	const [trailDetails, setTrailDetails] = useState<Map<number, TrailDetails>>(new Map());
	const [isStreaming, setIsStreaming] = useState(false);

	const abortControllerRef = useRef<AbortController | null>(null);

	// Cleanup AbortController on unmount to prevent memory leaks
	useEffect(() => {
		return () => {
			if (abortControllerRef.current) {
				abortControllerRef.current.abort();
			}
		};
	}, []); // No dependencies - stable cleanup

	const handleSubmit = useCallback(async (data: SearchFormData) => {
		if (!data.query.trim() || isStreaming) return;

		// Clear previous results
		setStreamContent('');
		setTrails([]);
		setParsedFilters(null);
		setToolTraces([]);
		setRequestId(null);
		setIsStreaming(true);

		// Cancel previous request if exists
		if (abortControllerRef.current) {
			abortControllerRef.current.abort();
		}

		// Create AbortController for timeout
		const controller = new AbortController();
		abortControllerRef.current = controller;
		const timeoutId = setTimeout(() => controller.abort(), STREAM_TIMEOUT_MS);

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

			// Helper function to process stream chunks
			const processStreamChunk = (chunk: string) => {
				const lines = chunk.split('\n');
				for (const line of lines) {
					if (line.startsWith('data: ')) {
						try {
							const data: StreamEvent = JSON.parse(line.substring(6));
							handleStreamEvent(data);
						} catch (parseError) {
							console.error('Failed to parse SSE data:', parseError, 'Raw line:', line);
							// Continue processing other lines instead of breaking
							continue;
						}
					}
				}
			};

			// Helper function to handle stream events
			const handleStreamEvent = (data: StreamEvent) => {
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
					abortControllerRef.current = null;
				}
			};

			// Process stream without arbitrary iteration limits
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value);
				processStreamChunk(chunk);
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
			abortControllerRef.current = null;
		}
	}, [isStreaming, setIsStreaming]);

	const cancelStreaming = useCallback(() => {
		if (abortControllerRef.current) {
			abortControllerRef.current.abort();
			abortControllerRef.current = null;
			setIsStreaming(false);
			setStreamContent(prev => prev + '\n\n[Request cancelled by user]');
		}
	}, [setIsStreaming]);

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

	const value: ResultsContextType = {
		streamContent,
		setStreamContent,
		trails,
		setTrails,
		parsedFilters,
		setParsedFilters,
		toolTraces,
		setToolTraces,
		requestId,
		setRequestId,
		expandedTrails,
		trailDetails,
		toggleTrailDetails,
		handleSubmit,
		cancelStreaming,
		isStreaming,
	};

	return (
		<ResultsContext.Provider value={value}>
			{children}
		</ResultsContext.Provider>
	);
};

export const useResults = (): ResultsContextType => {
	const context = useContext(ResultsContext);
	if (!context) {
		throw new Error('useResults must be used within a ResultsProvider');
	}
	return context;
};
