import React from 'react'
import { useAuth } from '../../hooks/useAuth'
import { LogOut, User, Sun, Moon } from 'lucide-react'

const Header = () => {
  const { user, logout, theme, toggleTheme } = useAuth()

  return (
    <header className="bg-white dark:bg-dark-800 shadow-sm border-b border-gray-200 dark:border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Project Phoenix</h1>
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 text-gray-600 dark:text-gray-300 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
            <User size={20} />
            <span>{user?.email}</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center space-x-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header