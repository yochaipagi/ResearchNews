import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import axios from 'axios';
import Link from 'next/link';

import Layout from '../components/Layout';

export default function Unsubscribe() {
  const router = useRouter();
  const { token } = router.query;
  
  const [isProcessing, setIsProcessing] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function processUnsubscribe() {
      if (!token) return;
      
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/unsubscribe?token=${token}`);
        setSuccess(true);
      } catch (err: any) {
        console.error('Unsubscribe error', err);
        setError(err.response?.data?.detail || 'Failed to unsubscribe. The link may be invalid or expired.');
      } finally {
        setIsProcessing(false);
      }
    }

    if (token) {
      processUnsubscribe();
    } else {
      setIsProcessing(false);
      setError('Invalid unsubscribe link. No token provided.');
    }
  }, [token]);

  return (
    <Layout title="Unsubscribe - Research Digest">
      <div className="max-w-lg mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Research Digest Unsubscribe</h1>
          
          {isProcessing ? (
            <div className="animate-pulse">
              <p className="text-gray-600">Processing your request...</p>
            </div>
          ) : success ? (
            <div>
              <div className="mb-6 text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                  <svg className="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">Successfully Unsubscribed</h2>
              <p className="text-gray-600 mb-6">
                You have been unsubscribed from Research Digest emails. 
                We're sorry to see you go!
              </p>
              <div className="mt-6">
                <Link href="/profile" className="text-blue-600 hover:text-blue-800">
                  Update your preferences instead
                </Link>
              </div>
            </div>
          ) : (
            <div>
              <div className="mb-6 text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <svg className="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              </div>
              <h2 className="text-lg font-medium text-gray-900 mb-2">Error</h2>
              <p className="text-gray-600 mb-6">{error}</p>
              <div className="mt-6">
                <Link href="/" className="text-blue-600 hover:text-blue-800">
                  Return to home page
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
} 