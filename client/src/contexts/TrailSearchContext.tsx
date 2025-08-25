import React, { createContext, useContext, ReactNode } from 'react';
import { useTrailSearch } from '../hooks/useTrailSearch';
import type { Trail, ParsedFilters, ToolTrace } from '../types';

// Define the context type
interface TrailSearchContextType {
	// State
	message: string;
	setMessage: (message: string) => void;
	streamContent: string;
	trails: Trail[];
	parsedFilters: ParsedFilters | null;
	toolTraces: ToolTrace[];
	showToolTrace: boolean;
	setShowToolTrace: (show: boolean) => void;
	isStreaming: boolean;
	requestId: string | null;
	expandedTrails: Set<number>;
	trailDetails: Map<number, any>;
	availableAgents: any;
	setAvailableAgents: (agents: any) => void;
	selectedAgent: string;
	setSelectedAgent: (agent: string) => void;

	// Actions
	handleSubmit: (data: any) => Promise<void>;
	toggleTrailDetails: (trail: Trail) => Promise<void>;
	cancelStreaming: () => void;
}

// Create the context
const TrailSearchContext = createContext<TrailSearchContextType | null>(null);

// Provider component
interface TrailSearchProviderProps {
	children: ReactNode;
}

export const TrailSearchProvider: React.FC<TrailSearchProviderProps> = ({ children }) => {
	const searchState = useTrailSearch();

	return (
		<TrailSearchContext.Provider value={searchState}>
			{children}
		</TrailSearchContext.Provider>
	);
};

// Custom hook to use the context
export const useTrailSearchContext = (): TrailSearchContextType => {
	const context = useContext(TrailSearchContext);

	if (!context) {
		throw new Error('useTrailSearchContext must be used within a TrailSearchProvider');
	}

	return context;
};

// HOC for components that need trail search state
export const withTrailSearch = <P extends object>(
	Component: React.ComponentType<P>
) => {
	const WrappedComponent = (props: P) => (
		<TrailSearchProvider>
			<Component {...props} />
		</TrailSearchProvider>
	);

	WrappedComponent.displayName = `withTrailSearch(${Component.displayName || Component.name})`;

	return WrappedComponent;
};
