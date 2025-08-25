export const TrailListSkeleton = () => {
	return (
		<div className="space-y-8 animate-pulse">
			{/* Header skeleton */}
			<div className="text-center">
				<div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-2"></div>
				<div className="h-6 bg-gray-200 rounded w-96 mx-auto"></div>
			</div>

			{/* Table skeleton */}
			<div className="bg-white/80 backdrop-blur-md border border-white/30 rounded-2xl shadow-xl overflow-hidden">
				{/* Table header skeleton */}
				<div className="bg-gradient-to-r from-emerald-50 to-blue-50 p-6">
					<div className="grid grid-cols-5 gap-4">
						<div className="h-6 bg-gray-200 rounded"></div>
						<div className="h-6 bg-gray-200 rounded"></div>
						<div className="h-6 bg-gray-200 rounded"></div>
						<div className="h-6 bg-gray-200 rounded"></div>
						<div className="h-6 bg-gray-200 rounded"></div>
					</div>
				</div>

				{/* Table rows skeleton */}
				{[...Array(3)].map((_, i) => (
					<div key={i} className="border-b border-gray-100/50 p-6">
						<div className="grid grid-cols-5 gap-4 items-center">
							{/* Trail details */}
							<div className="space-y-3">
								<div className="h-6 bg-gray-200 rounded w-3/4"></div>
								<div className="h-4 bg-gray-200 rounded w-1/2"></div>
								<div className="h-10 bg-gray-200 rounded"></div>
							</div>

							{/* Stats */}
							<div className="space-y-3">
								<div className="h-16 bg-gray-200 rounded"></div>
								<div className="h-16 bg-gray-200 rounded"></div>
							</div>

							{/* Difficulty */}
							<div className="space-y-3">
								<div className="h-8 bg-gray-200 rounded w-20 mx-auto"></div>
								<div className="h-6 bg-gray-200 rounded w-16 mx-auto"></div>
							</div>

							{/* Dogs */}
							<div className="space-y-2">
								<div className="h-12 w-12 bg-gray-200 rounded-full mx-auto"></div>
								<div className="h-4 bg-gray-200 rounded w-8 mx-auto"></div>
							</div>

							{/* Features */}
							<div className="space-y-2">
								<div className="flex flex-wrap gap-2">
									{[...Array(3)].map((_, j) => (
										<div key={j} className="h-6 bg-gray-200 rounded w-16"></div>
									))}
								</div>
							</div>
						</div>
					</div>
				))}
			</div>
		</div>
	);
};

export const SearchFormSkeleton = () => {
	return (
		<div className="mb-12 animate-pulse">
			{/* Main search container skeleton */}
			<div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
				<div className="flex flex-col gap-6">
					{/* Label skeleton */}
					<div className="h-6 bg-gray-200 rounded w-80"></div>

					{/* Textarea skeleton */}
					<div className="h-32 bg-gray-200 rounded-xl"></div>

					{/* Agent selection skeleton */}
					<div className="flex items-center justify-between p-4 bg-gray-50/50 rounded-xl">
						<div className="flex items-center gap-4">
							<div className="h-5 bg-gray-200 rounded w-24"></div>
							<div className="h-10 bg-gray-200 rounded w-40"></div>
						</div>
						<div className="h-4 bg-gray-200 rounded w-32"></div>
					</div>

					{/* Submit button skeleton */}
					<div className="h-14 bg-gray-200 rounded-xl"></div>
				</div>
			</div>

			{/* Example queries skeleton */}
			<div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-2xl p-6 border border-emerald-100">
				<div className="h-6 bg-gray-200 rounded w-48 mb-4"></div>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
					{[...Array(6)].map((_, i) => (
						<div key={i} className="h-16 bg-gray-200 rounded-xl"></div>
					))}
				</div>
			</div>
		</div>
	);
};
