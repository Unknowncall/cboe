import React from 'react';
import { Controller, Control } from 'react-hook-form';
import type { SearchFormData } from '../hooks/useTrailSearch';

interface AgentSelectorProps {
	control: Control<SearchFormData>;
	isStreaming: boolean;
	watchedAgentType: string;
}

const AgentSelector: React.FC<AgentSelectorProps> = ({ control, isStreaming, watchedAgentType }) => {
	return (
		<div className="flex items-center justify-between p-4 bg-gray-50/50 rounded-xl border border-gray-200">
			<div className="flex items-center gap-4">
				<label htmlFor="agent-select" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
					🤖 AI Assistant:
				</label>
				<Controller
					name="agentType"
					control={control}
					render={({ field }) => (
						<select
							{...field}
							id="agent-select"
							disabled={isStreaming}
							className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium bg-white focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 focus:outline-none disabled:opacity-50 transition-all duration-200"
							aria-label="Select AI agent type"
						>
							<option value="custom">⚡ Custom Agent</option>
							<option value="langchain">🧠 LangChain Agent</option>
						</select>
					)}
				/>
			</div>
			<div className="text-xs text-gray-600 max-w-xs">
				{watchedAgentType === 'custom' ? '⚡ Fast, direct OpenAI implementation' : '🧠 Framework-based with memory'}
			</div>
		</div>
	);
};

export default AgentSelector;
