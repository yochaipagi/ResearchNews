import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { GetServerSideProps } from 'next';
import Layout from '../components/Layout';
import CategoryExplorer from '../components/CategoryExplorer';
import PaperCard from '../components/PaperCard';
import BookmarkToast from '../components/BookmarkToast';
import { 
  MAIN_CATEGORIES, 
  TOP_CATEGORIES, 
  CATEGORY_MAP 
} from '../lib/categories';
import { 
  fetchFeed, 
  Paper, 
  savePaper, 
  unsavePaper, 
  setAuthToken,
  fetchSavedPapers 
} from '../lib/api';

interface ExploreProps {
  initialPapers: Paper[];
  initialCategory?: string;
}

export default function Explore({ initialPapers, initialCategory }: ExploreProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(initialCategory || null);
  const [papers, setPapers] = useState<Paper[]>(initialPapers);
  const [savedPapers, setSavedPapers] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>('');
  const [showToast, setShowToast] = useState<boolean>(false);
  const { data: session } = useSession();

  // Set auth token when session changes
  useState(() => {
    if (session?.user?.email) {
      setAuthToken(session.user.email);
      fetchSavedPaperIds();
    }
  });

  const fetchSavedPaperIds = async () => {
    if (!session) return;
    
    try {
      const savedPapersData = await fetchSavedPapers();
      const savedIds = new Set(savedPapersData.map(paper => paper.id));
      setSavedPapers(savedIds);
    } catch (error) {
      console.error('Error fetching saved papers:', error);
    }
  };

  const fetchCategoryPapers = async (categoryId: string) => {
    setLoading(true);
    try {
      const data = await fetchFeed(undefined, 15, categoryId);
      setPapers(data.papers);
      setSelectedCategory(categoryId);
    } catch (error) {
      console.error('Error fetching papers for category:', error);
      setToastMessage('Error loading papers. Please try again.');
      setShowToast(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (paper: Paper) => {
    if (!session) {
      setToastMessage('Sign in to save papers');
      setShowToast(true);
      return;
    }
    
    try {
      await savePaper(paper.arxiv_id);
      setSavedPapers(new Set(savedPapers).add(paper.id));
      setToastMessage('Paper saved to your collection');
      setShowToast(true);
    } catch (error) {
      console.error('Error saving paper:', error);
      setToastMessage('Unable to save paper. Please try again.');
      setShowToast(true);
    }
  };

  const handleUnsave = async (paper: Paper) => {
    if (!session) return;
    
    try {
      await unsavePaper(paper.arxiv_id);
      const newSavedPapers = new Set(savedPapers);
      newSavedPapers.delete(paper.id);
      setSavedPapers(newSavedPapers);
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

  const getCategoryName = (categoryId: string | null) => {
    if (!categoryId) return 'All Categories';
    return CATEGORY_MAP[categoryId] || categoryId;
  };

  return (
    <Layout title={`Explore ${getCategoryName(selectedCategory)} | ResearchFeed`}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left sidebar with category explorer */}
        <div className="md:col-span-1">
          <CategoryExplorer onSelectCategory={fetchCategoryPapers} />
        </div>
        
        {/* Right side with papers */}
        <div className="md:col-span-2">
          {/* Current category header */}
          <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
            <h1 className="text-xl font-bold">
              {selectedCategory ? (
                <>
                  {getCategoryName(selectedCategory)}
                  <span className="text-sm text-gray-500 ml-2">({selectedCategory})</span>
                </>
              ) : 'Browse All Categories'}
            </h1>
            <p className="text-gray-600 mt-2">
              {selectedCategory ? 
                `Explore the latest research papers in ${getCategoryName(selectedCategory)}` : 
                'Select a category from the explorer to view papers'}
            </p>
          </div>
          
          {/* Papers list */}
          {loading ? (
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
              <p className="text-xl font-bold text-gray-800 mb-2">No papers found</p>
              <p className="text-gray-600 mb-6">
                {selectedCategory ? 
                  `There are no recent papers in ${getCategoryName(selectedCategory)}` : 
                  'Please select a category to view papers'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {papers.map((paper) => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  isSaved={savedPapers.has(paper.id)}
                  onSave={handleSave}
                  onUnsave={handleUnsave}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
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
  const { category } = context.query;
  
  // If a category is provided, fetch papers for that category
  if (category && typeof category === 'string') {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/feed?category=${category}&limit=15`
      );
      
      if (response.ok) {
        const data = await response.json();
        return {
          props: {
            initialPapers: data.papers,
            initialCategory: category
          }
        };
      }
    } catch (error) {
      console.error('Error fetching category papers:', error);
    }
  }
  
  // Return empty array if no category or fetch fails
  return {
    props: {
      initialPapers: [],
      initialCategory: null
    }
  };
}; 