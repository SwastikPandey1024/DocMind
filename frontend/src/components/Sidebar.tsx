import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  const [isOpen, setIsOpen] = useState(true);

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  const menuItems = [
    { label: 'Dashboard', icon: '🏠', path: '/dashboard' },
    { label: 'Documents', icon: '📄', path: '/documents' },
    { label: 'Chat', icon: '💬', path: '/chat' },
    { label: 'Settings', icon: '⚙️', path: '/settings' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className={`transition-all duration-300 ${isOpen ? 'w-64' : 'w-20'} flex flex-col bg-white shadow dark:bg-gray-800`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4 dark:border-gray-700">
        {isOpen && (
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">DocuChat</h1>
            <p className="text-xs text-gray-600 dark:text-gray-400">v1.0</p>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {isOpen ? '←' : '→'}
        </button>
      </div>

      {/* Menu */}
      <nav className="flex-1 space-y-2 p-4">
        {menuItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full rounded-lg px-4 py-3 text-left transition-colors ${
              isActive(item.path)
                ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
            title={item.label}
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            {isOpen && <span className="font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* User Profile & Logout */}
      <div className="border-t border-gray-200 p-4 dark:border-gray-700">
        {isOpen && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.name}</p>
            <p className="text-xs text-gray-600 dark:text-gray-400">{user?.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600 hover:bg-red-100 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
        >
          {isOpen ? 'Logout' : '🚪'}
        </button>
      </div>
    </div>
  );
}
