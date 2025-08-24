import React from 'react';
import { Link } from 'react-router-dom';
import { Mountain, MapPin, Compass, Search, ArrowRight, Star, Users, Zap } from 'lucide-react';
import SEOHead from '../components/SEOHead';

const Home: React.FC = () => {
  return (
    <>
      <SEOHead
        title="Chicago Trail Explorer - AI-Powered Hiking Trail Discovery"
        description="Discover the best hiking trails in Chicago with our AI-powered trail explorer. Get personalized recommendations, detailed trail information, and real-time search results."
        canonicalUrl="https://chicago-trail-explorer.com/"
      />
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-green-200/20 to-transparent rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-tr from-blue-200/20 to-transparent rounded-full blur-3xl"></div>
          <div className="absolute top-1/3 left-1/2 w-64 h-64 bg-gradient-to-br from-purple-200/15 to-transparent rounded-full blur-2xl"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 py-20 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Hero Icons */}
            <div className="flex items-center justify-center gap-3 mb-8">
              <div className="p-4 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full shadow-lg animate-pulse">
                <Mountain className="h-10 w-10 text-white" />
              </div>
              <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full shadow-lg animate-pulse" style={{animationDelay: '1s'}}>
                <Compass className="h-10 w-10 text-white" />
              </div>
              <div className="p-4 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full shadow-lg animate-pulse" style={{animationDelay: '2s'}}>
                <MapPin className="h-10 w-10 text-white" />
              </div>
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 leading-tight">
              Chicago Trail Explorer
            </h1>

            <div className="w-32 h-1 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full mx-auto mb-8"></div>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-gray-700 max-w-4xl mx-auto leading-relaxed mb-12">
              Discover your next adventure with AI-powered trail recommendations.
              <br />
              Find the perfect hiking experience tailored to your preferences in the Chicago area.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/search"
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-bold py-4 px-8 rounded-full hover:from-emerald-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Search className="h-5 w-5" />
                <span>Start Exploring</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center space-x-2 bg-white text-gray-700 font-bold py-4 px-8 rounded-full hover:bg-gray-50 transition-all duration-200 shadow-lg border border-gray-200"
              >
                <span>Learn More</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose Chicago Trail Explorer?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience the future of trail discovery with our AI-powered platform
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center group">
              <div className="p-6 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full w-fit mx-auto mb-6 shadow-lg group-hover:shadow-xl transition-shadow">
                <Zap className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">AI-Powered Search</h3>
              <p className="text-gray-600 leading-relaxed">
                Simply describe what you're looking for in natural language. 
                Our AI understands your preferences and finds the perfect trails for you.
              </p>
            </div>

            <div className="text-center group">
              <div className="p-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full w-fit mx-auto mb-6 shadow-lg group-hover:shadow-xl transition-shadow">
                <MapPin className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Local Expertise</h3>
              <p className="text-gray-600 leading-relaxed">
                Comprehensive coverage of Chicago area trails with detailed information 
                about difficulty, length, amenities, and current conditions.
              </p>
            </div>

            <div className="text-center group">
              <div className="p-6 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full w-fit mx-auto mb-6 shadow-lg group-hover:shadow-xl transition-shadow">
                <Users className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Community Driven</h3>
              <p className="text-gray-600 leading-relaxed">
                Built by hikers for hikers, with continuously updated information 
                from our community of outdoor enthusiasts.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="text-3xl font-bold text-emerald-600 mb-2">500+</div>
              <div className="text-gray-600">Trails Cataloged</div>
            </div>
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">10K+</div>
              <div className="text-gray-600">Searches Completed</div>
            </div>
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="text-3xl font-bold text-purple-600 mb-2">98%</div>
              <div className="text-gray-600">User Satisfaction</div>
            </div>
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="text-3xl font-bold text-pink-600 mb-2">50mi</div>
              <div className="text-gray-600">Coverage Radius</div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Finding your perfect trail is as easy as 1-2-3
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-emerald-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Describe Your Ideal Trail</h3>
              <p className="text-gray-600">
                Tell us what you're looking for: "Easy trails near water" or 
                "Challenging hikes with great views" - use natural language!
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">AI Finds Perfect Matches</h3>
              <p className="text-gray-600">
                Our AI analyzes your request and searches through our comprehensive 
                database to find trails that match your preferences exactly.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Start Your Adventure</h3>
              <p className="text-gray-600">
                Get detailed information about each trail including difficulty, 
                length, amenities, and directions to start your outdoor adventure.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Hikers Say
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "Finally, a trail finder that actually understands what I'm looking for! 
                The AI recommendations are spot-on."
              </p>
              <div className="text-sm font-medium text-gray-900">Sarah M.</div>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "Love how I can just type 'dog-friendly trails near me' and get 
                perfect results. Makes planning weekend hikes so much easier!"
              </p>
              <div className="text-sm font-medium text-gray-900">Mike R.</div>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "The detailed trail information and real-time updates have made 
                my hiking adventures so much more enjoyable and safe."
              </p>
              <div className="text-sm font-medium text-gray-900">Jennifer L.</div>
            </div>
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="py-20 bg-gradient-to-r from-emerald-600 to-blue-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Discover Your Next Adventure?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of hikers who have found their perfect trails with Chicago Trail Explorer
          </p>
          <Link
            to="/search"
            className="inline-flex items-center space-x-2 bg-white text-emerald-600 font-bold py-4 px-8 rounded-full hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <Search className="h-5 w-5" />
            <span>Start Exploring Now</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </div>
    </div>
    </>
  );
};

export default Home;
