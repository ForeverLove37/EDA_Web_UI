import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { 
  Plus, 
  Folder, 
  BarChart3, 
  TrendingUp, 
  AlertCircle 
} from 'lucide-react'

const Dashboard = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/projects')
      setProjects(response.data)
    } catch (error) {
      console.error('Error fetching projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const createNewProject = async () => {
    const projectName = prompt('Enter project name:')
    if (!projectName) return

    try {
      const response = await axios.post('/projects', {
        name: projectName,
        description: ''
      })
      setProjects([...projects, response.data])
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Failed to create project')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600">Welcome to your symbiotic analysis environment</p>
        </div>
        <button
          onClick={createNewProject}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          <span>New Project</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <Folder className="text-blue-600" size={24} />
            <div>
              <h3 className="text-2xl font-bold">{projects.length}</h3>
              <p className="text-gray-600">Total Projects</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <BarChart3 className="text-green-600" size={24} />
            <div>
              <h3 className="text-2xl font-bold">
                {projects.reduce((acc, project) => acc + (project.analyses?.length || 0), 0)}
              </h3>
              <p className="text-gray-600">Analyses</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <TrendingUp className="text-purple-600" size={24} />
            <div>
              <h3 className="text-2xl font-bold">
                {projects.reduce((acc, project) => acc + (project.data_sources?.length || 0), 0)}
              </h3>
              <p className="text-gray-600">Data Sources</p>
            </div>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Your Projects</h3>
        
        {projects.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow-sm border text-center">
            <Folder size={48} className="mx-auto text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h4>
            <p className="text-gray-600 mb-4">Create your first project to start analyzing data</p>
            <button
              onClick={createNewProject}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Create Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Link
                key={project.id}
                to={`/project/${project.id}`}
                className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <Folder size={24} className="text-blue-600" />
                  <span className="text-sm text-gray-500">
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <h4 className="font-semibold text-gray-900 mb-2">{project.name}</h4>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {project.description || 'No description'}
                </p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{project.data_sources?.length || 0} data sources</span>
                  <span>{project.analyses?.length || 0} analyses</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard