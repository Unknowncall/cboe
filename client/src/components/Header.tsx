import React from 'react';
import { Mountain, MapPin, Compass } from 'lucide-react';

const Header: React.FC = () => {
	return (
		<header className="text-center mb-12 relative">
			{/* Hero section with icons */}
			<div className="relative inline-block mb-6 w-full max-w-4xl">
				<div className="flex items-center justify-center gap-3 mb-4">
					<div className="p-3 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full shadow-lg">
						<Mountain className="h-8 w-8 text-white" />
					</div>
					<div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full shadow-lg">
						<Compass className="h-8 w-8 text-white" />
					</div>
					<div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full shadow-lg">
						<MapPin className="h-8 w-8 text-white" />
					</div>
				</div>

				<h1 className="text-5xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-3 px-4 leading-tight">
					Chicago Trail Explorer
				</h1>

				<div className="w-24 h-1 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full mx-auto mb-4"></div>
			</div>

			<p className="text-xl text-gray-700 max-w-2xl mx-auto leading-relaxed">
				Discover your next adventure with AI-powered trail recommendations.
				Find the perfect hiking experience tailored to your preferences.
			</p>

			{/* Stats or features */}
			<div className="mt-8 flex flex-wrap justify-center gap-6 text-sm">
				<div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm">
					<div className="w-2 h-2 bg-green-500 rounded-full"></div>
					<span className="text-gray-700 font-medium">Natural Language Search</span>
				</div>
				<div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm">
					<div className="w-2 h-2 bg-blue-500 rounded-full"></div>
					<span className="text-gray-700 font-medium">Real-time Results</span>
				</div>
				<div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm">
					<div className="w-2 h-2 bg-purple-500 rounded-full"></div>
					<span className="text-gray-700 font-medium">Detailed Trail Info</span>
				</div>
			</div>
		</header>
	);
};

export default Header;
