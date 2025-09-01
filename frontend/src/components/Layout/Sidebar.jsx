import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  FolderPlus, 
  Database, 
  BarChart3, 
  MessageSquare, 
  FileText 
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'New Project', href: '/project/new', icon: FolderPlus },
    { name: 'Data Sources', href: '/data-sources', icon: Database },
    { name: 'Analysis', href: '/analysis', icon: BarChart3 },
    { name: 'AI Assistant', href: '/assistant', icon: MessageSquare },
    { name: 'Reports', href: '/reports', icon: FileText },
  ]

  return (
    <div className="w-64 bg-gray-900 text-white">
      <div className="p-6">
        <h2 className="text-xl font-semibold">Phoenix</h2>
        <p className="text-gray-400 text-sm">Symbiotic Analysis</p>
      </div>
      
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

export default Sidebar