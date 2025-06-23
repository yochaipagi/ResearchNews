import React, { useState, useEffect } from 'react';
import { fetchFeed, Paper } from '../lib/api';

interface PaperSuggestionsProps {
  currentPaperId?: number;
  category?: string | null;
  limit?: number;
}

const PaperSuggestions: React.FC<PaperSuggestionsProps> = ({ 
  currentPaperId, 
  category, 
  limit = 3 
}) => {
  const [suggestions, setSuggestions] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!category) return;

    const fetchSuggestions = async () => {
      setLoading(true);
      try {
        const result = await fetchFeed(undefined, limit, category);
        // Filter out the current paper from results if it exists
        const filteredResults = currentPaperId 
          ? result.papers.filter(paper => paper.id !== currentPaperId)
          : result.papers;
        
        setSuggestions(filteredResults.slice(0, limit));
      } catch (error) {
        console.error('Error fetching paper suggestions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [category, currentPaperId, limit]);

  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 bg-gray-50 rounded-xl p-5">
      <h3 className="text-lg font-bold mb-4">You might also like</h3>
      <div className="space-y-3">
        {loading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(limit)].map((_, i) => (
              <div key={i} className="flex gap-3">
                <div className="w-10 h-10 bg-gray-300 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          suggestions.map(paper => (
            <a 
              key={paper.id}
              href={`https://arxiv.org/abs/${paper.arxiv_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex gap-3 p-3 rounded-lg hover:bg-white hover:shadow-sm transition"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex-shrink-0 flex items-center justify-center text-white font-medium">
                {paper.category?.split('.')[1] || 'AI'}
              </div>
              <div>
                <h4 className="font-medium text-sm line-clamp-2 text-gray-900">{paper.title}</h4>
                <p className="text-xs text-gray-500 mt-1">{paper.authors.split(',')[0]}{paper.authors.includes(',') && ' et al.'}</p>
              </div>
            </a>
          ))
        )}
      </div>
    </div>
  );
};

export default PaperSuggestions; 