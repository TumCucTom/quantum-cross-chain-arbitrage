import React, { useState } from 'react';
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
  
  const LiveDataGraph: React.FC = () => {
    const [data, setData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
  
    const fetchLiveData = async () => {
      setLoading(true);
      try {
        // This endpoint should return an array of data points: { time: string, value: number }
        const response = await axios.get<DataPoint[]>('/api/live-data');
        setData(response.data);
      } catch (error) {
        console.error("Error fetching live data:", error);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div>
        <h2>Live Market Data</h2>
        <button onClick={fetchLiveData}>Refresh Data</button>
        {loading && <p>Loading data...</p>}
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          !loading && <p>No data available. Click "Refresh Data" to fetch live data.</p>
        )}
      </div>
    );
  };
  
  export default LiveDataGraph;