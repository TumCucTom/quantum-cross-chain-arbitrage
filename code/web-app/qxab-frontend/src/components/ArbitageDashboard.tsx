import React, { useState } from 'react';
import LiveDataGraph from './LiveDataGraph';
import { CssBaseline } from '@mui/material';

const ArbitrageDashboard: React.FC = () => {
  const [showGraph, setShowGraph] = useState(false);

  const handleGetLiveData = () => {
    setShowGraph(true);
  };

  const handleRunFullScript = () => {
    // Placeholder for full script execution logic
    runQAOA();
    alert("Run full script functionality coming soon!");
  };

  // Run QAOA on live data (stubbed API call)
  const runQAOA = async () => {
    try {
      
    } catch (error) {
      console.error("Error running QAOA:", error);
    }
  };

  return (
    <div className="dashboard-container">
      <h2>Arbitrage Opportunities Dashboard</h2>
      <div className="button-container">
        <button onClick={handleGetLiveData}>Get live data</button>
        <button onClick={handleRunFullScript}>Run full script</button>
      </div>
      {showGraph && <LiveDataGraph />}
    </div>
  );
};

export default ArbitrageDashboard;
