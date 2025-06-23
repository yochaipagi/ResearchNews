import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import { useSession, signIn, getSession } from 'next-auth/react';
import axios from 'axios';

import Layout from '../components/Layout';

type ArxivCategory = string;

interface OnboardingFormData {
  name: string;
  email: string;
  categories: ArxivCategory[];
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
}

export default function Onboarding() {
  const { data: session } = useSession();
  const router = useRouter();
  const [formData, setFormData] = useState<OnboardingFormData>({
    name: '',
    email: '',
    categories: [],
    frequency: 'DAILY',
  });
  const [availableCategories, setAvailableCategories] = useState<ArxivCategory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load available categories
  useEffect(() => {
    async function fetchCategories() {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/categories`);
        setAvailableCategories(response.data);
      } catch (err) {
        console.error('Failed to fetch categories', err);
        setError('Failed to load categories. Please try again.');
      }
    }

    fetchCategories();

    // Pre-fill email from session if available
    if (session?.user?.email) {
      const email = session.user.email || '';
      const name = session.user.name || '';
      setFormData(prev => ({ ...prev, email, name }));
    }
  }, [session]);

  // Handle form field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle category selection
  const handleCategoryChange = (category: string) => {
    setFormData(prev => {
      const updatedCategories = prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category];
      return { ...prev, categories: updatedCategories };
    });
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (formData.categories.length === 0) {
        throw new Error('Please select at least one category');
      }

      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/register`, formData);
      router.push('/profile?onboarded=true');
    } catch (err) {
      console.error('Registration error', err);
      setError('Failed to register. Please check your information and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Group categories by main area
  const categoryGroups: Record<string, ArxivCategory[]> = {};
  availableCategories.forEach(category => {
    const mainArea = category.includes('.') ? category.split('.')[0] : category;
    if (!categoryGroups[mainArea]) {
      categoryGroups[mainArea] = [];
    }
    categoryGroups[mainArea].push(category);
  });

  return (
    <Layout title="Get Started with Research Digest">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Welcome to Research Digest</h1>
        <p className="text-gray-600 mb-8">
          Customize your research digest by selecting your preferences below. You'll receive regular 
          updates with the latest papers from arXiv in your selected categories.
        </p>

        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
            <p>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Name (optional)
            </label>
            <input
              type="text"
              name="name"
              id="name"
              value={formData.name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Your name"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <input
              type="email"
              name="email"
              id="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Choose your research categories
            </label>
            <div className="space-y-4">
              {Object.entries(categoryGroups).map(([mainArea, categories]) => (
                <div key={mainArea} className="border rounded-md p-4">
                  <h3 className="font-medium text-gray-900 mb-2">{mainArea}</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                    {categories.map(category => (
                      <div key={category} className="flex items-center">
                        <input
                          id={category}
                          type="checkbox"
                          checked={formData.categories.includes(category)}
                          onChange={() => handleCategoryChange(category)}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor={category} className="ml-2 block text-sm text-gray-700">
                          {category}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            {formData.categories.length > 0 && (
              <p className="mt-2 text-sm text-gray-600">
                {formData.categories.length} categories selected
              </p>
            )}
          </div>

          <div>
            <label htmlFor="frequency" className="block text-sm font-medium text-gray-700">
              Digest frequency
            </label>
            <select
              id="frequency"
              name="frequency"
              value={formData.frequency}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="DAILY">Daily</option>
              <option value="WEEKLY">Weekly</option>
              <option value="MONTHLY">Monthly</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Processing...' : 'Subscribe to Research Digest'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);

  // Redirect if not logged in
  if (!session) {
    return {
      redirect: {
        destination: '/auth/signin?callbackUrl=/onboarding',
        permanent: false,
      },
    };
  }

  return {
    props: { session },
  };
}; 