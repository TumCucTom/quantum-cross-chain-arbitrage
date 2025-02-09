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
  currency1: string;
  currency2: string;
  isHistorical: boolean;
}
  
  const LiveDataGraph: React.FC<LiveDataGraphProps> = ({ currency1, currency2, isHistorical }) => {
    const [data1, setData1] = useState<ArbitrageOpportunity[]>([]);
    const [data2, setData2] = useState<ArbitrageOpportunity[]>([]);
    const [combinedData, setCombinedData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    const [windowLength, setWindowLength] = useState<number>(0);
    const [windowStart, setWindowStart] = useState<number>(0);
    
    // Function to simulate fetching historical data
    const fetchHistoricalData1 = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5002/history/${currency1+'USDT'}`, {
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
          setData1(opportunities);
          if (opportunities.length > 0 && windowLength === 0) {
            // Default preset (e.g., 'all' time points)
            setWindowLength(opportunities.length);
            setWindowStart(0);
          }  
        } else {
          console.error("API Error:", result.message);
        }
      } catch (error) {
        console.error("Error fetching historical data:", error);
      } finally {
        setLoading(false);
      }
    };

    const fetchHistoricalData2 = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:5002/history/${currency2+'USDT'}`, {
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
          setData2(opportunities);
          if (opportunities.length > 0 && windowLength === 0) {
            // Default preset (e.g., 'all' time points)
            setWindowLength(opportunities.length);
            setWindowStart(0);
          }  
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

  // Merge data1 and data2 by matching timestamps. Then compute ratio = price1 / price2.
  function mergeAndComputeRatio(
    arr1: ArbitrageOpportunity[],
    arr2: ArbitrageOpportunity[]
  ): ArbitrageOpportunity[] {
    // Build a map of timestamps -> price for each array.
    const map1 = new Map<number, ArbitrageOpportunity>();
    arr1.forEach((d) => {
      map1.set(d.timestamp, d);
    });

    const merged: ArbitrageOpportunity[] = [];

    // For each data2 point, see if there's a matching timestamp in map1.
    arr2.forEach((d2) => {
      const match = map1.get(d2.timestamp);
      if (match) {
        // ratio
        const ratio = d2.price !== 0 ? match.price / d2.price : 0;
        merged.push({
          feed: match.feed + '/' + d2.feed, // e.g. "BTC/ETH"
          timestamp: match.timestamp,       // or d2.timestamp, they match
          price: ratio,
          liquidity1: 0,
          liquidity2: 0,
        });
      }
    });

    // Sort by timestamp, just in case
    merged.sort((a, b) => a.timestamp - b.timestamp);
    return merged;
  }

  const computeCombinedData = () => {
    const combined = mergeAndComputeRatio(data1, data2);
    setCombinedData(combined);
  };

    // Fetch live data immediately and then every 3 seconds
  useEffect(() => {
    if (isHistorical) {
      const timeout1 = setTimeout(() => {
        fetchHistoricalData1();
      }, 1000);
      const timeout2 = setTimeout(() => {
        fetchHistoricalData2();
      }, 1000);

      console.log(data1);
      console.log(data2);
      computeCombinedData();
      
      return () => {
        clearTimeout(timeout1);
        clearTimeout(timeout2);
      };

    } else {
    }
  }, [isHistorical]);

    // In historical mode, show only the last sliderValue entries.
    const displayedData = isHistorical ? combinedData.slice(windowStart, windowStart + windowLength) : combinedData;

    // Preset button handler: sets the fixed windowLength (number of data points)
    const setPreset = (preset: '1h' | '1d' | '1m' | '6m' | 'all') => {
    // Example: these numbers represent the number of data points corresponding to each preset.
    let length = 0;
    switch (preset) {
      case '1h':
        length = 3;
        break;
      case '1d':
        length = 6;
        break;
      case '1m':
        length = 9;
        break;
      case '6m':
        length = 13;
        break;
      case 'all':
        length = combinedData.length;
        break;
      default:
        length = combinedData.length;
    }
    setWindowLength(length);
    setWindowStart(combinedData.length - length > 0 ? combinedData.length - length : 0);
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
            <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 2 }} dot={{ r: 0.5 }} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        !loading && <p>No data available.</p>
      )}

        {/* Interactive controls for historical mode */}
        {isHistorical && (
        <div style={{ marginTop: '20px' }}>
          <div>
            <label htmlFor="slider">Data window starts at index: {windowStart} (showing {windowLength} points)</label>
            <input
              id="slider"
              type="range"
              min="1"
              max={combinedData.length - windowLength >= 0 ? combinedData.length - windowLength : 0}
              value={windowStart}
              onChange={(e) => setWindowStart(Number(e.target.value))}
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