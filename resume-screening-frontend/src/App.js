import React, { useState } from 'react';
import './App.css';

function App() {
  const [jobDesc, setJobDesc] = useState('');
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobDesc.trim()) {
      setError('Please enter a job description.');
      return;
    }

    setError('');
    setLoading(true);
    setMatches([]);

    try {
      const response = await fetch('http://127.0.0.1:5000/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_description: jobDesc }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch from backend.');
      }

      const data = await response.json();
      setMatches(data.matches);
    } catch (err) {
      console.error(err);
      setError('Failed to connect to backend. Please make sure Flask is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>🔍 Resume Screening AI</h1>

      <form onSubmit={handleSubmit}>
        <textarea
          rows="8"
          cols="80"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          placeholder="Paste the job description here..."
          className="textarea"
        />
        <br />
        <button type="submit" className="submit-btn">Match Resumes</button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p className="loading">⏳ Matching resumes...</p>}

      {matches.length > 0 && (
        <div className="results">
          <h2>🎯 Top Matches</h2>
          <table className="results-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Person ID</th>
                <th>Match Score (%)</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((match, index) => (
                <tr key={index}>
                  <td>{match.name}</td>
                  <td>{match.person_id}</td>
                  <td>{(match.score * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
