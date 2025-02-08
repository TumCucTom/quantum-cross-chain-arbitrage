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
    liquidity1: number;
    liquidity2: number;
}

interface LiveDataGraphProps {
  currency: string;
}

const dummyData: ArbitrageOpportunity[] = [
    {
      feed: 'BTC/ETH',
      timestamp: 1622563200,
      liquidity1: 0.1,
      liquidity2: 0.2,
    },
    {
      feed: 'BTC/USDT',
      timestamp: 1622563300,
      liquidity1: 0.3,
      liquidity2: 0.4,
    },
    {
      feed: 'ETH/USDT',
      timestamp: 1622563400,
      liquidity1: 0.5,
      liquidity2: 0.6,
    },
];

const historicalData: ArbitrageOpportunity[] = [
  {
    feed: 'BTC/ETH',
    timestamp: 1622563200,
    liquidity1: 0.1,
    liquidity2: 0.2,
  },
  {
    feed: 'BTC/USDT',
    timestamp: 1622563300,
    liquidity1: 0.3,
    liquidity2: 0.4,
  },
  {
    feed: 'ETH/USDT',
    timestamp: 1622563400,
    liquidity1: 0.5,
    liquidity2: 0.6,
  },
  {
    feed: 'BTC/ETH',
    timestamp: 1622563500,
    liquidity1: 0.7,
    liquidity2: 0.8,
  },
  {
    feed: 'BTC/USDT',
    timestamp: 1622563600,
    liquidity1: 0.9,
    liquidity2: 1.0,
  },
  {
    feed: 'ETH/USDT',
    timestamp: 1622563700,
    liquidity1: 1.1,
    liquidity2: 1.2,
  },
  {
    feed: 'BTC/ETH',
    timestamp: 1622563800,
    liquidity1: 1.3,
    liquidity2: 1.4,
  },
  {
    feed: 'BTC/USDT',
    timestamp: 1622563900,
    liquidity1: 1.5,
    liquidity2: 1.6,
  },
  {
    feed: 'ETH/USDT',
    timestamp: 1622564000,
    liquidity1: 1.7,
    liquidity2: 1.8,
  },
  {
    feed: 'BTC/ETH',
    timestamp: 1622564100,
    liquidity1: 1.9,
    liquidity2: 2.0,
  },
  {
    feed: 'BTC/USDT',
    timestamp: 1622564200,
    liquidity1: 2.1,
    liquidity2: 2.2,
  },
  {
    feed: 'ETH/USDT',
    timestamp: 1622564300,
    liquidity1: 2.3,
    liquidity2: 2.4,
  },
  {
    feed: 'BTC/ETH',
    timestamp: 1622564400,
    liquidity1: 2.5,
    liquidity2: 2.6,
  },
];
  
  const LiveDataGraph: React.FC<LiveDataGraphProps> = ({ currency }) => {
    const [data, setData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [isHistorical, setIsHistorical] = useState<boolean>(false);
    const [sliderValue, setSliderValue] = useState<number>(historicalData.length);
  
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
        // WHERE THE API ENDPOINT WOULD BE CALLED FOR HISTORICAL DATA!! CURRENTLY DUMMY DATA
        const response = { data: historicalData } as { data: ArbitrageOpportunity[] }; //API CALL TO CURRENCY DATA
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
            <Line type="monotone" dataKey="liquidity1" stroke="#8884d8" activeDot={{ r: 8 }} />
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