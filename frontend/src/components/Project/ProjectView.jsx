import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { 
  Database, 
  BarChart3, 
  MessageSquare, 
  FileText, 
  Plus,
  Download,
  Play
} from 'lucide-react'

import DataSourceManager from './DataSourceManager'
import AnalysisDashboard from './AnalysisDashboard'
import AIAssistant from './AIAssistant'
import StoryTelling from './StoryTelling'

const ProjectView = () => {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [activeTab, setActiveTab] = useState('data')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProject()
  }, [projectId])

  const fetchProject = async () => {
    try {
      const response = await axios.get(`/projects/${projectId}`)
      setProject(response.data)
    } catch (error) {
      console.error('Error fetching project:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Project not found</h3>
      </div>
    )
  }

  const tabs = [
    { id: 'data', name: 'Data Sources', icon: Database },
    { id: 'analysis', name: 'Analysis', icon: BarChart3 },
    { id: 'assistant', name: 'AI Assistant', icon: MessageSquare },
    { id: 'stories', name: 'Stories', icon: FileText },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{project.name}</h2>
          <p className="text-gray-600 dark:text-gray-400">{project.description}</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Play size={16} />
            <span>Run Analysis</span>
          </button>
          
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Download size={16} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <Database className="text-blue-600" size={20} />
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{project.data_sources?.length || 0}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">Data Sources</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <BarChart3 className="text-green-600" size={20} />
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{project.analyses?.length || 0}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">Analyses</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <MessageSquare className="text-purple-600" size={20} />
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{project.analyses?.reduce((acc, a) => acc + (a.insights?.length || 0), 0) || 0}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">Insights</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <FileText className="text-orange-600" size={20} />
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">{project.stories?.length || 0}</h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">Stories</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-dark-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  isActive
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-dark-600'
                }`}
              >
                <Icon size={18} />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'data' && (
          <DataSourceManager 
            projectId={projectId} 
            dataSources={project.data_sources || []}
            onUpdate={fetchProject}
          />
        )}
        
        {activeTab === 'analysis' && (
          <AnalysisDashboard 
            projectId={projectId}
            analyses={project.analyses || []}
            dataSources={project.data_sources || []}
            onUpdate={fetchProject}
          />
        )}
        
        {activeTab === 'assistant' && (
          <AIAssistant 
            projectId={projectId}
            projectName={project.name}
            dataSources={project.data_sources || []}
          />
        )}
        
        {activeTab === 'stories' && (
          <StoryTelling 
            projectId={projectId}
            stories={project.stories || []}
            analyses={project.analyses || []}
            onUpdate={fetchProject}
          />
        )}
      </div>
    </div>
  )
}

export default ProjectView