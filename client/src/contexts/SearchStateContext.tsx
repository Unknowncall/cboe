import React, { createContext, useContext, ReactNode, useState, useCallback } from 'react';

// Search state context - only search-related state
interface SearchStateContextType {
	message: string;
	setMessage: (message: string) => void;
	selectedAgent: string;
	setSelectedAgent: (agent: string) => void;
	showToolTrace: boolean;
	setShowToolTrace: (show: boolean) => void;
}

const SearchStateContext = createContext<SearchStateContextType | null>(null);

interface SearchStateProviderProps {
	children: ReactNode;
}

export const SearchStateProvider: React.FC<SearchStateProviderProps> = ({ children }) => {
	const [message, setMessage] = useState('');
	const [selectedAgent, setSelectedAgent] = useState('custom');
	const [showToolTrace, setShowToolTrace] = useState(false);

	// Memoize callbacks to prevent unnecessary re-renders
	const setMessageCallback = useCallback((message: string) => setMessage(message), []);
	const setSelectedAgentCallback = useCallback((agent: string) => setSelectedAgent(agent), []);
	const setShowToolTraceCallback = useCallback((show: boolean) => setShowToolTrace(show), []);

	const value: SearchStateContextType = {
		message,
		setMessage: setMessageCallback,
		selectedAgent,
		setSelectedAgent: setSelectedAgentCallback,
		showToolTrace,
		setShowToolTrace: setShowToolTraceCallback,
	};

	return (
		<SearchStateContext.Provider value={value}>
			{children}
		</SearchStateContext.Provider>
	);
};

export const useSearchState = (): SearchStateContextType => {
	const context = useContext(SearchStateContext);
	if (!context) {
		throw new Error('useSearchState must be used within a SearchStateProvider');
	}
	return context;
};
