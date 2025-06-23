import React, { useState } from 'react';
import { BookmarkIcon, ShareIcon, ArrowTopRightOnSquareIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { Paper } from '../lib/api';
import PaperSuggestions from './PaperSuggestions';
import { CATEGORY_MAP } from '../lib/categories';

// Helper function to get shortened category display
const getCategoryDisplay = (categoryId: string | null): string => {
  if (!categoryId) return 'AI';
  
  // For primary categories (like cs.AI), return just the secondary part (AI)
  if (categoryId.includes('.')) {
    const parts = categoryId.split('.');
    if (parts.length === 2 && parts[1].length >= 2) {
      return parts[1];
    }
  }
  
  // Default to first 2 chars of the category
  return categoryId.substring(0, 2);
};

// Helper to get full category name
const getCategoryName = (categoryId: string | null): string => {
  if (!categoryId) return 'Uncategorized';
  
  return CATEGORY_MAP[categoryId] || categoryId;
};

interface PaperCardProps {
  paper: Paper;
  isSaved?: boolean;
  onSave?: (paper: Paper) => void;
  onUnsave?: (paper: Paper) => void;
}

const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  isSaved = false,
  onSave,
  onUnsave,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [showMore, setShowMore] = useState(false);
  const [saveAnimation, setSaveAnimation] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleSaveClick = () => {
    setSaveAnimation(true);
    setTimeout(() => setSaveAnimation(false), 500);
    
    if (isSaved && onUnsave) {
      onUnsave(paper);
    } else if (!isSaved && onSave) {
      onSave(paper);
    }
  };

  // Create a summary limited to 280 characters (Twitter-like)
  const shortSummary = paper.summary 
    ? paper.summary.length > 280 
      ? `${paper.summary.slice(0, 280)}...` 
      : paper.summary
    : "No summary available";

  // Create a custom TLDR from the summary
  const tldr = paper.summary
    ? `TLDR: ${paper.summary.split('.')[0]}.` // First sentence as TLDR
    : "No summary available";

  const shareOnTwitter = () => {
    const text = encodeURIComponent(`Check out this paper: "${paper.title}" ${tldr}`);
    const url = encodeURIComponent(`https://arxiv.org/abs/${paper.arxiv_id}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  const openPaperLink = () => {
    window.open(`https://arxiv.org/abs/${paper.arxiv_id}`, '_blank');
  };

  return (
    <div className="border border-gray-200 rounded-xl p-4 mb-4 bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 flex-shrink-0 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold">
          {getCategoryDisplay(paper.category)}
        </div>
        
        <div className="flex-1">
          {/* Paper metadata */}
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-2">
              <p className="font-semibold text-gray-900">
                {getCategoryName(paper.category)}
              </p>
              <span className="text-gray-500">·</span>
              <p className="text-gray-500 text-sm">{formatDate(paper.published_at)}</p>
            </div>
          </div>
          
          {/* Paper title */}
          <h2 className="text-lg font-bold text-gray-900 mt-1 mb-1 hover:text-blue-500 cursor-pointer" onClick={openPaperLink}>
            {paper.title}
          </h2>
          
          {/* Authors */}
          <p className="text-gray-600 text-sm mb-2">{paper.authors}</p>
          
          {/* Summary section */}
          <div className="mt-2">
            <p className="text-gray-700 text-sm font-medium mb-1">{tldr}</p>
            
            {paper.summary && paper.summary.length > 280 && (
              <button 
                onClick={() => setExpanded(!expanded)} 
                className="text-blue-500 text-sm hover:underline mt-1"
              >
                {expanded ? 'Show less' : 'Read more'}
              </button>
            )}
            
            {expanded && paper.summary && (
              <p className="text-gray-700 text-sm mt-2">{paper.summary}</p>
            )}
          </div>
          
          {/* Action buttons */}
          <div className="flex items-center justify-between mt-4 text-gray-500">
            <a 
              href={`https://arxiv.org/abs/${paper.arxiv_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center hover:text-blue-500 transition"
            >
              <ArrowTopRightOnSquareIcon className="h-5 w-5 mr-1" />
              <span className="text-sm">arXiv:{paper.arxiv_id}</span>
            </a>
            
            <div className="flex items-center space-x-6">
              <button 
                onClick={shareOnTwitter}
                className="flex items-center hover:text-blue-500 transition"
                aria-label="Share on Twitter"
              >
                <ShareIcon className="h-5 w-5" />
              </button>
              
              <button
                onClick={handleSaveClick}
                className="flex items-center hover:text-blue-500 transition"
                aria-label={isSaved ? "Unsave paper" : "Save paper"}
                title={isSaved ? "Remove from saved papers" : "Save for later"}
              >
                {isSaved ? (
                  <BookmarkSolidIcon className={`h-5 w-5 text-blue-500 transform transition-all ${saveAnimation ? 'scale-125' : 'hover:scale-110'}`} />
                ) : (
                  <BookmarkIcon className={`h-5 w-5 transform transition-all ${saveAnimation ? 'scale-125 text-blue-500' : 'hover:scale-110'}`} />
                )}
              </button>
              
              <button
                onClick={() => setShowMore(!showMore)}
                className="flex items-center hover:text-blue-500 transition"
                aria-label={showMore ? "Show less" : "Show more"}
              >
                {showMore ? (
                  <ChevronUpIcon className="h-5 w-5" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded view with suggestions */}
      {showMore && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <PaperSuggestions 
            currentPaperId={paper.id}
            category={paper.category} 
            limit={3}
          />
        </div>
      )}
    </div>
  );
};

export default PaperCard; 