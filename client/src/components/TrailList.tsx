import React, { memo } from 'react';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { MapPin, Mountain, Route, Dog } from 'lucide-react';
import type { Trail } from '../types';
import { Button } from '@/components/ui/button';

interface TrailListProps {
	trails: Trail[];
}

const TrailList: React.FC<TrailListProps> = memo(({
	trails,
}) => {
	const getDifficultyColor = (difficulty: string) => {
		switch (difficulty.toLowerCase()) {
			case 'easy': return 'bg-green-50 text-green-700 border-green-200';
			case 'moderate': return 'bg-yellow-50 text-yellow-700 border-yellow-200';
			case 'hard': return 'bg-red-50 text-red-700 border-red-200';
			default: return 'bg-gray-50 text-gray-700 border-gray-200';
		}
	};

	const getFeatureColor = (feature: string) => {
		const colors: { [key: string]: string } = {
			waterfall: 'bg-cyan-50 text-cyan-700 border-cyan-200',
			lake: 'bg-blue-50 text-blue-700 border-blue-200',
			dunes: 'bg-orange-50 text-orange-700 border-orange-200',
			prairie: 'bg-green-50 text-green-700 border-green-200',
			boardwalk: 'bg-gray-50 text-gray-700 border-gray-200',
			beach: 'bg-yellow-50 text-yellow-700 border-yellow-200',
			forest: 'bg-emerald-50 text-emerald-700 border-emerald-200',
			garden: 'bg-pink-50 text-pink-700 border-pink-200',
		};
		return colors[feature] || 'bg-gray-50 text-gray-700 border-gray-200';
	};

	if (trails.length === 0) {
		return null;
	}

	return (
		<section className="space-y-6" role="region" aria-labelledby="trail-results-heading">
			<h2 id="trail-results-heading" className="text-2xl font-bold text-gray-900">
				Trail Results ({trails.length} trail{trails.length !== 1 ? 's' : ''} found)
			</h2>

			<div className="w-full overflow-hidden">
				<div className="border rounded-xl bg-white shadow-sm overflow-x-auto">
					<Table className="w-full">
						<TableHeader className="bg-gray-50/50">
							<TableRow className="border-b border-gray-200">
								<TableHead className="w-[35%] font-semibold text-gray-900 py-4 px-4">Trail Details</TableHead>
								<TableHead className="w-[20%] text-center font-semibold text-gray-900 py-4 px-2">
									<div className="flex items-center justify-center gap-1">
										<Route className="h-4 w-4" />
										Stats
									</div>
								</TableHead>
								<TableHead className="w-[15%] text-center font-semibold text-gray-900 py-4 px-2">
									<div className="flex items-center justify-center gap-1">
										<Mountain className="h-4 w-4" />
										Level
									</div>
								</TableHead>
								<TableHead className="w-[10%] text-center font-semibold text-gray-900 py-4 px-2">
									<div className="flex items-center justify-center gap-1">
										<Dog className="h-4 w-4" />
										Dogs
									</div>
								</TableHead>
								<TableHead className="w-[20%] font-semibold text-gray-900 py-4 px-4">Features</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{trails.map((trail) => {
								return (
									<TableRow key={trail.id} className="hover:bg-gray-50/30 transition-colors border-b border-gray-100">
										<TableCell className="py-4 px-4 align-middle space-y-1">
											<p className="font-semibold text-gray-900">{trail.name}</p>
											<Button
												onClick={() => window.open(`https://www.google.com/maps?q=${trail.latitude},${trail.longitude}`, '_blank')}
												variant="outline"
											>
												<MapPin className="h-3 w-3" />
												<span>View Location</span>
											</Button>
										</TableCell>

										<TableCell className="text-center py-4 px-2 align-top">
											<div className="space-y-2">
												<div className="text-sm font-medium text-blue-700">
													{trail.distance_miles.toFixed(1)} mi
												</div>
												<div className="text-sm font-medium text-orange-700">
													{trail.elevation_gain_m}m
												</div>
											</div>
										</TableCell>

										<TableCell className="text-center py-4 px-2 align-top">
											<div className="space-y-2">
												<Badge variant="outline" className={`text-xs font-medium ${getDifficultyColor(trail.difficulty)}`}>
													{trail.difficulty}
												</Badge>
												<div className="text-xs text-gray-600 capitalize">
													{trail.route_type}
												</div>
											</div>
										</TableCell>

										<TableCell className="text-center py-4 px-2 align-top">
											<div className="flex justify-center">
												<span className={`text-lg ${trail.dogs_allowed ? 'text-green-600' : 'text-red-600'}`}>
													{trail.dogs_allowed ? '✓' : '✗'}
												</span>
											</div>
										</TableCell>

										<TableCell className="py-4 px-4 align-top">
											<div className="space-y-3">
												{/* Features */}
												<div className="flex flex-wrap gap-1">
													{trail.features.slice(0, 3).map(feature => (
														<Badge
															key={feature}
															variant="outline"
															className={`text-xs font-medium ${getFeatureColor(feature)}`}
														>
															{feature}
														</Badge>
													))}
													{trail.features.length > 3 && (
														<Badge variant="outline" className="text-xs bg-gray-50 text-gray-600 border-gray-200">
															+{trail.features.length - 3}
														</Badge>
													)}
												</div>

											</div>
										</TableCell>
									</TableRow>
								);
							})}
						</TableBody>
					</Table>
				</div>
			</div>
		</section>
	);
});

TrailList.displayName = 'TrailList';

export default TrailList;
