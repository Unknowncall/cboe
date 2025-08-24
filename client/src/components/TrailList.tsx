import React, { memo } from 'react';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { MapPin, Mountain, Route, Dog, Car, Droplets, TreePine, Info, ExternalLink, Phone } from 'lucide-react';
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
		<section className="space-y-8" role="region" aria-labelledby="trail-results-heading">
			<div className="text-center">
				<h2 id="trail-results-heading" className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent mb-2">
					🏔️ Trail Results
				</h2>
				<p className="text-lg text-gray-600">
					Found {trails.length} amazing trail{trails.length !== 1 ? 's' : ''} for your next adventure
				</p>
			</div>

			<div className="w-full overflow-hidden">
				<div className="bg-white/80 backdrop-blur-md border border-white/30 rounded-2xl shadow-xl overflow-hidden">
					<Table className="w-full">
						<TableHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
							<TableRow className="border-b border-emerald-100">
								<TableHead className="w-[35%] font-bold text-gray-800 py-6 px-6 text-left">
									<div className="flex items-center gap-2">
										<MapPin className="h-5 w-5 text-emerald-600" />
										Trail Details
									</div>
								</TableHead>
								<TableHead className="w-[20%] text-center font-bold text-gray-800 py-6 px-4">
									<div className="flex items-center justify-center gap-2">
										<Route className="h-5 w-5 text-blue-600" />
										Stats
									</div>
								</TableHead>
								<TableHead className="w-[15%] text-center font-bold text-gray-800 py-6 px-4">
									<div className="flex items-center justify-center gap-2">
										<Mountain className="h-5 w-5 text-purple-600" />
										Level
									</div>
								</TableHead>
								<TableHead className="w-[10%] text-center font-bold text-gray-800 py-6 px-4">
									<div className="flex items-center justify-center gap-2">
										<Dog className="h-5 w-5 text-green-600" />
										Dogs
									</div>
								</TableHead>
								<TableHead className="w-[20%] font-bold text-gray-800 py-6 px-6">
									<div className="flex items-center gap-2">
										<TreePine className="h-5 w-5 text-emerald-600" />
										Features
									</div>
								</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{trails.map((trail) => {
								return (
									<TableRow key={trail.id} className="group hover:bg-gradient-to-r hover:from-emerald-50/50 hover:to-blue-50/50 transition-all duration-200 border-b border-gray-100/50">
										<TableCell className="py-6 px-6 align-top">
											<div className="space-y-3">
												<div className="text-left">
													<p className="font-bold text-gray-900 text-lg group-hover:text-emerald-700 transition-colors duration-200">
														{trail.name}
													</p>
													{trail.city && trail.state && (
														<p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
															<MapPin className="h-4 w-4 text-gray-500" />
															{trail.city}, {trail.state}
														</p>
													)}
												</div>
												<Button
													onClick={() => window.open(`https://www.google.com/maps?q=${trail.latitude},${trail.longitude}`, '_blank')}
													variant="outline"
													className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border-blue-200 hover:border-blue-300 text-blue-700 hover:text-blue-800 transition-all duration-200"
												>
													<MapPin className="h-4 w-4" />
													<span>View on Map</span>
												</Button>
											</div>
										</TableCell>

										<TableCell className="text-center py-6 px-4 align-top">
											<div className="space-y-3">
												<div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
													<div className="text-lg font-bold text-blue-700 flex items-center justify-center gap-1">
														<Route className="h-4 w-4" />
														{trail.distance_miles.toFixed(1)} mi
													</div>
													<div className="text-xs text-blue-600">Distance</div>
												</div>
												<div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-3 border border-orange-200">
													<div className="text-sm font-bold text-orange-700 flex items-center justify-center gap-1">
														<Mountain className="h-4 w-4" />
														{(trail.elevation_gain_m * 3.28084).toFixed(0)} ft
													</div>
													<div className="text-xs text-orange-600">Elevation</div>
												</div>
											</div>
										</TableCell>

										<TableCell className="text-center py-6 px-4 align-middle">
											<div className="space-y-3">

												<Badge variant="outline" className={`text-sm font-bold border-2 ${getDifficultyColor(trail.difficulty)}`}>
													{trail.difficulty}
												</Badge>

												<div className="text-xs text-gray-600 capitalize bg-gray-50 px-3 py-1 rounded-full">
													{trail.route_type}
												</div>
											</div>
										</TableCell>

										<TableCell className="text-center py-6 px-4 align-middle">
											<div className="flex flex-col items-center gap-2">
												<div className={`w-12 h-12 rounded-full flex items-center justify-center ${trail.dogs_allowed ? 'bg-green-100 border-2 border-green-300' : 'bg-red-100 border-2 border-red-300'}`}>
													<Dog className={`h-6 w-6 ${trail.dogs_allowed ? 'text-green-600' : 'text-red-600'}`} />
												</div>
												<span className={`text-sm font-bold ${trail.dogs_allowed ? 'text-green-600' : 'text-red-600'}`}>
													{trail.dogs_allowed ? 'Yes' : ' No'}
												</span>
											</div>
										</TableCell>

										<TableCell className="py-6 px-6 align-middle">
											<div className="space-y-4">
												{/* Features */}
												<div>
													<div className="flex flex-wrap gap-2">
														{trail.features.slice(0, 4).map(feature => (
															<Badge
																key={feature}
																variant="outline"
																className={`text-xs font-medium border-2 ${getFeatureColor(feature)}`}
															>
																{feature}
															</Badge>
														))}
														{trail.features.length > 4 && (
															<Badge variant="outline" className="text-xs border-gray-300">
																+{trail.features.length - 4} more
															</Badge>
														)}
													</div>
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
		</section >
	);
});

TrailList.displayName = 'TrailList';

export default TrailList;
