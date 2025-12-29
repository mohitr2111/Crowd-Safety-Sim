// frontend/src/components/Header.jsx

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;

  const navLinks = [
    {
      path: '/',
      label: '🚀 Live AI Simulation',
      gradient: 'from-blue-600 to-purple-600'
    },
    {
      path: '/scenario-builder',
      label: '🎯 Scenario Builder',
      gradient: 'from-green-600 to-blue-600'
    },
    {
      path: '/comparison',
      label: '📊 AI vs Baseline',
      gradient: 'from-orange-600 to-red-600'
    }
  ];

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-8 py-6">
        {/* Title Section */}
        <div className="mb-4">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🚨 AI-Powered Crowd Safety Platform
          </h1>
          <p className="text-gray-600">
            Predictive AI for Stampede Prevention & Real-Time Intervention
          </p>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex gap-2 flex-wrap">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-6 py-2 rounded-lg font-semibold transition-all duration-200 ${
                isActive(link.path)
                  ? `bg-gradient-to-r ${link.gradient} text-white shadow-lg scale-105`
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 hover:scale-102'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Optional: Breadcrumbs or Status Indicator */}
        {location.pathname !== '/' && (
          <div className="mt-3 text-sm text-gray-500">
            <Link to="/" className="hover:text-blue-600">
              Home
            </Link>
            <span className="mx-2">/</span>
            <span className="text-gray-700">
              {location.pathname.replace('/', '').replace('-', ' ')}
            </span>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
