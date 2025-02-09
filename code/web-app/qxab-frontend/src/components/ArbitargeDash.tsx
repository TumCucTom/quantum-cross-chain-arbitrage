import React, { useState, useEffect } from 'react';
import {
  Button,
  Container,
  Typography,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Box,
} from '@mui/material';

// Define the arbitrage log interface. Adjust the field names/types to match your backend.
interface ArbitrageLog {
  time: string; // e.g. "2025-02-09 02:45:10 UTC"
  selectedTrades: string;
  expectedReward: number;
  actualProfit: number;
  numberOfTrades: number;
  timeBetweenTrades: string;
}

const ArbitrageDashboardPage: React.FC = () => {
  const [logs, setLogs] = useState<ArbitrageLog[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Function to start arbitrage by calling the backend.
  const startArbitrage = async () => {
    try {
      const response = await fetch("http://localhost:5002/start-arbitrage", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`Failed to start arbitrage: ${response.statusText}`);
      }
      setIsRunning(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Function to stop arbitrage by calling the backend.
  const stopArbitrage = async () => {
    try {
      const response = await fetch("http://localhost:5002/stop-arbitrage", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`Failed to stop arbitrage: ${response.statusText}`);
      }
      setIsRunning(false);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Function to fetch arbitrage logs from the backend.
  const fetchLogs = async () => {
    try {
      const response = await fetch("http://localhost:5002/arbitrage-logs");
      if (!response.ok) {
        throw new Error(`Failed to fetch logs: ${response.statusText}`);
      }
      const result = await response.json();
      // Assume your backend returns an object like { status: "success", logs: [...] }
      if (result.status === "success") {
        setLogs(result.logs);
      } else {
        setError(result.message || "Unknown error");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Poll logs from the backend every 5 seconds when arbitrage is running.
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      fetchLogs();
      interval = setInterval(fetchLogs, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning]);

  return (
    <Container maxWidth="lg" style={{ marginTop: '20px' }}>
      <Typography variant="h4" gutterBottom>
        Quantum-Enhanced Cross-Chain Arbitrage Bot
      </Typography>
      <Typography variant="h6" gutterBottom>
        Arbitrage Opportunities Dashboard
      </Typography>
      {error && (
        <Typography variant="body1" color="error">
          {error}
        </Typography>
      )}
      <Box mb={2}>
        <Button
          variant="contained"
          color="primary"
          onClick={startArbitrage}
          disabled={isRunning}
          style={{ marginRight: '10px' }}
        >
          Start Arbitrage
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={stopArbitrage}
          disabled={!isRunning}
        >
          Stop Arbitrage
        </Button>
      </Box>
      <Paper elevation={3}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Selected Trades</TableCell>
              <TableCell>Expected Reward</TableCell>
              <TableCell>Actual Profit Realisation</TableCell>
              <TableCell>No. of Trades</TableCell>
              <TableCell>Time Between Trades</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log, index) => (
              <TableRow key={index}>
                <TableCell>{log.time}</TableCell>
                <TableCell>{log.selectedTrades}</TableCell>
                <TableCell>{log.expectedReward}</TableCell>
                <TableCell>{log.actualProfit}</TableCell>
                <TableCell>{log.numberOfTrades}</TableCell>
                <TableCell>{log.timeBetweenTrades}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Container>
  );
};

export default ArbitrageDashboardPage;
