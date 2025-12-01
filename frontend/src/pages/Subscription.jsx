import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { subscriptionAPI } from '../utils/api';
import { Check, CreditCard } from 'lucide-react';

const Subscription = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const response = await subscriptionAPI.getCurrent();
      setSubscription(response.data.subscription);
    } catch (error) {
      console.error('Error loading subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (tier) => {
    try {
      const response = await subscriptionAPI.createCheckoutSession({ tier });
      window.location.href = response.data.checkout_url;
    } catch (error) {
      alert('Failed to create checkout session');
    }
  };

  const plans = [
    {
      name: 'Basic',
      tier: 'basic',
      price: '$9.99',
      features: ['1 booking per month', 'Email notifications', 'Basic support']
    },
    {
      name: 'Standard',
      tier: 'standard',
      price: '$19.99',
      features: ['5 bookings per month', 'Priority notifications', 'Priority support', 'Multiple destinations'],
      popular: true
    },
    {
      name: 'Premium',
      tier: 'premium',
      price: '$39.99',
      features: ['Unlimited bookings', 'SMS + Email notifications', '24/7 support', 'Advanced preferences', 'API access']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Subscription</h1>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : subscription && subscription.status === 'active' ? (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold mb-2">Current Plan</h2>
                <p className="text-gray-600">
                  You are subscribed to the <span className="font-semibold capitalize">{subscription.tier}</span> plan
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Renews on {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
              </div>
              <CreditCard className="h-12 w-12 text-green-600" />
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
            <p className="text-yellow-700">
              You don't have an active subscription. Choose a plan below to get started.
            </p>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.tier}
              className={`bg-white rounded-lg shadow-lg p-8 relative ${
                plan.popular ? 'ring-2 ring-blue-600' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <p className="text-4xl font-bold text-blue-600 mb-6">
                {plan.price}
                <span className="text-lg text-gray-600">/mo</span>
              </p>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <Check className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(plan.tier)}
                disabled={subscription?.tier === plan.tier && subscription?.status === 'active'}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  subscription?.tier === plan.tier && subscription?.status === 'active'
                    ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {subscription?.tier === plan.tier && subscription?.status === 'active'
                  ? 'Current Plan'
                  : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Subscription;
