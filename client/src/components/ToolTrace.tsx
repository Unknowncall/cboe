import React from 'react';
import type { ToolTrace } from '../types';

interface ToolTraceProps {
	toolTraces: ToolTrace[];
	showToolTrace: boolean;
}

const ToolTrace: React.FC<ToolTraceProps> = ({ toolTraces, showToolTrace }) => {
	if (!showToolTrace || toolTraces.length === 0) {
		return null;
	}

	return (
		<div className="mb-8 p-4 bg-gray-100 rounded-lg">
			<h3 className="text-md font-semibold mb-2">Tool Trace</h3>
			<div className="space-y-2">
				{toolTraces.map((trace, idx) => (
					<div key={idx} className="flex justify-between items-center text-sm">
						<span className="font-mono">{trace.tool}</span>
						<span className="text-gray-600">
							{trace.duration_ms}ms • {trace.result_count} results
						</span>
					</div>
				))}
			</div>
		</div>
	);
};

export default ToolTrace;
