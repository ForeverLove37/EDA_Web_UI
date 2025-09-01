import React, { useState } from 'react'
import axios from 'axios'
import { 
  FileText, 
  Plus, 
  Download,
  Eye,
  Edit3,
  FileDown
} from 'lucide-react'

const StoryTelling = ({ projectId, stories, analyses, onUpdate }) => {
  const [isCreating, setIsCreating] = useState(false)
  const [selectedStory, setSelectedStory] = useState(null)
  const [newStoryTitle, setNewStoryTitle] = useState('')

  const createStory = async () => {
    if (!newStoryTitle.trim()) {
      alert('Please enter a story title')
      return
    }

    if (analyses.length === 0) {
      alert('No analyses available to create a story')
      return
    }

    try {
      const components = analyses.flatMap(analysis => 
        (analysis.insights || []).slice(0, 3).map(insight => ({
          type: 'insight',
          analysisId: analysis.id,
          insight: insight,
          title: `Insight from ${analysis.name}`
        }))
      ).slice(0, 5) // Limit to top 5 insights

      await axios.post(`/projects/${projectId}/stories`, {
        title: newStoryTitle,
        components: components,
        export_formats: ['pdf', 'html']
      })

      onUpdate()
      setNewStoryTitle('')
      setIsCreating(false)
      alert('Story created successfully!')
    } catch (error) {
      console.error('Error creating story:', error)
      alert('Failed to create story')
    }
  }

  const exportStory = async (story, format) => {
    // This would call a backend export endpoint
    alert(`Exporting story as ${format}...`)
    // Implement actual export functionality
  }

  return (
    <div className="space-y-6">
      {/* Create Story */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Create Story</h3>
        
        {!isCreating ? (
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            <span>Create New Story</span>
          </button>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Story Title
              </label>
              <input
                type="text"
                value={newStoryTitle}
                onChange={(e) => setNewStoryTitle(e.target.value)}
                placeholder="Enter a title for your story"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Available Insights</h4>
              <div className="bg-gray-50 p-4 rounded-lg max-h-40 overflow-auto">
                {analyses.length === 0 ? (
                  <p className="text-gray-500 text-sm">No analyses available</p>
                ) : (
                  <div className="space-y-2">
                    {analyses.map((analysis) => (
                      <div key={analysis.id} className="text-sm">
                        <div className="font-medium text-gray-900">{analysis.name}</div>
                        <div className="text-gray-600">
                          {analysis.insights?.length || 0} insights
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={createStory}
                disabled={!newStoryTitle.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Story
              </button>
              <button
                onClick={() => setIsCreating(false)}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Stories List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Your Stories</h3>
          <span className="text-sm text-gray-500">
            {stories.length} story{stories.length !== 1 ? 's' : ''}
          </span>
        </div>

        {stories.length === 0 ? (
          <div className="bg-gray-50 p-12 rounded-lg text-center">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No stories yet</h4>
            <p className="text-gray-600">Create your first story to share insights</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {stories.map((story) => (
              <div key={story.id} className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-medium text-gray-900">{story.title}</h4>
                    <p className="text-sm text-gray-500">
                      {new Date(story.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => exportStory(story, 'pdf')}
                      className="flex items-center space-x-1 text-gray-600 hover:text-gray-800"
                      title="Export as PDF"
                    >
                      <FileDown size={16} />
                      <span className="text-sm">PDF</span>
                    </button>
                    <button
                      onClick={() => exportStory(story, 'html')}
                      className="flex items-center space-x-1 text-gray-600 hover:text-gray-800"
                      title="Export as HTML"
                    >
                      <Download size={16} />
                      <span className="text-sm">HTML</span>
                    </button>
                    <button
                      onClick={() => setSelectedStory(story)}
                      className="flex items-center space-x-1 text-gray-600 hover:text-gray-800"
                      title="View Story"
                    >
                      <Eye size={16} />
                    </button>
                  </div>
                </div>

                {/* Story Preview */}
                <div className="prose prose-sm max-w-none mb-4">
                  <div 
                    className="text-gray-700 line-clamp-3"
                    dangerouslySetInnerHTML={{ 
                      __html: story.narrative?.replace(/\n/g, '<br/>') || 'No narrative generated yet' 
                    }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>
                    {typeof story.components === 'object' ? Object.keys(story.components).length : 0} components
                  </span>
                  <span>
                    {story.export_formats?.join(', ') || 'No export formats'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Story Detail Modal */}
      {selectedStory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">{selectedStory.title}</h2>
                <button
                  onClick={() => setSelectedStory(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="prose max-w-none">
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: selectedStory.narrative?.replace(/\n/g, '<br/>') || 'No narrative available' 
                  }}
                />
              </div>

              <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Story Components</h3>
                <div className="grid grid-cols-1 gap-3">
                  {selectedStory.components && typeof selectedStory.components === 'object' ? (
                    Object.entries(selectedStory.components).map(([key, component]) => (
                      <div key={key} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex items-center justify-between mb-2">
                          <strong className="text-gray-900">{component.title || 'Component'}</strong>
                          <span className="text-sm text-gray-500 capitalize">{component.type}</span>
                        </div>
                        {component.insight && (
                          <p className="text-gray-700 text-sm">
                            {component.insight.message || component.insight.analysis}
                          </p>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500">No components available</p>
                  )}
                </div>
              </div>

              <div className="mt-8 flex space-x-4">
                <button
                  onClick={() => exportStory(selectedStory, 'pdf')}
                  className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                >
                  <FileDown size={16} />
                  <span>Export PDF</span>
                </button>
                <button
                  onClick={() => exportStory(selectedStory, 'html')}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  <Download size={16} />
                  <span>Export HTML</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoryTelling