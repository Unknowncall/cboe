import React, { ReactNode } from 'react';
import { SearchStateProvider } from './SearchStateContext';
import { ResultsProvider } from './ResultsContext';
import { UIStateProvider } from './UIStateContext';

interface CombinedProviderProps {
	children: ReactNode;
}

export const CombinedTrailSearchProvider: React.FC<CombinedProviderProps> = ({ children }) => {
	return (
		<SearchStateProvider>
			<ResultsProvider>
				<UIStateProvider>
					{children}
				</UIStateProvider>
			</ResultsProvider>
		</SearchStateProvider>
	);
};

// Export individual hooks for components to use
export { useSearchState } from './SearchStateContext';
export { useResults } from './ResultsContext';
export { useUIState } from './UIStateContext';
