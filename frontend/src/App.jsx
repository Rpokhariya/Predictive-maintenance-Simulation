// In: frontend/src/App.jsx

import React, { useState, useMemo } from 'react';
import { BearingPlot } from './BearingPlot';
// --- FIX: Import mock UI from our new file ---
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./mock-ui";

// --- IMPORTANT: UPDATE THESE URLs ---
const WS_URL_LOCAL = 'ws://localhost:8000/ws';
// const WS_URL_DEPLOYED = 'wss://your-fastapi-app.onrender.com/ws'; // <-- Change this when you deploy
const API_URL = WS_URL_LOCAL; 
// ------------------------------------

const ALL_BEARINGS = {
  "1st_test": [
    'B1-Ch1 (Healthy)', 'B1-Ch2 (Healthy)', 'B2-Ch1 (Healthy)', 'B2-Ch2 (Healthy)', 
    'B3-Ch1 (Fail-Inner)', 'B3-Ch2 (Fail-Inner)', 'B4-Ch1 (Fail-Roller)', 'B4-Ch2 (Fail-Roller)'
  ],
  "2nd_test": [
    'B1-Ch1 (Fail-Outer)', 'B2-Ch1 (Healthy)', 'B3-Ch1 (Healthy)', 'B4-Ch1 (Healthy)'
  ],
  "3rd_test": [
    'B1-Ch1 (Healthy)', 'B2-Ch1 (Healthy)', 'B3-Ch1 (Fail-Outer)', 'B4-Ch1 (Healthy)'
  ]
};

export default function App() {
  const [activeTab, setActiveTab] = useState("1st_test");
  
  const activeBearings = ALL_BEARINGS[activeTab] || [];

  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-screen">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Real-Time SoD Detection (WebSocket)</h1>
        <p className="text-gray-600">Live Kurtosis monitoring & SoD detection for all bearings</p>
      </header>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
        <TabsList>
          <TabsTrigger value="1st_test" onClick={() => setActiveTab("1st_test")}>Test Set 1</TabsTrigger>
          <TabsTrigger value="2nd_test" onClick={() => setActiveTab("2nd_test")}>Test Set 2</TabsTrigger>
          <TabsTrigger value="3rd_test" onClick={() => setActiveTab("3rd_test")}>Test Set 3</TabsTrigger>
        </TabsList>
        
        {Object.keys(ALL_BEARINGS).map(testName => (
          <TabsContent key={testName} value={testName}>
            <div style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', display: 'grid', gap: '1rem' }}>
              {/* For the active tab, render all bearing plots */}
              {activeTab === testName && activeBearings.map(bearingName => (
                <BearingPlot
                  key={bearingName}
                  testSet={testName}
                  bearingName={bearingName}
                  wsUrl={API_URL}
                />
              ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}

// --- FIX: All mock components have been moved to mock-ui.jsx ---