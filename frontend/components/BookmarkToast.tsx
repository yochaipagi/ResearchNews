import React, { useState, useEffect } from 'react';
import { BookmarkIcon } from '@heroicons/react/24/solid';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface BookmarkToastProps {
  message: string;
  show: boolean;
  onClose: () => void;
}

const BookmarkToast: React.FC<BookmarkToastProps> = ({ message, show, onClose }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  if (!show) return null;

  return (
    <div className="fixed bottom-5 left-1/2 transform -translate-x-1/2 z-50 
                  bg-gray-800 text-white px-4 py-3 rounded-full 
                  shadow-lg flex items-center transition-all duration-300 ease-in-out">
      <BookmarkIcon className="h-5 w-5 mr-2 text-blue-400" />
      <span>{message}</span>
      <button 
        onClick={onClose} 
        className="ml-3 text-gray-300 hover:text-white"
        aria-label="Close"
      >
        <XMarkIcon className="h-4 w-4" />
      </button>
    </div>
  );
};

export default BookmarkToast; 