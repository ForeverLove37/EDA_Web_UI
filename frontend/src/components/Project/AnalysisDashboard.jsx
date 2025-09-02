import React, { useState } from 'react'
import axios from 'axios'
import { 
  BarChart3, 
  Plus, 
  Filter,
  Download,
  Eye,
  Calendar
} from 'lucide-react'

const AnalysisDashboard = ({ projectId, analyses, dataSources, onUpdate }) => {
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  const [isRunning, setIsRunning] = useState(false)

  const runAnalysis = async (analysisType) => {
    if (dataSources.length === 0) {
      alert('Please connect a data source first')
      return
    }

    setIsRunning(true)

    try {
      const response = await axios.post(`/projects/${projectId}/analyze`, {
        name: `${analysisType} Analysis`,
        analysis_type: analysisType,
        parameters: {}
      })

      onUpdate()
      setSelectedAnalysis(response.data)
      alert('Analysis completed successfully!')
    } catch (error) {
      console.error('Error running analysis:', error)
      alert('Failed to run analysis')
    } finally {
      setIsRunning(false)
    }
  }

  const analysisTypes = [
    {
      id: 'eda',
      name: 'Exploratory Analysis',
      description: 'Comprehensive data exploration and summary statistics',
      icon: BarChart3,
      color: 'blue'
    },
    {
      id: 'statistical',
      name: 'Statistical Tests',
      description: 'Hypothesis testing and statistical significance',
      icon: Filter,
      color: 'green'
    },
    {
      id: 'clustering',
      name: 'Clustering',
      description: 'Identify patterns and groups in your data',
      icon: Eye,
      color: 'purple'
    },
    {
      id: 'timeseries',
      name: 'Time Series',
      description: 'Analyze trends and seasonality over time',
      icon: Calendar,
      color: 'orange'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Analysis Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Run Analysis</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {analysisTypes.map((type) => {
            const Icon = type.icon
            
            return (
              <button
                key={type.id}
                onClick={() => runAnalysis(type.id)}
                disabled={isRunning}
                className={`p-4 border rounded-lg text-left transition-colors ${
                  isRunning
                    ? 'opacity-50 cursor-not-allowed'
                    : `hover:border-${type.color}-300 hover:bg-${type.color}-50`
                }`}
              >
                <div className={`flex items-center justify-center w-10 h-10 bg-${type.color}-100 rounded-lg mb-3`}>
                  <Icon size={20} className={`text-${type.color}-600`} />
                </div>
                
                <h4 className="font-medium text-gray-900 mb-1">{type.name}</h4>
                <p className="text-sm text-gray-600">{type.description}</p>
                
                {isRunning && (
                  <div className="mt-2 flex items-center space-x-2 text-blue-600">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                    <span className="text-xs">Running...</span>
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Analysis Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Analysis Results</h3>
          <span className="text-sm text-gray-500">
            {analyses.length} analysis{analyses.length !== 1 ? 'es' : ''}
          </span>
        </div>

        {analyses.length === 0 ? (
          <div className="bg-gray-50 p-12 rounded-lg text-center">
            <BarChart3 size={48} className="mx-auto text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h4>
            <p className="text-gray-600">Run your first analysis to see results here</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-medium text-gray-900">{analysis.name}</h4>
                    <p className="text-sm text-gray-500">
                      {new Date(analysis.created_at).toLocaleDateString()} • {analysis.type}
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600">
                      <Download size={16} />
                    </button>
                    <button 
                      onClick={() => setSelectedAnalysis(analysis)}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <Eye size={16} />
                    </button>
                  </div>
                </div>

                {/* Insights Preview */}
                {analysis.insights && analysis.insights.length > 0 && (
                  <div className="space-y-3">
                    <h5 className="font-medium text-gray-900 text-sm">Key Insights</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {analysis.insights.slice(0, 4).map((insight, index) => (
                        <div key={index} className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                          <p className="text-sm text-blue-900 line-clamp-2">
                            {insight.insight?.message || insight.insight?.analysis || 'Insight found'}
                          </p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                              {insight.type}
                            </span>
                            <span className="text-xs text-blue-500">
                              {Math.round(insight.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {analysis.insights.length > 4 && (
                      <p className="text-sm text-gray-500 text-center">
                        +{analysis.insights.length - 4} more insights
                      </p>
                    )}
                  </div>
                )}

                {(!analysis.insights || analysis.insights.length === 0) && (
                  <p className="text-gray-500 text-sm">No insights generated yet</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Detail Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedAnalysis.name}
                </h3>
                <button
                  onClick={() => setSelectedAnalysis(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div className="prose max-w-none">
                <h4>Insights</h4>
                {selectedAnalysis.insights && selectedAnalysis.insights.length > 0 ? (
                  <div className="space-y-4">
                    {selectedAnalysis.insights.map((insight, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <strong className="text-gray-900">{insight.type}</strong>
                          <span className="text-sm text-gray-500">
                            Confidence: {Math.round(insight.confidence * 100)}%
                          </span>
                        </div>
                        <p className="text-gray-700">
                          {insight.insight?.message || insight.insight?.analysis || 'No message'}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No insights available</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalysisDashboard