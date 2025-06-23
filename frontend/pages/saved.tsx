import { useState, useEffect } from 'react';
import { useSession, getSession } from 'next-auth/react';
import { GetServerSideProps } from 'next';
import { 
  ArrowPathIcon, 
  BookmarkIcon
} from '@heroicons/react/24/outline';
import Layout from '../components/Layout';
import PaperCard from '../components/PaperCard';
import BookmarkToast from '../components/BookmarkToast';
import { Paper, unsavePaper, fetchSavedPapers, setAuthToken } from '../lib/api';

interface SavedProps {
  initialSavedPapers: Paper[];
}

export default function Saved({ initialSavedPapers }: SavedProps) {
  const [papers, setPapers] = useState<Paper[]>(initialSavedPapers);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [showToast, setShowToast] = useState<boolean>(false);
  const { data: session } = useSession();

  // Set auth token when session changes
  useEffect(() => {
    if (session?.user?.email) {
      setAuthToken(session.user.email);
      
      // Fetch saved papers if not provided in props
      if (initialSavedPapers.length === 0) {
        loadSavedPapers();
      }
    }
  }, [session]);

  const loadSavedPapers = async () => {
    if (!session) return;
    
    setLoading(true);
    try {
      const savedPapers = await fetchSavedPapers();
      setPapers(savedPapers);
    } catch (error) {
      console.error('Error fetching saved papers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUnsave = async (paper: Paper) => {
    if (!session) return;
    
    try {
      await unsavePaper(paper.arxiv_id);
      setPapers(papers.filter(p => p.id !== paper.id));
      
      // Show success toast
      setToastMessage('Paper removed from your collection');
      setShowToast(true);
    } catch (error) {
      console.error('Error unsaving paper:', error);
      setToastMessage('Unable to remove paper. Please try again.');
      setShowToast(true);
    }
  };

  const closeToast = () => {
    setShowToast(false);
  };

  return (
    <Layout title="Saved Papers | ResearchFeed">
      {/* Sticky header */}
      <div className="sticky top-0 z-10 bg-white bg-opacity-90 backdrop-blur-sm border-b border-gray-200 mb-4">
        <div className="flex justify-between items-center py-3">
          <div className="flex items-center">
            <BookmarkIcon className="h-6 w-6 text-blue-500 mr-2" />
            <h1 className="text-xl font-bold">Saved Papers</h1>
          </div>
          
          {session && (
            <button 
              onClick={loadSavedPapers}
              className="p-2 rounded-full hover:bg-gray-100 transition"
              disabled={loading}
              aria-label="Refresh saved papers"
            >
              <ArrowPathIcon className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {!session ? (
        <div className="text-center py-10 bg-white rounded-xl border border-gray-200 p-5">
          <BookmarkIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">Sign in to see your saved papers</h2>
          <p className="text-gray-600 mb-6">
            Save interesting research papers to read later or reference in your work
          </p>
          <button 
            onClick={() => window.location.href = '/api/auth/signin'}
            className="px-5 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition"
          >
            Sign in
          </button>
        </div>
      ) : loading ? (
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="border border-gray-200 rounded-xl p-4 bg-white">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : papers.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-xl border border-gray-200 p-5">
          <BookmarkIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 mb-2">No saved papers yet</h2>
          <p className="text-gray-600 mb-6">
            When you find interesting papers, click the bookmark icon to save them here
          </p>
          <a 
            href="/"
            className="px-5 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition"
          >
            Discover Papers
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {papers.map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              isSaved={true}
              onUnsave={handleUnsave}
            />
          ))}
        </div>
      )}

      {/* Toast notification */}
      <BookmarkToast 
        message={toastMessage}
        show={showToast}
        onClose={closeToast}
      />
    </Layout>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  
  if (!session) {
    // Allow non-authenticated users to see the page (but with a prompt to sign in)
    return {
      props: {
        initialSavedPapers: [],
      },
    };
  }
  
  try {
    // Set up authorization header with the user's email
    const headers = {
      Authorization: `Bearer ${session?.user?.email || ''}`,
    };
    
    // Fetch saved papers from API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/user/saved-papers`, { 
      headers 
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch saved papers');
    }
    
    const initialSavedPapers = await response.json();
    
    return {
      props: {
        initialSavedPapers,
      },
    };
  } catch (error) {
    console.error('Error fetching saved papers in getServerSideProps:', error);
    
    return {
      props: {
        initialSavedPapers: [],
      },
    };
  }
}; 