import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, MapPin, ArrowLeft } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50 flex items-center justify-center">
      <div className="max-w-2xl mx-auto px-4 text-center">
        {/* 404 Visual */}
        <div className="mb-8">
          <div className="text-8xl font-bold text-gray-300 mb-4">404</div>
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="p-3 bg-gradient-to-br from-gray-400 to-gray-500 rounded-full">
              <MapPin className="h-8 w-8 text-white" />
            </div>
          </div>
        </div>

        {/* Content */}
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Trail Not Found
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-lg mx-auto">
          Looks like you've wandered off the beaten path! The page you're looking for doesn't exist.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Link
            to="/"
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-bold py-3 px-6 rounded-full hover:from-emerald-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Home className="h-5 w-5" />
            <span>Go Home</span>
          </Link>
          <Link
            to="/search"
            className="inline-flex items-center space-x-2 bg-white text-gray-700 font-bold py-3 px-6 rounded-full hover:bg-gray-50 transition-all duration-200 shadow-lg border border-gray-200"
          >
            <Search className="h-5 w-5" />
            <span>Find Trails</span>
          </Link>
        </div>

        {/* Helpful Links */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Popular Destinations
          </h2>
          <div className="grid sm:grid-cols-2 gap-4">
            <Link
              to="/search"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Search className="h-5 w-5 text-emerald-600" />
              <span className="text-gray-700">Search Trails</span>
            </Link>
            <Link
              to="/about"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <MapPin className="h-5 w-5 text-blue-600" />
              <span className="text-gray-700">About Us</span>
            </Link>
            <Link
              to="/faq"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-purple-600" />
              <span className="text-gray-700">FAQ</span>
            </Link>
            <Link
              to="/contact"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Home className="h-5 w-5 text-pink-600" />
              <span className="text-gray-700">Contact</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
