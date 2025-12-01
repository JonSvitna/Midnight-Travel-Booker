import React from 'react';
import { Link } from 'react-router-dom';
import { Moon, Clock, Shield, Zap, Check } from 'lucide-react';

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <Moon className="h-20 w-20 text-blue-600 mx-auto mb-8" />
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Never Miss a Midnight Deal Again
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Automate your travel bookings at midnight and secure the lowest rates 
            while you sleep. No more staying up late!
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/signup"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold border-2 border-blue-600 hover:bg-blue-50 transition"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Clock className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Automated Booking</h3>
            <p className="text-gray-600">
              Set your travel preferences and let our system book at exactly midnight
              in your timezone when prices drop.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Shield className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Secure & Private</h3>
            <p className="text-gray-600">
              Your credentials are encrypted with military-grade security. 
              We never store payment information.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Zap className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Instant Notifications</h3>
            <p className="text-gray-600">
              Get email notifications immediately after booking attempts, 
              successful or not.
            </p>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Basic',
                price: '$9.99',
                features: ['1 booking per month', 'Email notifications', 'Basic support']
              },
              {
                name: 'Standard',
                price: '$19.99',
                features: ['5 bookings per month', 'Priority notifications', 'Priority support', 'Multiple destinations']
              },
              {
                name: 'Premium',
                price: '$39.99',
                features: ['Unlimited bookings', 'SMS + Email notifications', '24/7 support', 'Advanced preferences', 'API access']
              }
            ].map((plan) => (
              <div key={plan.name} className="bg-white p-8 rounded-lg shadow-md">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-4xl font-bold text-blue-600 mb-6">{plan.price}<span className="text-lg text-gray-600">/mo</span></p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <Check className="h-5 w-5 text-green-500 mr-2" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/signup"
                  className="block w-full bg-blue-600 text-white text-center px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  Choose Plan
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2025 Midnight Travel Booker. All rights reserved.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            For demonstration purposes only. Use responsibly and ethically.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
