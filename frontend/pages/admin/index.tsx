import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import { useSession, getSession } from 'next-auth/react';
import axios from 'axios';
import { ChartBarIcon, UserIcon, DocumentTextIcon, ClockIcon } from '@heroicons/react/24/outline';

import Layout from '../../components/Layout';

interface UserResponse {
  id: number;
  email: string;
  name: string | null;
  categories: string[];
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  next_digest_at: string | null;
  is_active: boolean;
  created_at: string;
}

interface StatsResponse {
  user_count: number;
  active_user_count: number;
  paper_count: number;
  frequency_stats: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  popular_categories: Record<string, number>;
}

export default function AdminDashboard() {
  const { data: session } = useSession();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'users'>('overview');

  // Fetch admin data
  useEffect(() => {
    async function fetchAdminData() {
      setIsLoading(true);
      try {
        // Get stats
        const statsResponse = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/admin/stats`,
          { headers: { Authorization: `Bearer ${session?.user?.email}` } }
        );
        setStats(statsResponse.data);

        // Get users
        const usersResponse = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/admin/users`,
          { headers: { Authorization: `Bearer ${session?.user?.email}` } }
        );
        setUsers(usersResponse.data);
      } catch (err) {
        console.error('Failed to fetch admin data', err);
        setError('Failed to load admin data. You may not have admin permissions.');
      } finally {
        setIsLoading(false);
      }
    }

    if (session?.user?.email) {
      fetchAdminData();
    }
  }, [session]);

  // Handle manual trigger of paper fetch
  const handleTriggerFetch = async () => {
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/trigger/fetch`,
        {},
        { headers: { Authorization: `Bearer ${session?.user?.email}` } }
      );
      alert('Paper fetch task triggered successfully!');
    } catch (err) {
      console.error('Failed to trigger paper fetch', err);
      alert('Failed to trigger paper fetch task.');
    }
  };

  // Handle manual trigger of summary processing
  const handleTriggerSummarize = async () => {
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/trigger/summarize`,
        {},
        { headers: { Authorization: `Bearer ${session?.user?.email}` } }
      );
      alert('Summary processing task triggered successfully!');
    } catch (err) {
      console.error('Failed to trigger summary processing', err);
      alert('Failed to trigger summary processing task.');
    }
  };

  if (isLoading) {
    return (
      <Layout title="Admin Dashboard - Research Digest">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
          <div className="flex justify-center">
            <div className="animate-pulse">Loading admin data...</div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Admin Dashboard - Research Digest">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard - Research Digest">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
        
        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Users
            </button>
          </nav>
        </div>
        
        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              {/* Total Users Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <UserIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                        <dd>
                          <div className="text-lg font-medium text-gray-900">{stats.user_count}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-5 py-3">
                  <div className="text-sm">
                    <span className="font-medium text-green-700">
                      {stats.active_user_count} active ({Math.round((stats.active_user_count / stats.user_count) * 100)}%)
                    </span>
                  </div>
                </div>
              </div>

              {/* Total Papers Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <DocumentTextIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Papers</dt>
                        <dd>
                          <div className="text-lg font-medium text-gray-900">{stats.paper_count}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-5 py-3">
                  <div className="text-sm">
                    <button 
                      onClick={handleTriggerFetch}
                      className="font-medium text-blue-600 hover:text-blue-500"
                    >
                      Trigger paper fetch
                    </button>
                  </div>
                </div>
              </div>

              {/* Frequency Stats Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ClockIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Digest Frequency</dt>
                        <dd>
                          <div className="text-lg font-medium text-gray-900">
                            {stats.frequency_stats.daily} daily
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-5 py-3">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">
                      {stats.frequency_stats.weekly} weekly, {stats.frequency_stats.monthly} monthly
                    </span>
                  </div>
                </div>
              </div>

              {/* Categories Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <ChartBarIcon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Top Categories</dt>
                        <dd>
                          <div className="text-lg font-medium text-gray-900">
                            {Object.keys(stats.popular_categories).length} categories
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-5 py-3">
                  <div className="text-sm">
                    <button 
                      onClick={handleTriggerSummarize}
                      className="font-medium text-blue-600 hover:text-blue-500"
                    >
                      Process summaries
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Popular Categories Chart */}
            <div className="bg-white shadow rounded-lg p-6 mb-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Popular Categories</h3>
              <div className="space-y-4">
                {Object.entries(stats.popular_categories).map(([category, count]) => (
                  <div key={category}>
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-medium text-gray-700">{category}</div>
                      <div className="text-sm text-gray-500">{count} users</div>
                    </div>
                    <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(count / stats.user_count) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="flex flex-col">
            <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          User
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Status
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Frequency
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Next Digest
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Categories
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{user.name || 'No name'}</div>
                                <div className="text-sm text-gray-500">{user.email}</div>
                                <div className="text-xs text-gray-400">
                                  Joined {new Date(user.created_at).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                user.is_active
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.frequency}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.next_digest_at
                              ? new Date(user.next_digest_at).toLocaleString()
                              : 'Not scheduled'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="max-w-xs truncate">
                              {user.categories.join(', ')}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
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
        destination: '/auth/signin?callbackUrl=/admin',
        permanent: false,
      },
    };
  }

  return {
    props: { session },
  };
}; 