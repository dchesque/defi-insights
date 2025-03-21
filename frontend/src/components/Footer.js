import React from 'react';
import { Link } from 'react-router-dom';
import { FaTwitter, FaDiscord, FaGithub, FaLinkedin } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer className="bg-[#1A1C31] py-12 px-6 md:px-12">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-600 rounded-full w-8 h-8 flex items-center justify-center mr-2">
                <span className="text-white font-bold">B</span>
              </div>
              <span className="font-bold">BaseMind<span className="text-indigo-400">.ai</span></span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
  <span className="gradient-text">Análise de Criptomoedas com IA</span>
</h1>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white"><FaTwitter /></a>
              <a href="#" className="text-gray-400 hover:text-white"><FaDiscord /></a>
              <a href="#" className="text-gray-400 hover:text-white"><FaGithub /></a>
              <a href="#" className="text-gray-400 hover:text-white"><FaLinkedin /></a>
            </div>
          </div>
          
          <div className="col-span-1">
            <h3 className="font-medium text-white mb-4">Product</h3>
            <ul className="space-y-3 text-sm">
              <li><Link to="/features" className="text-gray-400 hover:text-white">Features</Link></li>
              <li><Link to="/pricing" className="text-gray-400 hover:text-white">Pricing</Link></li>
              <li><Link to="/api" className="text-gray-400 hover:text-white">API</Link></li>
              <li><Link to="/docs" className="text-gray-400 hover:text-white">Documentation</Link></li>
            </ul>
          </div>
          
          <div className="col-span-1">
            <h3 className="font-medium text-white mb-4">Company</h3>
            <ul className="space-y-3 text-sm">
              <li><Link to="/about" className="text-gray-400 hover:text-white">About</Link></li>
              <li><Link to="/blog" className="text-gray-400 hover:text-white">Blog</Link></li>
              <li><Link to="/careers" className="text-gray-400 hover:text-white">Careers</Link></li>
              <li><Link to="/contact" className="text-gray-400 hover:text-white">Contact</Link></li>
            </ul>
          </div>
          
          <div className="col-span-1">
            <h3 className="font-medium text-white mb-4">Resources</h3>
            <ul className="space-y-3 text-sm">
              <li><Link to="/community" className="text-gray-400 hover:text-white">Community</Link></li>
              <li><Link to="/help" className="text-gray-400 hover:text-white">Help Center</Link></li>
              <li><Link to="/privacy" className="text-gray-400 hover:text-white">Privacy Policy</Link></li>
              <li><Link to="/terms" className="text-gray-400 hover:text-white">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-12 pt-8 text-center text-sm text-gray-400">
          <p>© 2025 BaseMind.ai. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;