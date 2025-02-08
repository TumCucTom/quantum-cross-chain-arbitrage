import React, { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
  } from 'recharts';

interface ArbitrageOpportunity {
  id: string;
  profit: number;
  route: string[];
  timestamp: string;
}

const dummyData: ArbitrageOpportunity[] = [
    {
      id: "opp1",
      profit: 15.3,
      route: ["Binance", "Coinbase", "Kraken"],
      timestamp: "2025-02-08T10:00:00Z",
    },
    {
      id: "opp2",
      profit: 8.7,
      route: ["Gemini", "Bitstamp"],
      timestamp: "2025-02-08T10:05:00Z",
    },
    {
      id: "opp3",
      profit: 12.1,
      route: ["Bitfinex", "Bittrex", "Coincheck"],
      timestamp: "2025-02-08T10:10:00Z",
    },
  ];

const ArbitrageDashboard: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [qaoaResult, setQaoaResult] = useState<ArbitrageOpportunity[] | null>(null);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      // Replace with your backend endpoint which supplies arbitrage data.
      const response = { data: dummyData } as { data: ArbitrageOpportunity[] };
      setOpportunities(response.data);
    } catch (error) {
      console.error('Error fetching arbitrage opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
    // Poll every 5 seconds (adjust as necessary)
    const interval = setInterval(fetchOpportunities, 5000);
    return () => clearInterval(interval);
  }, []);

    // Run QAOA on live data (stubbed API call)
    const runQAOA = async () => {
        try {
          // Simulated API endpoint that would run your QAOA logic
          const response = { data: opportunities } as { data: ArbitrageOpportunity[] };;
          setQaoaResult(response.data);
        } catch (error) {
          console.error('Error running QAOA:', error);
          setQaoaResult(null);
        }
      };

  return (
    <div>
      <h2>Arbitrage Opportunities</h2>
      {loading && <p>Loading...</p>}
      {opportunities.length === 0 && !loading && <p>No opportunities found.</p>}
      {opportunities.map((opp) => (
        <div key={opp.id} className="opportunity-card">
          <p>
            <strong>Profit:</strong> {opp.profit.toFixed(2)}
          </p>
          <p>
            <strong>Route:</strong> {opp.route.join(' → ')}
          </p>
          <p>
            <strong>Timestamp:</strong> {new Date(opp.timestamp).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ArbitrageDashboard;
