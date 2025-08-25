import React, { useState } from 'react';
import type { ToolTrace } from '../types';
import { useSearchState, useResults } from '../contexts';

const ToolTrace: React.FC = () => {
	const { showToolTrace } = useSearchState();
	const { toolTraces } = useResults();
	const [expandedTraces, setExpandedTraces] = useState<Set<number>>(new Set());

	if (!showToolTrace || toolTraces.length === 0) {
		return null;
	}

	const toggleTrace = (index: number) => {
		const newExpanded = new Set(expandedTraces);
		if (newExpanded.has(index)) {
			newExpanded.delete(index);
		} else {
			newExpanded.add(index);
		}
		setExpandedTraces(newExpanded);
	};

	return (
		<div className="mb-8 p-4 bg-gray-50 rounded-lg border">
			<h3 className="text-lg font-semibold mb-4 text-gray-800">🔍 AI Tool Traces</h3>
			<div className="space-y-3">
				{toolTraces.map((trace, idx) => {
					const isExpanded = expandedTraces.has(idx);
					return (
						<div key={idx} className="bg-white rounded-md border shadow-sm">
							{/* Header - Always visible */}
							<div
								className="p-3 cursor-pointer hover:bg-gray-50 flex justify-between items-center"
								onClick={() => toggleTrace(idx)}
							>
								<div className="flex items-center space-x-3">
									<span className={`w-3 h-3 rounded-full ${trace.success ? 'bg-green-500' : 'bg-red-500'}`}></span>
									<span className="font-mono text-sm font-medium">{trace.tool}</span>
									{trace.ai_confidence && (
										<span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
											{Math.round(trace.ai_confidence * 100)}% confidence
										</span>
									)}
								</div>
								<div className="flex items-center space-x-3 text-sm text-gray-600">
									<span>{trace.duration_ms}ms</span>
									{trace.result_count !== undefined && (
										<span>{trace.result_count} results</span>
									)}
									<span className="text-xs">
										{isExpanded ? '▼' : '▶'}
									</span>
								</div>
							</div>

							{/* Expanded content */}
							{isExpanded && (
								<div className="px-3 pb-3 border-t bg-gray-50">
									{/* AI Reasoning */}
									{trace.reasoning && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">🧠 AI Reasoning</h4>
											<div className="text-sm text-gray-600 whitespace-pre-line bg-white p-3 rounded border">
												{trace.reasoning}
											</div>
										</div>
									)}

									{/* Processing Steps */}
									{trace.processing_steps && trace.processing_steps.length > 0 && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">⚙️ Processing Steps</h4>
											<div className="space-y-1">
												{trace.processing_steps.map((step, stepIdx) => (
													<div key={stepIdx} className="text-sm text-gray-600 bg-white p-2 rounded border-l-2 border-blue-200">
														{step}
													</div>
												))}
											</div>
										</div>
									)}

									{/* Input Parameters */}
									{trace.input_parameters && Object.keys(trace.input_parameters).length > 0 && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">📥 Input Parameters</h4>
											<div className="bg-white p-3 rounded border">
												<pre className="text-xs text-gray-600 overflow-x-auto">
													{JSON.stringify(trace.input_parameters, null, 2)}
												</pre>
											</div>
										</div>
									)}

									{/* Search Filters */}
									{trace.search_filters && Object.keys(trace.search_filters).length > 0 && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">🎯 Generated Search Filters</h4>
											<div className="bg-white p-3 rounded border">
												<pre className="text-xs text-gray-600 overflow-x-auto">
													{JSON.stringify(trace.search_filters, null, 2)}
												</pre>
											</div>
										</div>
									)}

									{/* Database Query */}
									{trace.database_query && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">🗃️ Database Query</h4>
											<div className="bg-gray-900 text-green-400 p-3 rounded border font-mono text-xs overflow-x-auto">
												{trace.database_query}
											</div>
										</div>
									)}

									{/* Function Call Details */}
									{trace.function_call && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-gray-700 mb-2">🔧 Function Call</h4>
											<div className="bg-white p-3 rounded border">
												<div className="text-sm">
													<span className="font-mono text-blue-600">{trace.function_call.name}</span>
													{trace.function_call.extraction_confidence && (
														<span className="ml-2 text-xs text-gray-500">
															(extraction confidence: {Math.round(trace.function_call.extraction_confidence * 100)}%)
														</span>
													)}
												</div>
												{trace.function_call.arguments && (
													<pre className="text-xs text-gray-600 mt-2 overflow-x-auto">
														{JSON.stringify(trace.function_call.arguments, null, 2)}
													</pre>
												)}
											</div>
										</div>
									)}

									{/* Errors */}
									{trace.errors && trace.errors.length > 0 && (
										<div className="mb-4">
											<h4 className="font-semibold text-sm text-red-700 mb-2">❌ Errors</h4>
											<div className="space-y-1">
												{trace.errors.map((error, errorIdx) => (
													<div key={errorIdx} className="text-sm text-red-600 bg-red-50 p-2 rounded border-l-2 border-red-200">
														{error}
													</div>
												))}
											</div>
										</div>
									)}

									{/* Summary */}
									<div className="pt-2 border-t flex justify-between items-center text-xs text-gray-500">
										<span>
											Status: {trace.success ? '✅ Success' : '❌ Failed'}
										</span>
										<span>
											Duration: {trace.duration_ms}ms
										</span>
									</div>
								</div>
							)}
						</div>
					);
				})}
			</div>
		</div>
	);
};

export default ToolTrace;
