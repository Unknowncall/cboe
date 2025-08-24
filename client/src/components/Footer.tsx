import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, Mountain, MapPin, Mail, HelpCircle, Info } from 'lucide-react';

const Footer: React.FC = () => {
	return (
		<footer className="bg-gradient-to-r from-slate-800 to-slate-900 text-white">
			<div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
				<div className="grid grid-cols-1 md:grid-cols-4 gap-8">
					{/* Brand section */}
					<div className="col-span-1 md:col-span-2">
						<div className="flex items-center gap-3 mb-4">
							<div className="p-2 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg">
								<Mountain className="h-6 w-6 text-white" />
							</div>
							<span className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
								Chicago Trail Explorer
							</span>
						</div>
						<p className="text-slate-300 mb-4 max-w-md">
							Discover your next adventure with AI-powered trail recommendations.
							Find the perfect hiking experience tailored to your preferences in the Chicago area.
						</p>
						<div className="flex items-center gap-1 text-sm text-slate-400">
							<span>Built with</span>
							<Heart className="h-4 w-4 text-red-400 mx-1" />
							<span>by outdoor enthusiasts</span>
						</div>
					</div>

					{/* Quick Links */}
					<div>
						<h3 className="text-lg font-semibold mb-4">Quick Links</h3>
						<ul className="space-y-2">
							<li>
								<Link to="/" className="text-slate-300 hover:text-emerald-400 transition-colors flex items-center gap-2">
									<Mountain className="h-4 w-4" />
									Home
								</Link>
							</li>
							<li>
								<Link to="/search" className="text-slate-300 hover:text-emerald-400 transition-colors flex items-center gap-2">
									<MapPin className="h-4 w-4" />
									Find Trails
								</Link>
							</li>
							<li>
								<Link to="/about" className="text-slate-300 hover:text-emerald-400 transition-colors flex items-center gap-2">
									<Info className="h-4 w-4" />
									About Us
								</Link>
							</li>
							<li>
								<Link to="/faq" className="text-slate-300 hover:text-emerald-400 transition-colors flex items-center gap-2">
									<HelpCircle className="h-4 w-4" />
									FAQ
								</Link>
							</li>
						</ul>
					</div>

					{/* Support */}
					<div>
						<h3 className="text-lg font-semibold mb-4">Support</h3>
						<ul className="space-y-2">
							<li>
								<Link to="/contact" className="text-slate-300 hover:text-emerald-400 transition-colors flex items-center gap-2">
									<Mail className="h-4 w-4" />
									Contact Us
								</Link>
							</li>
							<li>
								<a href="/sitemap.xml" className="text-slate-300 hover:text-emerald-400 transition-colors">
									Sitemap
								</a>
							</li>
							<li>
								<a href="mailto:hello@chicagotrailexplorer.com" className="text-slate-300 hover:text-emerald-400 transition-colors">
									hello@chicagotrailexplorer.com
								</a>
							</li>
						</ul>
					</div>
				</div>

				{/* Bottom section */}
				<div className="mt-8 pt-8 border-t border-slate-700">
					<div className="flex flex-col md:flex-row justify-between items-center gap-4">
						<p className="text-sm text-slate-400">
							© 2025 Chicago Trail Explorer. All rights reserved.
						</p>
						<div className="flex items-center gap-4 text-sm text-slate-400">
							<span>Privacy Policy</span>
							<span>•</span>
							<span>Terms of Service</span>
							<span>•</span>
							<span>Get out there and explore! 🏔️</span>
						</div>
					</div>
				</div>
			</div>
		</footer>
	);
};

export default Footer;