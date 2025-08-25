import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import Layout from './components/Layout';
import { CombinedTrailSearchProvider } from './contexts';
import './App.css';

// Lazy load pages for code splitting
const Home = lazy(() => import('./pages/Home'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const About = lazy(() => import('./pages/About'));
const FAQ = lazy(() => import('./pages/FAQ'));
const Contact = lazy(() => import('./pages/Contact'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Loading skeleton component
const PageSkeleton = () => (
	<div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50 animate-pulse">
		<div className="max-w-7xl mx-auto px-4 py-8">
			<div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
			<div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
			<div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{[...Array(6)].map((_, i) => (
					<div key={i} className="h-48 bg-gray-200 rounded"></div>
				))}
			</div>
		</div>
	</div>
);

function App() {
	return (
		<CombinedTrailSearchProvider>
			<Router>
				<Suspense fallback={<PageSkeleton />}>
					<Routes>
						<Route path="/" element={<Layout />}>
							<Route index element={<Home />} />
							<Route path="search" element={<SearchPage />} />
							<Route path="about" element={<About />} />
							<Route path="faq" element={<FAQ />} />
							<Route path="contact" element={<Contact />} />
							<Route path="*" element={<NotFound />} />
						</Route>
					</Routes>
				</Suspense>
			</Router>
		</CombinedTrailSearchProvider>
	);
}

export default App;
