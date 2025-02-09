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
  trade_batch: number;
  time_of_trade: string;
  token_from_trade: string;
  token_to_trade: string;
  amount: number;
  expected_reward: number;
  txhash: string;
  cross_chain_state_validated: boolean;
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
      const response = await axios.get('/qaoa-arbitrage');
      setTrades(response.data);
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
        trade_batch: 1,
        time_of_trade: '2025-02-09T12:00:00Z',
        token_from_trade: 'BTC',
        token_to_trade: 'ETH',
        amount: 0.003,
        expected_reward: 100,
        txhash: "0x123456789abcdef0",
        cross_chain_state_validated: true,
      },
      {
        trade_batch: 1,
        time_of_trade: '2025-02-09T12:00:03Z',
        token_from_trade: 'ETH',
        token_to_trade: 'BCH',
        amount: 0.002,
        expected_reward: 100,
        txhash: "0x123456789abcdef1",
        cross_chain_state_validated: true,
      },
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
              <TableCell>Trade Batch</TableCell>
              <TableCell>Time of Trade</TableCell>
              <TableCell>Token From</TableCell>
              <TableCell>Token To</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Total Expected Reward</TableCell>
              <TableCell>Transaction Hash</TableCell>
              <TableCell>Cross Chain State Validated?</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade, index) => (
              <TableRow>
                <TableCell>{trade.trade_batch}</TableCell>
                <TableCell>{trade.time_of_trade}</TableCell>
                <TableCell>{trade.token_from_trade}</TableCell>
                <TableCell>{trade.token_to_trade}</TableCell>
                <TableCell>{trade.amount}</TableCell>
                <TableCell>{trade.expected_reward}</TableCell>
                <TableCell>{trade.txhash}</TableCell>
                <TableCell>{trade.cross_chain_state_validated ? "Yes" : "No"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

