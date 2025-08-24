import React, { memo, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import type { Trail, TrailDetails } from '../types';

interface TrailCardProps {
	trail: Trail;
	isExpanded: boolean;
	trailDetails: TrailDetails | undefined;
	onToggleDetails: (trail: Trail) => void;
}

const TrailCard: React.FC<TrailCardProps> = memo(({
	trail,
	isExpanded,
	trailDetails,
	onToggleDetails,
}) => {
	// Memoize expensive computations
	const formattedFeatures = useMemo(() =>
		trail.features.join(', '),
		[trail.features]
	);

	const formattedLocation = useMemo(() =>
		`${trail.latitude.toFixed(4)}, ${trail.longitude.toFixed(4)}`,
		[trail.latitude, trail.longitude]
	);

	const getDifficultyColor = (difficulty: string) => {
		switch (difficulty.toLowerCase()) {
			case 'easy': return 'bg-green-100 text-green-800';
			case 'moderate': return 'bg-yellow-100 text-yellow-800';
			case 'hard': return 'bg-red-100 text-red-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	};

	const getRouteTypeColor = (routeType: string) => {
		return routeType === 'loop' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800';
	};

	const getFeatureColor = (feature: string) => {
		const colors: { [key: string]: string } = {
			waterfall: 'bg-cyan-100 text-cyan-800',
			lake: 'bg-blue-100 text-blue-800',
			dunes: 'bg-orange-100 text-orange-800',
			prairie: 'bg-green-100 text-green-800',
			boardwalk: 'bg-gray-100 text-gray-800',
			beach: 'bg-yellow-100 text-yellow-800',
			forest: 'bg-emerald-100 text-emerald-800',
			garden: 'bg-pink-100 text-pink-800',
		};
		return colors[feature] || 'bg-gray-100 text-gray-800';
	};

	return (
		<Card className="overflow-hidden">
			<CardHeader>
				<div className="flex justify-between items-start">
					<div>
						<CardTitle className="text-xl" id={`trail-title-${trail.id}`}>
							{trail.name}
						</CardTitle>
						<CardDescription className="mt-1">{trail.why}</CardDescription>
					</div>
					<Button
						variant="outline"
						size="sm"
						onClick={() => onToggleDetails(trail)}
						aria-expanded={isExpanded}
						aria-controls={`trail-details-${trail.id}`}
						aria-labelledby={`trail-title-${trail.id}`}
						aria-describedby={`trail-summary-${trail.id}`}
					>
						{isExpanded ? 'Hide Details' : 'Show Details'}
					</Button>
				</div>
			</CardHeader>
			<CardContent>
				{/* Trail Badges */}
				<div
					className="flex flex-wrap gap-2 mb-4"
					id={`trail-summary-${trail.id}`}
					aria-label="Trail characteristics"
				>
					<Badge className="bg-indigo-100 text-indigo-800" aria-label={`Distance: ${trail.distance_miles.toFixed(1)} miles`}>
						{trail.distance_miles.toFixed(1)} mi
					</Badge>
					<Badge className="bg-orange-100 text-orange-800" aria-label={`Elevation gain: ${trail.elevation_gain_m} meters`}>
						{trail.elevation_gain_m} m elevation
					</Badge>
					<Badge className={getDifficultyColor(trail.difficulty)}>
						{trail.difficulty}
					</Badge>
					<Badge className={getRouteTypeColor(trail.route_type)}>
						{trail.route_type}
					</Badge>
					<Badge className={trail.dogs_allowed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
						{trail.dogs_allowed ? 'Dogs allowed' : 'No dogs'}
					</Badge>
				</div>

				{/* Feature Tags */}
				<div className="flex flex-wrap gap-2 mb-4">
					{trail.features.map(feature => (
						<Badge key={feature} className={getFeatureColor(feature)}>
							{feature}
						</Badge>
					))}
				</div>

				{/* Description Snippet */}
				<p className="text-gray-600 mb-4">{trail.description_snippet}</p>

				{/* Expanded Details */}
				{isExpanded && trailDetails && (
					<div
						className="pt-4 border-t border-gray-200"
						id={`trail-details-${trail.id}`}
						aria-labelledby={`trail-title-${trail.id}`}
						role="region"
					>
						<h4 className="font-semibold mb-2">Full Description</h4>
						<p className="text-gray-700">
							{trailDetails.description}
						</p>
						<div className="mt-2 text-sm text-gray-500" aria-label="Geographic coordinates">
							Location: {formattedLocation}
						</div>
					</div>
				)}
			</CardContent>
		</Card>
	);
});

TrailCard.displayName = 'TrailCard';

export default TrailCard;
