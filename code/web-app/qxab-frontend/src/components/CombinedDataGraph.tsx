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
    const [data, setData] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    const [windowLength, setWindowLength] = useState<number>(0);
    const [windowStart, setWindowStart] = useState<number>(0);

    function extractJsonFromString(str: string): any {
      const firstBrace = str.indexOf('{');
      const lastBrace = str.lastIndexOf('}');
      if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
        throw new Error("No valid JSON found in the response string.");
      }
      const jsonString = str.substring(firstBrace, lastBrace + 1);
      return JSON.parse(jsonString);
    }
  
    const fetchLiveData = async () => {
      setLoading(true);
      try {
        const response = await fetch("http://localhost:5002/ftso-live-prices", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          // Send the current currency as a single-element array.
          body: JSON.stringify({ symbols: [currency1, currency2] }),
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch live data: ${response.statusText}`);
        }
        const result = await response.json();
        const extracted = extractJsonFromString(result.data);
        const opportunities: ArbitrageOpportunity[] = transformLiveData(extracted);
        if (result.status === "success") {
          // Assuming result.data is an array of ArbitrageOpportunity objects:
          setData((prevData) => [...prevData, ...opportunities].slice(-10));
        } else {
          console.error("API Error:", result.message);
        }
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
        const response = await fetch(`http://localhost:5002/history/${currency1+'/'+currency2}`, {
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
      // Step 1: Convert raw data into structured objects
      const formattedData: ArbitrageOpportunity[] = data.history.map((row: any[]): ArbitrageOpportunity => ({
        feed: row[0], // Token name (e.g., BTC, ETH)
        timestamp: new Date(row[4]).setHours(0, 0, 0, 0) / 1000, // Convert to start of day (Unix timestamp in seconds)
        price: parseFloat(row[1]) || 0,
        liquidity1: row[2] !== null ? parseFloat(row[2]) : 0,
        liquidity2: row[3] !== null ? parseFloat(row[3]) : 0, // Fix: use row[3] for liquidity2
      }));
    
      // Step 2: Group data by timestamp (day) into a Map
      const groupedByDay = new Map<number, { [key: string]: number }>();
    
      formattedData.forEach(({ feed, timestamp, price }) => {
        if (!groupedByDay.has(timestamp)) {
          groupedByDay.set(timestamp, {});
        }
        groupedByDay.get(timestamp)![feed] = price; // Store price under token name
      });
    
      // Step 3: Compute price ratio when both tokens exist for the same day
      const computedRatios: ArbitrageOpportunity[] = [];
      
      groupedByDay.forEach((prices, timestamp) => {
        const tokens = Object.keys(prices);
    
        if (tokens.length === 2) { // Ensure we have both tokens on the same day
          const token1 = tokens[0];
          const token2 = tokens[1];
          const ratio = prices[token2] !== 0 ? prices[token1] / prices[token2] : 0;
    
          computedRatios.push({
            feed: `${token1}/${token2}`,
            timestamp,
            price: ratio,
            liquidity1: 0,
            liquidity2: 0,
          });
        }
      });
    
      return computedRatios;
    };
    

    function transformLiveData(rawData: any): ArbitrageOpportunity[] {
      return rawData.feeds.map((item: any) => ({
        feed: item.feed_id, // use feed_id from the raw JSON
        timestamp: new Date(item.timestamp).getTime() / 1000, // convert to Unix timestamp (seconds)
        price: item.price,
        liquidity1: 0, // default value
        liquidity2: 0, // default value
      }));
    }

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
    const displayedData = isHistorical ? data.slice(windowStart, windowStart + windowLength) : data;

    // Preset button handler: sets the fixed windowLength (number of data points)
    const setPreset = (preset: '1d' | '1m' | '6m' | '1y' | 'all') => {
    // Example: these numbers represent the number of data points corresponding to each preset.
    let length = 0;
    switch (preset) {
      case '1d':
        length = 1;
        break;
      case '1m':
        length = 30;
        break;
      case '6m':
        length = 30*6;
        break;
      case '1y':
        length = 365;
        break;
      case 'all':
        length = data.length;
        break;
      default:
        length = data.length;
    }
    setWindowLength(length);
    setWindowStart(data.length - length > 0 ? data.length - length : 0);
  };
  
    return (
      <div>
      <h2>{isHistorical ? 'Historical Market Data' : 'Live Market Data'}</h2>
      {loading && <p>Loading data...</p>}
      {displayedData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={displayedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp"   
              type="number"
              domain={['auto', 'auto']}
              tickFormatter={(val) => {
                // val is your Unix timestamp in seconds.
                const date = new Date(val * 1000); // multiply by 1000 if val is in seconds
                return date.toLocaleString();      // or toLocaleTimeString(), etc.
              }}/>
            <YAxis domain={['auto', 'auto']}/>
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
              max={data.length - windowLength >= 0 ? data.length - windowLength : 0}
              value={windowStart}
              onChange={(e) => setWindowStart(Number(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>
          <div style={{ marginTop: '10px' }}>
            <button onClick={() => setPreset('1d')}>1 Hour</button>
            <button onClick={() => setPreset('1m')}>1 Day</button>
            <button onClick={() => setPreset('6m')}>1 Month</button>
            <button onClick={() => setPreset('1y')}>6 Months</button>
            <button onClick={() => setPreset('all')}>All</button>
          </div>
        </div>
      )}
    </div>
    );
  };
  
  export default LiveDataGraph;