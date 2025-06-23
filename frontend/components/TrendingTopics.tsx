import React from 'react';
import { FireIcon } from '@heroicons/react/24/outline';
import { CATEGORY_MAP } from '../lib/categories';

// Top trending topics with description and official arXiv categories
const TRENDING_TOPICS = [
  {
    id: 'large-language-models',
    name: 'Large Language Models',
    categories: ['cs.CL', 'cs.AI', 'cs.LG'],
    description: 'Research on LLMs like GPT-4 and Gemini'
  },
  {
    id: 'diffusion-models',
    name: 'Diffusion Models',
    categories: ['cs.CV', 'cs.LG', 'eess.IV'],
    description: 'Image generation and stable diffusion'
  },
  {
    id: 'reinforcement-learning',
    name: 'Reinforcement Learning',
    categories: ['cs.LG', 'cs.AI', 'cs.NE'],
    description: 'RL with human feedback (RLHF)'
  },
  {
    id: 'multimodal-ai',
    name: 'Multimodal AI',
    categories: ['cs.CV', 'cs.CL', 'cs.LG'],
    description: 'Models that combine text, images, and audio'
  },
  {
    id: 'quantum-computing',
    name: 'Quantum Computing',
    categories: ['quant-ph', 'cs.ET', 'physics.comp-ph'],
    description: 'Quantum algorithms and hardware'
  }
];

interface TrendingTopicsProps {
  onSelectTopic: (categories: string[]) => void;
}

const TrendingTopics: React.FC<TrendingTopicsProps> = ({ onSelectTopic }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
      <div className="flex items-center mb-4">
        <FireIcon className="h-5 w-5 text-red-500 mr-2" />
        <h2 className="text-lg font-bold">Trending Research Areas</h2>
      </div>
      
      <div className="space-y-4">
        {TRENDING_TOPICS.map(topic => (
          <div 
            key={topic.id}
            onClick={() => onSelectTopic(topic.categories)}
            className="cursor-pointer group"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-gray-900 group-hover:text-blue-600 transition">{topic.name}</h3>
                <p className="text-sm text-gray-500 mt-1">{topic.description}</p>
              </div>
              <div className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full group-hover:bg-blue-100 group-hover:text-blue-600 transition">
                Explore
              </div>
            </div>
            <div className="flex gap-1 mt-2">
              {topic.categories.map(category => (
                <span 
                  key={category} 
                  className="text-xs bg-gray-50 text-gray-500 px-2 py-0.5 rounded"
                  title={CATEGORY_MAP[category]}
                >
                  {category}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingTopics; 