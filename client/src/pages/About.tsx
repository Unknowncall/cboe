import React from 'react';
import { Mountain, Target, Users, Zap, Award, Heart } from 'lucide-react';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-emerald-600 to-blue-600 text-white">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <Mountain className="h-16 w-16 mx-auto mb-6 text-emerald-200" />
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              About Chicago Trail Explorer
            </h1>
            <p className="text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed">
              Revolutionizing outdoor exploration with AI-powered trail discovery 
              for the Chicago metropolitan area and beyond.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        {/* Mission Section */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Our Mission
          </h2>
          <p className="text-xl text-gray-700 max-w-4xl mx-auto leading-relaxed">
            We believe that everyone deserves to discover the perfect outdoor adventure. 
            Our AI-powered platform makes it easy to find trails that match your preferences, 
            fitness level, and interests, connecting you with Chicago's incredible natural spaces.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="p-3 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full w-fit mb-4">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">AI-Powered Search</h3>
            <p className="text-gray-600">
              Our advanced AI understands natural language queries and provides 
              personalized trail recommendations based on your specific needs.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full w-fit mb-4">
              <Target className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Precision Matching</h3>
            <p className="text-gray-600">
              Find trails that perfectly match your difficulty preference, distance requirements, 
              and specific interests like waterfalls, wildlife, or scenic views.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full w-fit mb-4">
              <Users className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Community Driven</h3>
            <p className="text-gray-600">
              Built by outdoor enthusiasts for outdoor enthusiasts, with continuously 
              updated trail information and community-verified details.
            </p>
          </div>
        </div>

        {/* Story Section */}
        <div className="bg-white rounded-3xl p-8 md:p-12 shadow-lg mb-16">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
              <div className="space-y-4 text-gray-700">
                <p>
                  Chicago Trail Explorer was born from a simple frustration: finding the perfect 
                  hiking trail shouldn't require hours of research across multiple websites and apps.
                </p>
                <p>
                  Our team of outdoor enthusiasts and technology experts came together to create 
                  a solution that makes trail discovery as simple as having a conversation with 
                  a knowledgeable local guide.
                </p>
                <p>
                  Today, we're proud to serve thousands of hikers, nature lovers, and adventure 
                  seekers in the Chicago area, helping them discover hidden gems and popular 
                  destinations alike.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-emerald-200 to-blue-200 rounded-2xl p-8 text-center">
                <Award className="h-16 w-16 text-emerald-600 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 mb-2">10,000+</h3>
                <p className="text-gray-700 font-medium">Trails Discovered</p>
              </div>
            </div>
          </div>
        </div>

        {/* Values Section */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">Our Values</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <Heart className="h-12 w-12 text-emerald-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-3">Accessibility</h3>
              <p className="text-gray-600">
                Making outdoor exploration accessible to everyone, regardless of experience level or physical ability.
              </p>
            </div>
            <div className="text-center">
              <Mountain className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-3">Conservation</h3>
              <p className="text-gray-600">
                Promoting responsible outdoor recreation and supporting the preservation of natural spaces.
              </p>
            </div>
            <div className="text-center">
              <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-3">Community</h3>
              <p className="text-gray-600">
                Building a community of outdoor enthusiasts who share knowledge and inspire each other.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-emerald-600 to-blue-600 rounded-3xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
          <p className="text-xl mb-8 opacity-90">
            Start your next adventure with personalized trail recommendations.
          </p>
          <a
            href="/search"
            className="inline-block bg-white text-emerald-600 font-bold py-3 px-8 rounded-full hover:bg-gray-100 transition-colors"
          >
            Find Your Trail
          </a>
        </div>
      </div>
    </div>
  );
};

export default About;
