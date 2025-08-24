import React from 'react';
import { Badge } from './ui/badge';
import type { ParsedFilters } from '../types';

interface ParsedFiltersProps {
	parsedFilters: ParsedFilters | null;
}

const ParsedFilters: React.FC<ParsedFiltersProps> = ({ parsedFilters }) => {
	if (!parsedFilters) {
		return null;
	}

	return (
		<div className="mb-8 p-4 bg-blue-50 rounded-lg">
			<h3 className="text-md font-semibold mb-2">Detected Filters</h3>
			<div className="flex flex-wrap gap-2">
				{parsedFilters.distance_cap_miles && (
					<Badge variant="secondary">Distance ≤ {parsedFilters.distance_cap_miles} mi</Badge>
				)}
				{parsedFilters.elevation_cap_m && (
					<Badge variant="secondary">Elevation ≤ {parsedFilters.elevation_cap_m} m</Badge>
				)}
				{parsedFilters.difficulty && (
					<Badge variant="secondary">Difficulty: {parsedFilters.difficulty}</Badge>
				)}
				{parsedFilters.route_type && (
					<Badge variant="secondary">Route: {parsedFilters.route_type}</Badge>
				)}
				{parsedFilters.dogs_allowed !== null && parsedFilters.dogs_allowed !== undefined && (
					<Badge variant="secondary">
						Dogs: {parsedFilters.dogs_allowed ? 'allowed' : 'not allowed'}
					</Badge>
				)}
				{parsedFilters.features && parsedFilters.features.length > 0 && parsedFilters.features.map(feature => (
					<Badge key={feature} variant="secondary">Feature: {feature}</Badge>
				))}
				{parsedFilters.radius_miles && (
					<Badge variant="secondary">Within {parsedFilters.radius_miles} mi of Chicago</Badge>
				)}
			</div>
		</div>
	);
};

export default ParsedFilters;
