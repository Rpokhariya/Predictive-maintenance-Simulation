// In: frontend/src/BearingPlot.jsx

import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import useWebSocket, { ReadyState } from 'react-use-websocket';
// --- FIX: Import mock UI from our new file ---
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./mock-ui";

export function BearingPlot({ testSet, bearingName, wsUrl }) {
  const [chartData, setChartData] = useState([]);
  const [sodIndex, setSodIndex] = useState(-1);
  const [threshold, setThreshold] = useState(0);

  // --- WebSocket Connection ---
  const socketUrl = `${wsUrl}/${testSet}/${encodeURIComponent(bearingName)}`;
  
  // --- FIX: Removed the stray '_' ---
  const { lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true,
    reconnectInterval: 5000,
    onOpen: () => {
      console.log(`WebSocket connected for ${bearingName}`);
      setChartData([]);
      setSodIndex(-1);
      setThreshold(0);
    },
    onClose: () => console.log(`WebSocket disconnected for ${bearingName}`),
  });

  // --- Real-Time Data Update ---
  useEffect(() => {
    if (lastJsonMessage) {
      if (lastJsonMessage.status === "Finished") {
        console.log(`Stream finished for ${bearingName}`);
        return;
      }
      
      setChartData(prevData => [...prevData, lastJsonMessage]);
      
      if (lastJsonMessage.sod_index !== -1) {
        setSodIndex(lastJsonMessage.sod_index);
      }
      if (lastJsonMessage.threshold > 0) {
        setThreshold(lastJsonMessage.threshold);
      }
    }
  }, [lastJsonMessage]);

  // --- Status Logic ---
  const sodStatus = (sodIndex !== -1) ? "Degradation Detected" : "Healthy";
  const statusColor = (sodIndex !== -1) ? "text-red-500" : "text-green-500";
  const lastKurtosis = chartData.length > 0 ? chartData[chartData.length - 1].raw.toFixed(3) : "N/A";

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting...',
    [ReadyState.OPEN]: 'Live',
    [ReadyState.CLOSING]: 'Closing...',
    [ReadyState.CLOSED]: 'Disconnected',
    [ReadyState.UNINSTANTIATED]: 'Initializing...',
  }[readyState];

  const statusTextStyle = {
    color: readyState === ReadyState.OPEN ? 'green' : 'gray',
    fontWeight: 'bold'
  };
  
  const sodTextStyle = {
    color: sodIndex !== -1 ? 'red' : 'green',
    fontWeight: 'bold'
  };

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <CardTitle>{bearingName}</CardTitle>
        <CardDescription className="flex justify-between">
          <span style={statusTextStyle}>
            {connectionStatus}
          </span>
          <span style={sodTextStyle}>{sodStatus}</span>
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-grow">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData} margin={{ top: 30, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" type="number" domain={[0, 'dataMax']} />
            <YAxis label={{ value: 'Kurtosis', angle: -90, position: 'insideLeft' }} domain={['auto', 'auto']} />
            <Tooltip wrapperStyle={{ zIndex: 1000 }} />
            <Legend verticalAlign="bottom" />
            
            {/* These colors match your App.jsx */}
            <Line type="monotone" dataKey="raw" stroke="#cbd5e1" dot={false} name="Raw Kurtosis" isAnimationActive={false} />
            <Line type="monotone" dataKey="below_threshold" stroke="#8884d8" dot={false} strokeWidth={2} name="Smoothed (Normal)" connectNulls={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="above_threshold" stroke="#f97316" dot={false} strokeWidth={2} name="Smoothed (Above Threshold)" connectNulls={false} isAnimationActive={false} />

            {/* Dotted Red Threshold Line */}
            {threshold > 0 && (
              <ReferenceLine y={threshold} label={{ value: `Threshold (${threshold.toFixed(2)})`, position: 'insideRight' }} stroke="#ff4b4b" strokeDasharray="3 3" />
            )}
            
            {/* Vertical Red SoD Line */}
            {sodIndex !== -1 && (
              <ReferenceLine x={sodIndex} label={{ value: `SoD @ ${sodIndex}`, position: 'top' }} stroke="red" strokeWidth={2} />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// --- FIX: All mock components have been moved to mock-ui.jsx ---