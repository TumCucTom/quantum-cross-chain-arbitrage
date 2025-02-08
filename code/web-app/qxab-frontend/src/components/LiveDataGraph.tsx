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
    feed: string;
    timestamp: number;
    price: number;
    liquidity1: number;
    liquidity2: number;
}

interface LiveDataGraphProps {
  currency: string;
  isHistorical: boolean;
}

const dummyData: ArbitrageOpportunity[] = [
    {
      feed: 'BTC/ETH',
      timestamp: 1622563200,
      price: 5,
      liquidity1: 5,
      liquidity2: 9
    },
    {
      feed: 'BTC/ETH',
      timestamp: 1622563200,
      price: 5,
      liquidity1: 5,
      liquidity2: 9
    }
];
  
  const LiveDataGraph: React.FC<LiveDataGraphProps> = ({ currency, isHistorical }) => {
    const [data, setData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [sliderValue, setSliderValue] = useState<number>(0);
  
    const fetchLiveData = async () => {
      setLoading(true);
      try {
        // WHERE THE API ENDPOINT WOULD BE CALLED FOR HISTORICAL DATA!! CURRENTLY DUMMY DATA
        const response = { data: dummyData } as { data: ArbitrageOpportunity[] };;
        setData(response.data);
      } catch (error) {
        console.error("Error fetching live data:", error);
      } finally {
        setLoading(false);
      }
    };

    // Function to simulate fetching historical data
    const fetchHistoricalData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5002/history/${currency}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          mode: "cors",  // Enable CORS mode
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch historical data: ${response.statusText}`);
        }
        const result = await response.json();
        const opportunities: ArbitrageOpportunity[] = transformHistoryData(result);

        if (result.status === "success") {
          setData(opportunities);
          setSliderValue(opportunities.length);
        } else {
          console.error("API Error:", result.message);
        }
      } catch (error) {
        console.error("Error fetching historical data:", error);
      } finally {
        setLoading(false);
      }
    };

    const transformHistoryData = (data: any): ArbitrageOpportunity[] => {
      return data.history.map((row: any[]) => {
        return {
          feed: row[0],
          timestamp: new Date(row[4]).getTime() / 1000,
          price: parseFloat(row[1]) || 0,
          liquidity1: row[2] !== null ? parseFloat(row[2]) : 0,
          liquidity2: row[2] !== null ? parseFloat(row[2]) : 0,
        };
      });
    };

    // Fetch live data immediately and then every 3 seconds
  useEffect(() => {
    if (isHistorical) {
      const timeout = setTimeout(() => {
        fetchHistoricalData();
      }, 500);

      return () => clearTimeout(timeout);
    } else {
      fetchLiveData();
      const interval = setInterval(fetchLiveData, 5000);
      return () => clearInterval(interval);
    }
  }, [isHistorical]);

    // In historical mode, show only the last sliderValue entries.
    const displayedData = isHistorical ? data.slice(-sliderValue) : data;

    // Preset button handler (mapping presets to a number of data points)
    const setPreset = (preset: '1h' | '1d' | '1m' | '6m' | 'all') => {
      // These numbers are examples. Adjust them based on the granularity of your real data.
      switch (preset) {
        case '1h':
          setSliderValue(3);
          break;
        case '1d':
          setSliderValue(6);
          break;
        case '1m':
          setSliderValue(9);
          break;
        case '6m':
          setSliderValue(13);
          break;
        case 'all':
          setSliderValue(data.length);
          break;
        default:
          setSliderValue(data.length);
      }
    };
  
    return (
      <div>
      <h2>{isHistorical ? 'Historical Market Data' : 'Live Market Data'}</h2>
      {loading && <p>Loading data...</p>}
      {displayedData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={displayedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 2 }} dot={{ r: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        !loading && <p>No data available.</p>
      )}

        {/* Interactive controls for historical mode */}
        {isHistorical && (
        <div style={{ marginTop: '20px' }}>
          <div>
            <label htmlFor="slider">Select number of data points: {sliderValue}</label>
            <input
              id="slider"
              type="range"
              min="1"
              max={data.length}
              value={sliderValue}
              onChange={(e) => setSliderValue(Number(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>
          <div style={{ marginTop: '10px' }}>
            <button onClick={() => setPreset('1h')}>1 Hour</button>
            <button onClick={() => setPreset('1d')}>1 Day</button>
            <button onClick={() => setPreset('1m')}>1 Month</button>
            <button onClick={() => setPreset('6m')}>6 Months</button>
            <button onClick={() => setPreset('all')}>All</button>
          </div>
        </div>
      )}
    </div>
    );
  };
  
  export default LiveDataGraph;