import React from 'react';
import Link from 'next/link';
import { HashtagIcon } from '@heroicons/react/24/outline';
import { CATEGORY_MAP } from '../lib/categories';

// Define related category mappings based on arXiv domain knowledge
const RELATED_CATEGORIES: Record<string, string[]> = {
  // Computer Science
  'cs.AI': ['cs.LG', 'cs.CL', 'cs.NE', 'cs.RO', 'cs.CV'],
  'cs.CL': ['cs.AI', 'cs.LG', 'cs.IR', 'stat.ML'],
  'cs.LG': ['cs.AI', 'cs.CL', 'cs.CV', 'stat.ML', 'math.OC'],
  'cs.CV': ['cs.LG', 'cs.AI', 'cs.RO', 'cs.NE', 'eess.IV'],
  'cs.RO': ['cs.AI', 'cs.CV', 'cs.LG', 'cs.SY'],
  'cs.NE': ['cs.AI', 'cs.LG', 'q-bio.NC'],
  'cs.IR': ['cs.CL', 'cs.AI', 'cs.LG'],
  'cs.HC': ['cs.AI', 'cs.SE'],
  'cs.SE': ['cs.HC', 'cs.AI', 'stat.CO'],
  
  // Machine Learning from Statistics
  'stat.ML': ['cs.LG', 'cs.AI', 'math.ST', 'cs.CV', 'cs.CL'],
  
  // Physics
  'physics.comp-ph': ['cs.LG', 'math.OC'],
  'quant-ph': ['physics.comp-ph', 'cs.ET'],
  
  // Math
  'math.OC': ['cs.LG', 'math.ST', 'stat.ML'],
  'math.ST': ['stat.ML', 'math.OC', 'cs.LG'],
  
  // Biology
  'q-bio.NC': ['cs.NE', 'cs.AI', 'q-bio.QM'],
  
  // Electrical Engineering
  'eess.IV': ['cs.CV', 'eess.SP', 'cs.LG']
};

// Popular categories to show when no specific category is selected
const POPULAR_CATEGORIES = [
  'cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'stat.ML', 
  'cs.RO', 'quant-ph', 'eess.IV', 'cs.NE'
];

interface RelatedTagsProps {
  currentCategory: string | null;
  onCategorySelect: (category: string) => void;
}

const RelatedTags: React.FC<RelatedTagsProps> = ({ currentCategory, onCategorySelect }) => {
  // Get related categories or popular ones if no category selected
  const getRelatedCategories = (): string[] => {
    if (!currentCategory) return POPULAR_CATEGORIES;
    
    return RELATED_CATEGORIES[currentCategory] || POPULAR_CATEGORIES.slice(0, 6);
  };

  const relatedCategories = getRelatedCategories();

  return (
    <div className="mb-6">
      <h2 className="text-lg font-bold mb-3">
        {currentCategory ? 'Related Categories' : 'Popular Categories'}
      </h2>
      <div className="flex flex-wrap gap-2">
        {relatedCategories.map(category => (
          <button
            key={category}
            onClick={() => onCategorySelect(category)}
            className={`
              px-3 py-2 rounded-full text-sm font-medium
              flex items-center bg-white border border-gray-200
              transition-all hover:bg-blue-50 hover:border-blue-300
              hover:shadow-sm hover:scale-105
              ${category === currentCategory ? 'bg-blue-100 border-blue-300 text-blue-700' : 'text-gray-700'}
            `}
            title={category}
          >
            <HashtagIcon className="h-3.5 w-3.5 mr-1" />
            <span>{CATEGORY_MAP[category] || category}</span>
          </button>
        ))}
        
        <Link 
          href="/explore" 
          className="px-3 py-2 rounded-full text-sm font-medium
                    flex items-center bg-white border border-gray-200
                    transition-all hover:bg-gray-50 hover:border-gray-300
                    hover:shadow-sm"
        >
          <span className="text-gray-700">More Categories...</span>
        </Link>
      </div>
    </div>
  );
};

export default RelatedTags; 