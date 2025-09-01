import React, { useState } from 'react'
import axios from 'axios'
import { 
  Database, 
  Plus, 
  FileText, 
  Server, 
  Cloud,
  Globe,
  FileType
} from 'lucide-react'

const DataSourceManager = ({ projectId, dataSources, onUpdate }) => {
  const [isConnecting, setIsConnecting] = useState(false)
  const [selectedType, setSelectedType] = useState('csv')

  const dataSourceTypes = [
    { id: 'csv', name: 'CSV File', icon: FileText, description: 'Upload a CSV file' },
    { id: 'excel', name: 'Excel File', icon: FileType, description: 'Upload an Excel spreadsheet' },
    { id: 'json', name: 'JSON Data', icon: FileText, description: 'Upload JSON data or file' },
    { id: 'postgres', name: 'PostgreSQL', icon: Server, description: 'Connect to PostgreSQL database' },
    { id: 'mysql', name: 'MySQL', icon: Server, description: 'Connect to MySQL database' },
    { id: 'bigquery', name: 'BigQuery', icon: Cloud, description: 'Connect to Google BigQuery' },
    { id: 's3', name: 'Amazon S3', icon: Cloud, description: 'Connect to S3 bucket' },
    { id: 'api', name: 'API Endpoint', icon: Globe, description: 'Connect to REST API' },
  ]

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setIsConnecting(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source_type', selectedType)
      formData.append('config', JSON.stringify({
        name: file.name,
        type: selectedType
      }))

      await axios.post(`/projects/${projectId}/data-sources`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      onUpdate()
      alert('Data source connected successfully!')
    } catch (error) {
      console.error('Error connecting data source:', error)
      alert('Failed to connect data source')
    } finally {
      setIsConnecting(false)
    }
  }

  const renderConnectionForm = () => {
    switch (selectedType) {
      case 'csv':
      case 'excel':
      case 'json':
        return (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Upload File
            </label>
            <input
              type="file"
              accept={selectedType === 'excel' ? '.xlsx,.xls' : selectedType === 'json' ? '.json' : '.csv'}
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
        )
      
      case 'postgres':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Host</label>
                <input type="text" className="mt-1 block w-full border-gray-300 rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Port</label>
                <input type="number" defaultValue="5432" className="mt-1 block w-full border-gray-300 rounded-md" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Database</label>
              <input type="text" className="mt-1 block w-full border-gray-300 rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              <input type="text" className="mt-1 block w-full border-gray-300 rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input type="password" className="mt-1 block w-full border-gray-300 rounded-md" />
            </div>
          </div>
        )
      
      default:
        return (
          <div className="text-center py-8">
            <p className="text-gray-500">Connection form for {selectedType} coming soon...</p>
          </div>
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Connection Panel */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Connect Data Source</h3>
        
        {/* Data Source Type Selection */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {dataSourceTypes.map((type) => {
            const Icon = type.icon
            const isSelected = selectedType === type.id
            
            return (
              <button
                key={type.id}
                onClick={() => setSelectedType(type.id)}
                className={`p-4 border rounded-lg text-center transition-colors ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon size={24} className="mx-auto mb-2 text-gray-600" />
                <div className="text-sm font-medium text-gray-900">{type.name}</div>
                <div className="text-xs text-gray-500">{type.description}</div>
              </button>
            )
          })}
        </div>

        {/* Connection Form */}
        {renderConnectionForm()}

        {isConnecting && (
          <div className="mt-4 flex items-center space-x-2 text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span>Connecting to data source...</span>
          </div>
        )}
      </div>

      {/* Existing Data Sources */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Connected Data Sources</h3>
        
        {dataSources.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <Database size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">No data sources connected yet</p>
            <p className="text-sm text-gray-400">Connect your first data source to start analyzing</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dataSources.map((source) => (
              <div key={source.id} className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between mb-3">
                  <Database size={20} className="text-blue-600" />
                  <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                    {source.type}
                  </span>
                </div>
                
                <h4 className="font-medium text-gray-900 mb-2">{source.name}</h4>
                
                {source.data_preview && (
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>{source.data_preview.row_count} rows</div>
                    <div>{source.data_preview.column_count} columns</div>
                    <div className="text-xs text-gray-400">
                      Connected {new Date(source.created_at).toLocaleDateString()}
                    </div>
                  </div>
                )}
                
                {source.data_profile && source.data_profile.quality_issues && (
                  <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-xs text-yellow-800">
                      {source.data_profile.quality_issues.length} data quality issues detected
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DataSourceManager