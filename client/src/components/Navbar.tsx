import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mountain, Menu, X, Search, Info, HelpCircle, Mail, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const Navbar: React.FC = () => {
	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const location = useLocation();

	const navigation = [
		{ name: 'Home', href: '/', icon: Home },
		{ name: 'Search Trails', href: '/search', icon: Search },
		{ name: 'About', href: '/about', icon: Info },
		{ name: 'FAQ', href: '/faq', icon: HelpCircle },
		{ name: 'Contact', href: '/contact', icon: Mail },
	];

	const isActivePage = (href: string) => {
		if (href === '/' && location.pathname === '/') return true;
		if (href !== '/' && location.pathname.startsWith(href)) return true;
		return false;
	};

	return (
		<nav className="bg-white/95 backdrop-blur-md shadow-lg border-b border-emerald-100 sticky top-0 z-50">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex justify-between items-center h-16">
					{/* Logo and Brand */}
					<Link
						to="/"
						className="flex items-center space-x-3 group"
					>
						<div className="p-2 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg shadow-md group-hover:shadow-lg transition-shadow">
							<Mountain className="h-6 w-6 text-white" />
						</div>
						<div className="flex flex-col">
							<span className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-green-700 bg-clip-text text-transparent">
								Chicago Trail Explorer
							</span>
							<span className="text-xs text-gray-500 hidden sm:block">
								AI-Powered Trail Discovery
							</span>
						</div>
					</Link>

					{/* Desktop Navigation */}
					<div className="hidden md:flex items-center space-x-1">
						{navigation.map((item) => {
							const IconComponent = item.icon;
							const isActive = isActivePage(item.href);

							return (
								<Link
									key={item.name}
									to={item.href}
									className={cn(
										"flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
										isActive
											? "bg-emerald-100 text-emerald-700 shadow-sm"
											: "text-gray-700 hover:bg-emerald-50 hover:text-emerald-600"
									)}
								>
									<IconComponent className="h-4 w-4" />
									<span>{item.name}</span>
								</Link>
							);
						})}
					</div>

					{/* Mobile menu button */}
					<div className="md:hidden">
						<button
							onClick={() => setIsMenuOpen(!isMenuOpen)}
							className="p-2 rounded-lg text-gray-700 hover:bg-emerald-50 hover:text-emerald-600 transition-colors"
						>
							{isMenuOpen ? (
								<X className="h-6 w-6" />
							) : (
								<Menu className="h-6 w-6" />
							)}
						</button>
					</div>
				</div>
			</div>

			{/* Mobile Navigation Menu */}
			{isMenuOpen && (
				<div className="md:hidden bg-white border-t border-emerald-100">
					<div className="px-4 pt-2 pb-3 space-y-1">
						{navigation.map((item) => {
							const IconComponent = item.icon;
							const isActive = isActivePage(item.href);

							return (
								<Link
									key={item.name}
									to={item.href}
									onClick={() => setIsMenuOpen(false)}
									className={cn(
										"flex items-center space-x-3 px-3 py-3 rounded-lg text-base font-medium transition-all duration-200",
										isActive
											? "bg-emerald-100 text-emerald-700"
											: "text-gray-700 hover:bg-emerald-50 hover:text-emerald-600"
									)}
								>
									<IconComponent className="h-5 w-5" />
									<span>{item.name}</span>
								</Link>
							);
						})}
					</div>
				</div>
			)}
		</nav>
	);
};

export default Navbar;
