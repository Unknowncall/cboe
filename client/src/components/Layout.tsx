import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import ErrorBoundary from './ErrorBoundary';

const Layout: React.FC = () => {
	return (
		<ErrorBoundary>
			<div className="min-h-screen flex flex-col">
				<Navbar />
				<main className="flex-1">
					<Outlet />
				</main>
				<Footer />
			</div>
		</ErrorBoundary>
	);
};

export default Layout;
