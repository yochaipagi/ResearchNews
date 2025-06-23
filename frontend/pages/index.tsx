import React from 'react';
import { GetServerSideProps } from 'next';
import { useSession, signIn, getSession } from 'next-auth/react';
import Link from 'next/link';
import { EnvelopeIcon, ClockIcon, DocumentTextIcon, UserGroupIcon } from '@heroicons/react/24/outline';

import Layout from '../components/Layout';

export default function Home() {
  const { data: session } = useSession();

  return (
    <Layout title="Research Digest - Stay Updated with the Latest arXiv Papers">
      <div className="bg-white">
        {/* Hero section */}
        <div className="relative bg-gradient-to-r from-blue-600 to-indigo-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
            <div className="md:w-3/5">
              <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
                Stay updated with the latest research in your field
              </h1>
              <p className="mt-6 text-xl text-blue-100 max-w-3xl">
                Research Digest delivers personalized arXiv papers directly to your inbox at your preferred frequency.
                No noise, just the research that matters to you.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row gap-4">
                {session ? (
                  <>
                    <Link href="/profile" className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-gray-50">
                      Your Profile
                    </Link>
                    <Link href="/onboarding" className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-500 hover:bg-indigo-600">
                      Customize Your Digest
                    </Link>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => signIn('google', { callbackUrl: '/onboarding' })}
                      className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-500 hover:bg-indigo-600"
                    >
                      Get Started
                    </button>
                    <Link href="#features" className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-100 bg-indigo-800 bg-opacity-60 hover:bg-opacity-70">
                      Learn More
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="absolute bottom-0 right-0 hidden lg:block w-2/5 h-full">
            <div className="h-full bg-contain bg-no-repeat bg-right-bottom" style={{ backgroundImage: "url('/images/email-illustration.svg')" }}></div>
          </div>
        </div>

        {/* Feature section */}
        <div id="features" className="py-16 sm:py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-base font-semibold text-indigo-600 tracking-wide uppercase">Features</h2>
              <p className="mt-1 text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight">
                Why choose Research Digest?
              </p>
              <p className="max-w-xl mt-5 mx-auto text-xl text-gray-500">
                Our newsletter is designed to keep researchers informed without overwhelming them.
              </p>
            </div>

            <div className="mt-16">
              <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
                <div className="pt-6">
                  <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                    <div className="-mt-6">
                      <div>
                        <span className="inline-flex items-center justify-center p-3 bg-indigo-500 rounded-md shadow-lg">
                          <EnvelopeIcon className="h-6 w-6 text-white" aria-hidden="true" />
                        </span>
                      </div>
                      <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">Email Newsletter</h3>
                      <p className="mt-5 text-base text-gray-500">
                        Receive a curated selection of papers directly in your inbox. No need to check multiple websites.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-6">
                  <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                    <div className="-mt-6">
                      <div>
                        <span className="inline-flex items-center justify-center p-3 bg-indigo-500 rounded-md shadow-lg">
                          <ClockIcon className="h-6 w-6 text-white" aria-hidden="true" />
                        </span>
                      </div>
                      <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">Flexible Frequency</h3>
                      <p className="mt-5 text-base text-gray-500">
                        Choose daily, weekly, or monthly digests based on your preferences and reading habits.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-6">
                  <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                    <div className="-mt-6">
                      <div>
                        <span className="inline-flex items-center justify-center p-3 bg-indigo-500 rounded-md shadow-lg">
                          <DocumentTextIcon className="h-6 w-6 text-white" aria-hidden="true" />
                        </span>
                      </div>
                      <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">AI-Generated Summaries</h3>
                      <p className="mt-5 text-base text-gray-500">
                        Each paper includes a concise TL;DR summary to help you quickly grasp the key points.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-6">
                  <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                    <div className="-mt-6">
                      <div>
                        <span className="inline-flex items-center justify-center p-3 bg-indigo-500 rounded-md shadow-lg">
                          <UserGroupIcon className="h-6 w-6 text-white" aria-hidden="true" />
                        </span>
                      </div>
                      <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">Personalized Selection</h3>
                      <p className="mt-5 text-base text-gray-500">
                        Select your research interests from arXiv categories to receive only relevant papers.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA section */}
        <div className="bg-indigo-700">
          <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              <span className="block">Ready to stay updated?</span>
              <span className="block">Start your research digest today.</span>
            </h2>
            <p className="mt-4 text-lg leading-6 text-indigo-200">
              It takes less than a minute to set up your personalized research digest.
            </p>
            {session ? (
              <Link href="/onboarding" className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50 sm:w-auto">
                Customize Your Digest
              </Link>
            ) : (
              <button
                onClick={() => signIn('google', { callbackUrl: '/onboarding' })}
                className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-700 bg-white hover:bg-indigo-50 sm:w-auto"
              >
                Get Started
              </button>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  
  return {
    props: { session },
  };
}; 