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
      id: '1',
      profit: 0.002,
      route: ['BTC', 'ETH', 'USDT'],
      timestamp: '2021-06-01T12:00:00Z',
    },
    {
      id: '2',
      profit: 0.0015,
      route: ['BTC', 'USDT'],
      timestamp: '2021-06-01T12:05:00Z',
    },
    {
      id: '3',
      profit: 0.003,
      route: ['ETH', 'USDT'],
      timestamp: '2021-06-01T12:10:00Z',
    },
];

const historicalData: ArbitrageOpportunity[] = [
  {
    id: '1',
    profit: 0.002,
    route: ['BTC', 'ETH', 'USDT'],
    timestamp: '2021-06-01T12:00:00Z',
  },
  {
    id: '2',
    profit: 0.0015,
    route: ['BTC', 'USDT'],
    timestamp: '2021-06-01T12:05:00Z',
  },
  {
    id: '3',
    profit: 0.003,
    route: ['ETH', 'USDT'],
    timestamp: '2021-06-01T12:10:00Z',
  },
  {
    id: '4',
    profit: 0.0025,
    route: ['BTC', 'ETH', 'USDT'],
    timestamp: '2021-06-01T12:15:00Z',
  },
  {
    id: '5',
    profit: 0.001,
    route: ['BTC', 'USDT'],
    timestamp: '2021-06-01T12:20:00Z',
  },
  {
    id: '6',
    profit: 0.0028,
    route: ['ETH', 'USDT'],
    timestamp: '2021-06-01T12:25:00Z',
  },
  {
    id: '7',
    profit: 0.0022,
    route: ['BTC', 'ETH', 'USDT'],
    timestamp: '2021-06-01T12:30:00Z',
  },
  {
    id: '8',
    profit: 0.0013,
    route: ['BTC', 'USDT'],
    timestamp: '2021-06-01T12:35:00Z',
  },
  {
    id: '9',
    profit: 0.0029,
    route: ['ETH', 'USDT'],
    timestamp: '2021-06-01T12:40:00Z',
  },
  {
    id: '10',
    profit: 0.0021,
    route: ['BTC', 'ETH', 'USDT'],
    timestamp: '2021-06-01T12:45:00Z',
  },
  {
    id: '11',
    profit: 0.0012,
    route: ['BTC', 'USDT'],
    timestamp: '2021-06-01T12:50:00Z',
  },
  {
    id: '12',
    profit: 0.0027,
    route: ['ETH', 'USDT'],
    timestamp: '2021-06-01T12:55:00Z',
  },
  {
    id: '13',
    profit: 0.0023,
    route: ['BTC', 'ETH', 'USDT'],
    timestamp: '2021-06-01T13:00:00Z',
  },
];
  
  const LiveDataGraph: React.FC = () => {
    const [data, setData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [isHistorical, setIsHistorical] = useState<boolean>(false);
    const [sliderValue, setSliderValue] = useState<number>(historicalData.length);
  
    const fetchLiveData = async () => {
      setLoading(true);
      try {
        // This endpoint should return an array of data points: { time: string, value: number }
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
        // Simulated API call returning historical data
        const response = { data: historicalData } as { data: ArbitrageOpportunity[] };
        setData(response.data);
        setSliderValue(response.data.length);
      } catch (error) {
        console.error("Error fetching historical data:", error);
      } finally {
        setLoading(false);
      }
    };

  // Fetch live data immediately and then every 3 seconds
  useEffect(() => {
    if (isHistorical) {
      fetchHistoricalData();
    } else {
      fetchLiveData();
      const interval = setInterval(fetchLiveData, 3000);
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
            <Line type="monotone" dataKey="profit" stroke="#8884d8" activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        !loading && <p>No data available.</p>
      )}
      <button
        onClick={() => setIsHistorical(!isHistorical)}
        style={{ marginTop: '20px' }}
      >
        {isHistorical ? 'Show Live Data' : 'Show Historical Data'}
      </button>

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