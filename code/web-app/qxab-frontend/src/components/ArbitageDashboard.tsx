import React, { useState } from 'react';
import LiveDataGraph from './LiveDataGraph';
import Grid from '@mui/material/Grid';
import { IconButton, Paper } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';

const ArbitrageDashboard: React.FC = () => {
  const [graphs, setGraphs] = useState<boolean[]>(Array(4).fill(false));

  const toggleGraph = (index: number) => {
    setGraphs((prevGraphs) => {
      const newGraphs = [...prevGraphs];
      newGraphs[index] = !newGraphs[index]; // Toggle visibility
      return newGraphs;
    });
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
        {/* Buttons to fetch data and run script */}
        <div className="button-container">
          <button onClick={() => setGraphs(Array(4).fill(true))}>Get live data</button>
          <button onClick={() => alert("Run full script functionality coming soon!")}>
            Run full script
          </button>
        </div>

        {/* 2x2 Grid Layout */}
        <div style={{ marginTop: '24px' }}>
          <Grid container spacing={2}>
          {graphs.map((show, index) => (
            // Each grid item takes up 50% width by using xs={6}.
            // Notice we do not include an "item" prop.
            <Grid xs={6} key={index}>
              <Paper
                style={{
                  padding: 16,
                  textAlign: 'center',
                  position: 'relative',
                  minHeight: 200,
                }}
              >
                {/* The '+' icon toggles the graph */}
                <IconButton
                  onClick={() => toggleGraph(index)}
                  style={{ position: 'absolute', top: 8, right: 8 }}
                >
                  <AddIcon />
                </IconButton>

                {/* Display the LiveDataGraph component if toggled on, otherwise a placeholder message */}
                {show ? <LiveDataGraph /> : <p>Click + to add graph</p>}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </div>
    </div>
  );
};

export default ArbitrageDashboard;
