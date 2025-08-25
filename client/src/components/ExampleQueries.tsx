import React from 'react';

interface ExampleQueriesProps {
	onExampleClick: (query: string) => void;
	disabled: boolean;
}

const ExampleQueries: React.FC<ExampleQueriesProps> = ({ onExampleClick, disabled }) => {
	const exampleQueries = [
		"Easy loop trail under 3 miles with lake views near Chicago",
		"Free trails with parking and restrooms in Illinois",
		"Paved trails that are wheelchair accessible with no entry fees",
		"Dog-friendly trails with camping available in state parks",
		"Trails managed by National Park Service with water fountains",
		"Moderate trails with picnic areas and year-round access",
		"Loop trails under 5 miles in Cook County with restrooms",
		"Hard difficulty trails in Wisconsin state parks",
		"Trails that cost money but have good amenities near Chicago",
		"A long scenic trail in Wisconsin",
	];

	return (
		<div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-2xl p-6 border border-emerald-100">
			<h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
				💡 Popular Trail Searches
			</h3>
			<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
				{exampleQueries.map((example, index) => (
					<button
						key={index}
						type="button"
						onClick={() => onExampleClick(example)}
						disabled={disabled}
						className="group px-4 py-3 text-sm text-left bg-white/80 hover:bg-white hover:shadow-md text-gray-700 rounded-xl border border-gray-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:border-emerald-300"
						aria-label={`Use example query: ${example}`}
					>
						<div className="flex items-start gap-2">
							<span className="text-emerald-500 group-hover:text-emerald-600 transition-colors duration-200 mt-0.5">
								🥾
							</span>
							<span className="leading-relaxed group-hover:text-gray-900 transition-colors duration-200">
								{example}
							</span>
						</div>
					</button>
				))}
			</div>
			<p className="text-xs text-gray-600 mt-4 text-center">
				Click any example to get started, or write your own custom search above
			</p>
		</div>
	);
};

export default ExampleQueries;
