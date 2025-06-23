import React, { useState } from 'react';
import { MAIN_CATEGORIES, Category, MainCategory } from '../lib/categories';
import { ChevronRightIcon, ChevronDownIcon } from '@heroicons/react/24/outline';

interface CategoryExplorerProps {
  onSelectCategory: (categoryId: string) => void;
}

const CategoryExplorer: React.FC<CategoryExplorerProps> = ({ onSelectCategory }) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['cs']));

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const renderSubcategory = (category: Category, depth: number = 0) => {
    const hasSubcategories = category.subcategories && category.subcategories.length > 0;
    const isExpanded = expandedCategories.has(category.id);
    
    return (
      <div key={category.id} className="category-item">
        <div 
          className={`flex items-center py-2 px-3 hover:bg-gray-50 rounded-md cursor-pointer
                    ${depth > 0 ? 'ml-' + (depth * 4) : ''}`}
          onClick={() => hasSubcategories ? toggleCategory(category.id) : onSelectCategory(category.id)}
        >
          {hasSubcategories ? (
            <span className="mr-1">
              {isExpanded ? (
                <ChevronDownIcon className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRightIcon className="h-4 w-4 text-gray-500" />
              )}
            </span>
          ) : (
            <span className="w-4 mr-1"></span>
          )}
          <span 
            className="flex-1 text-sm font-medium hover:text-blue-600"
            title={category.description}
          >
            {category.id} - {category.name}
          </span>
          {!hasSubcategories && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSelectCategory(category.id);
              }}
              className="ml-2 text-xs text-gray-500 hover:text-blue-600 px-2 py-1 rounded-full bg-gray-100 hover:bg-blue-50"
            >
              View
            </button>
          )}
        </div>
        
        {hasSubcategories && isExpanded && (
          <div className="subcategories">
            {category.subcategories!.map(subcat => renderSubcategory(subcat, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h2 className="text-lg font-bold mb-4">ArXiv Category Explorer</h2>
      <div className="category-tree max-h-[60vh] overflow-y-auto pr-2">
        {MAIN_CATEGORIES.map(mainCategory => (
          <div key={mainCategory.id} className="main-category mb-3">
            <div 
              className="flex items-center py-2 font-medium text-gray-900 hover:text-blue-700 cursor-pointer"
              onClick={() => toggleCategory(mainCategory.id)}
            >
              {expandedCategories.has(mainCategory.id) ? (
                <ChevronDownIcon className="h-5 w-5 mr-1" />
              ) : (
                <ChevronRightIcon className="h-5 w-5 mr-1" />
              )}
              {mainCategory.name}
            </div>
            
            {expandedCategories.has(mainCategory.id) && (
              <div className="subcategories">
                {mainCategory.subcategories.map(subcat => renderSubcategory(subcat))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryExplorer; 