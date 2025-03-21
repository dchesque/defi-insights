import React from 'react';
import { Link } from 'react-router-dom';
import { FaGithub } from 'react-icons/fa';

const Header = () => {
  return (
    <header className="py-4 px-6 md:px-12 flex justify-between items-center">
      <Link to="/" className="flex items-center">
        <div className="bg-indigo-600 rounded-full w-8 h-8 flex items-center justify-center mr-2">
          <span className="text-white font-bold">B</span>
        </div>
        <span className="font-bold">BaseMind<span className="text-indigo-400">.ai</span></span>
      </Link>
      
      <nav className="hidden md:flex items-center space-x-6">
        <Link to="/" className="text-gray-300 hover:text-white">Home</Link>
        <Link to="/features" className="text-gray-300 hover:text-white">Features</Link>
        <Link to="/about" className="text-gray-300 hover:text-white">About</Link>
        <Link to="/contact" className="text-gray-300 hover:text-white">Contact</Link>
      </nav>
      
      <div>
        <a href="https://github.com/yourusername/basemind-ai" 
           target="_blank" 
           rel="noopener noreferrer"
           className="px-4 py-2 border border-indigo-600 rounded text-indigo-400 hover:bg-indigo-600 hover:text-white transition-colors">
          Sign In
        </a>
      </div>
    </header>
  );
};

export default Header;