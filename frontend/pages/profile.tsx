import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import { useSession, getSession } from 'next-auth/react';
import axios from 'axios';

import Layout from '../components/Layout';

interface UserProfile {
  id: number;
  email: string;
  name: string | null;
  categories: string[];
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  next_digest_at: string | null;
  is_active: boolean;
  created_at: string;
}

interface ProfileFormData {
  name: string;
  categories: string[];
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
}

export default function Profile() {
  const { data: session } = useSession();
  const router = useRouter();
  const { onboarded } = router.query;
  
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [formData, setFormData] = useState<ProfileFormData>({
    name: '',
    categories: [],
    frequency: 'DAILY',
  });
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(
    onboarded ? 'Successfully subscribed to Research Digest!' : null
  );

  // Fetch user profile and categories
  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        // Get profile
        const profileResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/profile`, {
          headers: { Authorization: `Bearer ${session?.user?.email}` },
        });
        setProfile(profileResponse.data);
        setFormData({
          name: profileResponse.data.name || '',
          categories: profileResponse.data.categories,
          frequency: profileResponse.data.frequency,
        });

        // Get available categories
        const categoriesResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/categories`);
        setAvailableCategories(categoriesResponse.data);
      } catch (err) {
        console.error('Failed to fetch data', err);
        setError('Failed to load your profile. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    }

    if (session?.user?.email) {
      fetchData();
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
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (formData.categories.length === 0) {
        throw new Error('Please select at least one category');
      }

      await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL}/profile`,
        formData,
        {
          headers: { Authorization: `Bearer ${session?.user?.email}` },
        }
      );
      setSuccessMessage('Profile updated successfully!');
      
      // Refresh profile data
      const profileResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/profile`, {
        headers: { Authorization: `Bearer ${session?.user?.email}` },
      });
      setProfile(profileResponse.data);
    } catch (err) {
      console.error('Update error', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Group categories by main area
  const categoryGroups: Record<string, string[]> = {};
  availableCategories.forEach(category => {
    const mainArea = category.includes('.') ? category.split('.')[0] : category;
    if (!categoryGroups[mainArea]) {
      categoryGroups[mainArea] = [];
    }
    categoryGroups[mainArea].push(category);
  });

  if (isLoading) {
    return (
      <Layout title="Your Profile - Research Digest">
        <div className="max-w-3xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Your Profile</h1>
          <div className="flex justify-center">
            <div className="animate-pulse">Loading your profile...</div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Your Profile - Research Digest">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Your Profile</h1>
        
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
            <p>{error}</p>
          </div>
        )}
        
        {successMessage && (
          <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
            <p>{successMessage}</p>
          </div>
        )}

        {profile && (
          <div className="mb-8 p-4 bg-gray-50 rounded-md">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Subscription Details</h2>
            <p className="text-gray-600">
              <span className="font-medium">Email:</span> {profile.email}
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Status:</span> {profile.is_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Next digest:</span> {profile.next_digest_at 
                ? new Date(profile.next_digest_at).toLocaleString() 
                : 'Not scheduled'}
            </p>
            <p className="text-gray-600">
              <span className="font-medium">Subscribed since:</span> {new Date(profile.created_at).toLocaleDateString()}
            </p>
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your research categories
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
              disabled={isSaving}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isSaving ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
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
        destination: '/auth/signin?callbackUrl=/profile',
        permanent: false,
      },
    };
  }

  return {
    props: { session },
  };
}; 