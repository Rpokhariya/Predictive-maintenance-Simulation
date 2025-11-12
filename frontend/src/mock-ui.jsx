// In: frontend/src/mock-ui.jsx

import React from 'react';

// --- Mock UI Components ---
// We put these here so both App.jsx and BearingPlot.jsx can share them.

export const Tabs = ({ value, onValueChange, className, children }) => (
  <div className={className}>{children}</div>
);
export const TabsList = ({ children }) => (
  <div style={{ display: 'flex', gap: '10px', borderBottom: '1px solid #ccc', paddingBottom: '5px' }}>{children}</div>
);
export const TabsTrigger = ({ value, children, onClick }) => (
  <button onClick={onClick} style={{ padding: '10px 15px', border: 'none', background: 'transparent', cursor: 'pointer', fontSize: '1rem' }}>
    {children}
  </button>
);
export const TabsContent = ({ value, children }) => <div>{children}</div>;

export const Card = ({ className, children }) => (
  <div className={className} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', background: 'white', display: 'flex', flexDirection: 'column' }}>{children}</div>
);
export const CardHeader = ({ children }) => (
  <div style={{ padding: '16px', borderBottom: '1px solid #e2e8f0' }}>{children}</div>
);
export const CardTitle = ({ children }) => (
  <h3 style={{ fontWeight: '600', fontSize: '1.25rem' }}>{children}</h3>
);
export const CardDescription = ({ className, children }) => (
  <div className={className} style={{ color: '#64748b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>{children}</div>
);
export const CardContent = ({ className, children }) => (
  <div className={className} style={{ padding: '16px', flexGrow: 1 }}>{children}</div>
);