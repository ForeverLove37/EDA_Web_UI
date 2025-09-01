import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Send, 
  Brain, 
  Lightbulb,
  MessageSquare,
  Zap
} from 'lucide-react'

const AIAssistant = ({ projectId, projectName, dataSources }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [insights, setInsights] = useState([])

  useEffect(() => {
    // Load initial insights if we have data sources
    if (dataSources.length > 0) {
      generateInitialInsights()
    }
  }, [dataSources])

  const generateInitialInsights = async () => {
    try {
      const response = await axios.post(`/projects/${projectId}/analyze`, {
        name: 'Initial Analysis',
        analysis_type: 'eda',
        parameters: {}
      })
      
      setInsights(response.data.insights || [])
      
      // Add welcome message with insights
      setMessages([
        {
          type: 'ai',
          content: `Welcome to your ${projectName} project! I've analyzed your data and found some interesting insights. How can I help you explore further?`,
          timestamp: new Date()
        }
      ])
    } catch (error) {
      console.error('Error generating insights:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post(`/projects/${projectId}/ask`, {
        question: input
      })

      const aiMessage = {
        type: 'ai',
        content: response.data.answer,
        confidence: response.data.confidence,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage = {
        type: 'ai',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        isError: true,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickQuestion = async (question) => {
    setInput(question)
    // Small delay to allow input to update
    setTimeout(() => {
      handleSendMessage()
    }, 100)
  }

  const quickQuestions = [
    "What are the main trends in this data?",
    "Show me summary statistics",
    "Are there any outliers or anomalies?",
    "What correlations exist between variables?",
    "Suggest next steps for analysis"
  ]

  return (
    <div className="flex h-[600px] bg-white rounded-lg shadow-sm border">
      {/* Insights Panel */}
      <div className="w-80 border-r border-gray-200 p-4 overflow-auto">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb size={20} className="text-yellow-600" />
          <h3 className="font-medium text-gray-900">AI Insights</h3>
        </div>

        {insights.length === 0 ? (
          <div className="text-center py-8">
            <Brain size={32} className="mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500 text-sm">No insights yet</p>
            <p className="text-gray-400 text-xs">Connect data to generate insights</p>
          </div>
        ) : (
          <div className="space-y-3">
            {insights.slice(0, 5).map((insight, index) => (
              <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex items-start space-x-2">
                  <Zap size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-blue-900">
                      {insight.insight?.message || insight.insight?.analysis || 'New insight'}
                    </p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                        {insight.type}
                      </span>
                      <span className="text-xs text-blue-500">
                        {Math.round(insight.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quick Questions */}
        <div className="mt-6">
          <h4 className="font-medium text-gray-900 mb-3 text-sm">Quick Questions</h4>
          <div className="space-y-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                className="w-full text-left p-2 text-sm text-gray-700 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Panel */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Welcome to AI Assistant</h3>
              <p className="text-gray-500">Ask me anything about your data</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.isError
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  {message.confidence && (
                    <div className="text-xs opacity-70 mt-1">
                      Confidence: {Math.round(message.confidence * 100)}%
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-600"></div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask a question about your data..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAssistant