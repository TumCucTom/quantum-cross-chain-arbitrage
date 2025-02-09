import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button
} from '@mui/material';

type Trade = {
  id: number;
  time_of_trade: string;
  expected_reward: number;
  actual_profit: number;
  number_of_trades: number;
  time_between_trades: string;
};

export default function ArbitrageTable() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isArbitrageRunning, setIsArbitrageRunning] = useState(false);

  // Fetch the trades from the backend
  const fetchTrades = async () => {
    try {
      // Replace with your endpoint
      const response = await axios.get('/api/trades');
      setTrades(response.data);
    } catch (error) {
      console.error('Error fetching trades:', error);
    }
  };

  // Start arbitrage (POST request)
  const startArbitrage = async () => {
    try {
      await axios.post('/api/arbitrage/start');
      setIsArbitrageRunning(true);
      // Optionally refetch trades after starting
      fetchTrades();
    } catch (error) {
      console.error('Error starting arbitrage:', error);
    }
  };

  // Stop arbitrage (POST request)
  const stopArbitrage = async () => {
    try {
      await axios.post('/api/arbitrage/stop');
      setIsArbitrageRunning(false);
      // Optionally refetch trades after stopping
      fetchTrades();
    } catch (error) {
      console.error('Error stopping arbitrage:', error);
    }
  };

  useEffect(() => {
    // Mock data or real fetch
    setTrades([
      {
        id: 1,
        time_of_trade: '2025-02-09T12:00:00Z',
        expected_reward: 100,
        actual_profit: 90,
        number_of_trades: 5,
        time_between_trades: '10s'
      },
      {
        id: 2,
        time_of_trade: '2025-02-09T12:05:00Z',
        expected_reward: 120,
        actual_profit: 110,
        number_of_trades: 6,
        time_between_trades: '15s'
      }
    ]);
  }, []);

  return (
    <div style={{ width: '100vw', height: '90vh', padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Buttons for starting/stopping arbitrage */}
      <div style={{ marginBottom: '16px' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={startArbitrage}
          disabled={isArbitrageRunning}
        >
          Start Arbitrage
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={stopArbitrage}
          disabled={!isArbitrageRunning}
          style={{ marginLeft: '8px' }}
        >
          Stop Arbitrage
        </Button>
      </div>

      {/* Table container */}
      <TableContainer component={Paper} style={{ maxHeight: 'calc(100% - 100px)' }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Time of Trade</TableCell>
              <TableCell>Expected Reward</TableCell>
              <TableCell>Actual Profit</TableCell>
              <TableCell>No. of Trades</TableCell>
              <TableCell>Time Between Trades</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade, index) => (
              <TableRow key={trade.id || index}>
                <TableCell>{trade.time_of_trade}</TableCell>
                <TableCell>{trade.expected_reward}</TableCell>
                <TableCell>{trade.actual_profit}</TableCell>
                <TableCell>{trade.number_of_trades}</TableCell>
                <TableCell>{trade.time_between_trades}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

