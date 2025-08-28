import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [edaType, setEdaType] = useState('conventional');
  const [conventionalTool, setConventionalTool] = useState('ydata-profiling');
  const [aiTool, setAiTool] = useState('analyze');
  const [llmChoice, setLlmChoice] = useState('deepseek');
  const [transformationPrompt, setTransformationPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setIsLoading(true);
    setResult(null);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    let url = '';
    let config = {};

    if (edaType === 'conventional') {
      formData.append('tool', conventionalTool);
      url = '/api/eda/conventional';
      config = {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'text',
      };
    } else {
      formData.append('llm_choice', llmChoice);
      if (aiTool === 'analyze') {
        url = '/api/eda/ai/analyze';
      } else {
        formData.append('transformation_prompt', transformationPrompt);
        url = '/api/eda/ai/transform';
      }
      config = { headers: { 'Content-Type': 'multipart/form-data' } };
    }

    try {
      const response = await axios.post(url, formData, config);
      setResult(response.data);
    } catch (err) {
      setError('An error occurred. Please check the console for details.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderResult = () => {
    if (isLoading) return <div className="loader">Loading...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!result) return null;

    if (edaType === 'conventional') {
      return <iframe srcDoc={result} title="EDA Report" className="result-iframe" />;
    }
    
    if (aiTool === 'analyze') {
        return <pre className="result-json">{JSON.stringify(result.analysis, null, 2)}</pre>;
    }

    if (aiTool === 'transform') {
      const data = result.transformed_data;
      if (!data || data.length === 0) return <p>No data to display.</p>;
      
      const headers = Array.isArray(data) ? Object.keys(data[0]) : Object.keys(data);
      const rows = Array.isArray(data) ? data : [data];

      return (
        <table className="result-table">
          <thead>
            <tr>{headers.map(h => <th key={h}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>{headers.map(h => <td key={h}>{JSON.stringify(row[h])}</td>)}</tr>
            ))}
          </tbody>
        </table>
      );
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Comprehensive EDA Web Tool</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit} className="control-panel">
          <div className="form-section">
            <label htmlFor="file-upload">1. Upload Data File</label>
            <input id="file-upload" type="file" onChange={handleFileChange} />
          </div>

          <div className="form-section">
            <label>2. Choose EDA Type</label>
            <div>
              <input type="radio" id="conventional" name="edaType" value="conventional" checked={edaType === 'conventional'} onChange={() => setEdaType('conventional')} />
              <label htmlFor="conventional">Conventional EDA</label>
            </div>
            <div>
              <input type="radio" id="ai-powered" name="edaType" value="ai-powered" checked={edaType === 'ai-powered'} onChange={() => setEdaType('ai-powered')} />
              <label htmlFor="ai-powered">AI-Powered EDA</label>
            </div>
          </div>

          {edaType === 'conventional' && (
            <div className="form-section">
              <label htmlFor="conventional-tool">3. Select Tool</label>
              <select id="conventional-tool" value={conventionalTool} onChange={(e) => setConventionalTool(e.target.value)}>
                <option value="ydata-profiling">YData Profiling</option>
                <option value="sweetviz">Sweetviz</option>
                <option value="custom_plot">Custom Plot</option>
              </select>
            </div>
          )}

          {edaType === 'ai-powered' && (
            <>
              <div className="form-section">
                <label>3. Select AI Task & Model</label>
                <select value={aiTool} onChange={(e) => setAiTool(e.target.value)}>
                  <option value="analyze">Analyze Data</option>
                  <option value="transform">Transform Data</option>
                </select>
                <select value={llmChoice} onChange={(e) => setLlmChoice(e.target.value)}>
                  <option value="deepseek">Deepseek</option>
                  <option value="chataiapi">ChatAI API</option>
                </select>
              </div>
              {aiTool === 'transform' && (
                <div className="form-section">
                  <label htmlFor="transform-prompt">4. Transformation Prompt</label>
                  <textarea id="transform-prompt" value={transformationPrompt} onChange={(e) => setTransformationPrompt(e.target.value)} placeholder="e.g., Extract names and emails into JSON objects" />
                </div>
              )}
            </>
          )}

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Run EDA'}
          </button>
        </form>

        <div className="result-area">
          <h2>Results</h2>
          {renderResult()}
        </div>
      </main>
    </div>
  );
}

export default App;
