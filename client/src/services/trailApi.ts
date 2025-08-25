import type { Trail, StreamEvent, TrailDetails } from '../types';
import { STREAM_TIMEOUT_MS } from '../constants/validation';

// Response types
export interface SearchResponse {
	results: Trail[];
	parsed_filters?: any;
	tool_traces?: any[];
	request_id?: string;
}

// Custom error classes
export class ApiError extends Error {
	status?: number;
	code?: string;

	constructor(message: string, status?: number, code?: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.code = code;
	}
}

export class ApiTimeoutError extends Error {
	constructor(message = 'Request timed out') {
		super(message);
		this.name = 'ApiTimeoutError';
	}
}

export class ApiNetworkError extends Error {
	constructor(message = 'Network error occurred') {
		super(message);
		this.name = 'ApiNetworkError';
	}
}

// Retry configuration
interface RetryConfig {
	maxRetries: number;
	baseDelay: number;
	maxDelay: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
	maxRetries: 3,
	baseDelay: 1000,
	maxDelay: 5000,
};

// Exponential backoff delay calculation
const calculateDelay = (attempt: number, baseDelay: number, maxDelay: number): number => {
	const delay = baseDelay * Math.pow(2, attempt);
	return Math.min(delay, maxDelay);
};

// Main API service class
export class TrailApiService {
	private baseUrl: string;
	private defaultTimeout: number;

	constructor(baseUrl = '/api', timeout = STREAM_TIMEOUT_MS) {
		this.baseUrl = baseUrl;
		this.defaultTimeout = timeout;
	}

	// Generic fetch with retry logic
	private async fetchWithRetry<T>(
		url: string,
		options: RequestInit,
		retryConfig = DEFAULT_RETRY_CONFIG
	): Promise<T> {
		let lastError: Error | null = null;

		for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
			try {
				const controller = new AbortController();
				const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);

				const response = await fetch(url, {
					...options,
					signal: options.signal || controller.signal,
				});

				clearTimeout(timeoutId);

				if (!response.ok) {
					throw new ApiError(`HTTP ${response.status}: ${response.statusText}`);
				}

				return await response.json();
			} catch (error) {
				lastError = error instanceof Error ? error : new Error('Unknown error');

				// Don't retry on user abort or certain errors
				if (error instanceof Error && error.name === 'AbortError') {
					throw new ApiTimeoutError();
				}

				// Don't retry on the last attempt
				if (attempt === retryConfig.maxRetries) {
					break;
				}

				// Wait before retrying
				const delay = calculateDelay(attempt, retryConfig.baseDelay, retryConfig.maxDelay);
				await new Promise(resolve => setTimeout(resolve, delay));
			}
		}

		throw lastError || new ApiNetworkError();
	}

	// Search with support for both streaming and non-streaming responses
	async searchTrails(
		query: string,
		agentType: string,
		signal?: AbortSignal,
		onData?: (event: StreamEvent) => void
	): Promise<void> {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);

		try {
			const response = await fetch(`${this.baseUrl}/chat`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					message: query,
					agent_type: agentType,
				}),
				signal: signal || controller.signal,
			});

			clearTimeout(timeoutId);

			if (!response.ok) {
				throw new ApiError(`HTTP ${response.status}: ${response.statusText}`);
			}

			// Check if this is a streaming response or a JSON response
			const contentType = response.headers.get('content-type');
			
			if (contentType?.includes('text/plain') || contentType?.includes('text/event-stream')) {
				// Handle streaming response (original behavior)
				if (!response.body) {
					throw new Error('No response body');
				}

				const reader = response.body.getReader();
				const decoder = new TextDecoder();

				let iterations = 0;
				const MAX_ITERATIONS = 1000;

				while (iterations < MAX_ITERATIONS) {
					const { done, value } = await reader.read();
					if (done) break;
					iterations++;

					const chunk = decoder.decode(value);
					const lines = chunk.split('\n');

					for (const line of lines) {
						if (line.startsWith('data: ')) {
							try {
								const data: StreamEvent = JSON.parse(line.substring(6));
								onData?.(data);
							} catch (parseError) {
								console.error('Failed to parse SSE data:', parseError, 'Raw line:', line);
								continue;
							}
						}
					}
				}

				if (iterations >= MAX_ITERATIONS) {
					throw new Error('Stream processing exceeded maximum iterations');
				}
			} else {
				// Handle JSON response (Vercel serverless mode)
				const data = await response.json();
				
				// Simulate streaming by sending events in sequence
				if (data.content) {
					// Send content as tokens
					const words = data.content.split(' ');
					for (let i = 0; i < words.length; i++) {
						await new Promise(resolve => setTimeout(resolve, 50)); // Small delay for UX
						onData?.({
							type: 'token',
							content: words[i] + (i < words.length - 1 ? ' ' : '')
						});
					}
				}
				
				// Send final results
				onData?.(data);
			}
		} catch (error) {
			clearTimeout(timeoutId);

			if (error instanceof Error && error.name === 'AbortError') {
				throw new ApiTimeoutError('Search request timed out');
			}

			throw error;
		}
	}

	// Get trail details
	async getTrailDetails(trailId: number, signal?: AbortSignal): Promise<TrailDetails> {
		return this.fetchWithRetry<TrailDetails>(
			`${this.baseUrl}/trail/${trailId}`,
			{
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
				},
				signal,
			}
		);
	}

	// Get available agents
	async getAvailableAgents(signal?: AbortSignal): Promise<any> {
		return this.fetchWithRetry<any>(
			`${this.baseUrl}/agents`,
			{
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
				},
				signal,
			}
		);
	}

	// Health check
	async healthCheck(signal?: AbortSignal): Promise<{ status: string; timestamp: number }> {
		return this.fetchWithRetry<{ status: string; timestamp: number }>(
			`${this.baseUrl}/health`,
			{
				method: 'GET',
				signal,
			}
		);
	}
}

// Create a singleton instance
export const trailApiService = new TrailApiService();

// Export specific methods for easier imports
export const searchTrails = trailApiService.searchTrails.bind(trailApiService);
export const getTrailDetails = trailApiService.getTrailDetails.bind(trailApiService);
export const getAvailableAgents = trailApiService.getAvailableAgents.bind(trailApiService);
export const healthCheck = trailApiService.healthCheck.bind(trailApiService);
