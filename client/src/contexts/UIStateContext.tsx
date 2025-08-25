import React, { createContext, useContext, ReactNode, useCallback, useState } from 'react';

// UI state context - loading states and user interactions  
interface UIStateContextType {
	isStreaming: boolean;
	setIsStreaming: (isStreaming: boolean) => void;
	availableAgents: any;
	setAvailableAgents: (agents: any) => void;
}

const UIStateContext = createContext<UIStateContextType | null>(null);

interface UIStateProviderProps {
	children: ReactNode;
}

export const UIStateProvider: React.FC<UIStateProviderProps> = ({ children }) => {
	const [isStreaming, setIsStreaming] = useState(false);
	const [availableAgents, setAvailableAgents] = useState<any>(null);

	// Memoize callbacks
	const setIsStreamingCallback = useCallback((isStreaming: boolean) => setIsStreaming(isStreaming), []);
	const setAvailableAgentsCallback = useCallback((agents: any) => setAvailableAgents(agents), []);

	const value: UIStateContextType = {
		isStreaming,
		setIsStreaming: setIsStreamingCallback,
		availableAgents,
		setAvailableAgents: setAvailableAgentsCallback,
	};

	return (
		<UIStateContext.Provider value={value}>
			{children}
		</UIStateContext.Provider>
	);
};

export const useUIState = (): UIStateContextType => {
	const context = useContext(UIStateContext);
	if (!context) {
		throw new Error('useUIState must be used within a UIStateProvider');
	}
	return context;
};
