import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AnalysisHistory from './pages/AnalysisHistory';
import RoadMap from './pages/RoadMap';
import Settings from './pages/Settings';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard mode="dashboard" />;

      case 'analysis':
        return <Dashboard mode="analysis" />;

      case 'history':
        return <AnalysisHistory />;

      case 'map':
        return <RoadMap />;

      case 'settings':
        return <Settings />;

      default:
        return <Dashboard />;
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-primary)'
      }}
    >
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflowY: 'auto'
        }}
      >
        {renderPage()}
      </div>
    </div>
  );
}




