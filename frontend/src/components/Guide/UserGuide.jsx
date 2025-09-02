import React from 'react';
import { BookOpen, Database, BarChart3, MessageSquare, FileText, Users, Plus, Download } from 'lucide-react';

const UserGuide = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <BookOpen className="h-12 w-12 text-blue-600 mr-3" />
          <h1 className="text-4xl font-bold text-gray-900">Project Phoenix User Guide</h1>
        </div>
        <p className="text-lg text-gray-600">
          A comprehensive guide to using the Symbiotic Analysis Environment
        </p>
      </div>

      {/* Quick Start Section */}
      <section className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-blue-900 mb-4">🚀 Quick Start</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center mb-3">
              <Users className="h-6 w-6 text-blue-600 mr-2" />
              <h3 className="font-semibold">1. Login</h3>
            </div>
            <p className="text-sm text-gray-600">
              Use admin@phoenix.com / Admin123! or register a new account
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center mb-3">
              <Plus className="h-6 w-6 text-green-600 mr-2" />
              <h3 className="font-semibold">2. Create Project</h3>
            </div>
            <p className="text-sm text-gray-600">
              Start by creating a new analysis project
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center mb-3">
              <Database className="h-6 w-6 text-purple-600 mr-2" />
              <h3 className="font-semibold">3. Add Data</h3>
            </div>
            <p className="text-sm text-gray-600">
              Connect your data sources to begin analysis
            </p>
          </div>
        </div>
      </section>

      {/* Main Features Section */}
      <section>
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">✨ Key Features</h2>
        
        <div className="space-y-6">
          {/* Data Sources */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center mb-4">
              <Database className="h-8 w-8 text-blue-600 mr-3" />
              <h3 className="text-xl font-semibold">Data Sources</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Connect multiple data sources for comprehensive analysis:
            </p>
            <ul className="grid md:grid-cols-2 gap-2 text-sm text-gray-600">
              <li>• CSV Files</li>
              <li>• Excel Spreadsheets</li>
              <li>• JSON Data</li>
              <li>• PostgreSQL Databases</li>
              <li>• MySQL Databases</li>
              <li>• S3 Buckets</li>
              <li>• API Endpoints</li>
              <li>• PDF Documents</li>
            </ul>
          </div>

          {/* AI Analysis */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center mb-4">
              <BarChart3 className="h-8 w-8 text-green-600 mr-3" />
              <h3 className="text-xl font-semibold">AI-Powered Analysis</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Leverage AI to automatically analyze your data and generate insights:
            </p>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Analysis Types</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• Statistical Analysis</li>
                  <li>• Clustering Detection</li>
                  <li>• Anomaly Detection</li>
                  <li>• Correlation Analysis</li>
                  <li>• Seasonality Patterns</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Features</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• Automated Data Profiling</li>
                  <li>• Quality Assessment</li>
                  <li>• Proactive Insights</li>
                  <li>• Confidence Scoring</li>
                  <li>• Actionable Recommendations</li>
                </ul>
              </div>
            </div>
          </div>

          {/* AI Assistant */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center mb-4">
              <MessageSquare className="h-8 w-8 text-purple-600 mr-3" />
              <h3 className="text-xl font-semibold">AI Assistant</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Chat with your data using natural language queries:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 italic">
                "What's the average sales by region?"<br/>
                "Show me trends over time"<br/>
                "Identify outliers in the dataset"<br/>
                "Compare performance between categories"
              </p>
            </div>
          </div>

          {/* Storytelling */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center mb-4">
              <FileText className="h-8 w-8 text-orange-600 mr-3" />
              <h3 className="text-xl font-semibold">Storytelling & Export</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Transform insights into compelling narratives and export them:
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <Download className="h-5 w-5" />
              <span>Export to PDF, HTML, PowerPoint</span>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">📋 Typical Workflow</h2>
        
        <div className="space-y-4">
          <div className="flex items-start">
            <div className="bg-blue-600 text-white rounded-full h-8 w-8 flex items-center justify-center mr-4 flex-shrink-0">1</div>
            <div>
              <h3 className="font-semibold">Create Project</h3>
              <p className="text-gray-600 text-sm">Start a new analysis project with a descriptive name</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="bg-green-600 text-white rounded-full h-8 w-8 flex items-center justify-center mr-4 flex-shrink-0">2</div>
            <div>
              <h3 className="font-semibold">Connect Data Sources</h3>
              <p className="text-gray-600 text-sm">Add one or multiple data sources for analysis</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="bg-purple-600 text-white rounded-full h-8 w-8 flex items-center justify-center mr-4 flex-shrink-0">3</div>
            <div>
              <h3 className="font-semibold">Run AI Analysis</h3>
              <p className="text-gray-600 text-sm">Let AI perform initial analysis and generate insights</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="bg-orange-600 text-white rounded-full h-8 w-8 flex items-center justify-center mr-4 flex-shrink-0">4</div>
            <div>
              <h3 className="font-semibold">Explore with AI Assistant</h3>
              <p className="text-gray-600 text-sm">Ask questions and dive deeper into your data</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="bg-red-600 text-white rounded-full h-8 w-8 flex items-center justify-center mr-4 flex-shrink-0">5</div>
            <div>
              <h3 className="font-semibold">Create & Export Stories</h3>
              <p className="text-gray-600 text-sm">Build narratives and export reports for sharing</p>
            </div>
          </div>
        </div>
      </section>

      {/* Tips Section */}
      <section>
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">💡 Pro Tips</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-800 mb-2">Data Preparation</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Clean your data before uploading for best results</li>
              <li>• Use consistent formatting in your datasets</li>
              <li>• Include clear column headers</li>
            </ul>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-800 mb-2">AI Interaction</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Be specific with your questions</li>
              <li>• Ask follow-up questions based on insights</li>
              <li>• Use the assistant to validate your hypotheses</li>
            </ul>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-800 mb-2">Project Management</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Create separate projects for different analyses</li>
              <li>• Use descriptive project names</li>
              <li>• Regularly review and archive completed projects</li>
            </ul>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-800 mb-2">Exporting Results</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Use PDF for formal reports</li>
              <li>• HTML exports are great for web sharing</li>
              <li>• PowerPoint for presentations</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Support Section */}
      <section className="bg-blue-50 rounded-lg p-6 text-center">
        <h2 className="text-xl font-semibold text-blue-900 mb-4">Need Help?</h2>
        <p className="text-blue-700">
          The AI Assistant is always available to help you navigate the platform and answer any questions about your data analysis.
        </p>
      </section>
    </div>
  );
};

export default UserGuide;