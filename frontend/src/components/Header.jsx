import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../services/apiConfig';

export default function Header() {
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    let mounted = true;

    fetch(API_ENDPOINTS.HEALTH)
      .then((response) => {
        if (!response.ok) throw new Error('API unavailable');
        return response.json();
      })
      .then(() => {
        if (mounted) setApiConnected(true);
      })
      .catch(() => {
        if (mounted) setApiConnected(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <header style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: '28px',
      gap: '20px',
      flexWrap: 'wrap'
    }}>
      <div>
        <h1 style={{ fontSize: '1.85rem', fontWeight: '800', marginBottom: '6px', color: 'var(--text-primary)' }}>
          Road Intelligence Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          AI-Powered Road Damage Intelligence & Repair Prioritization System
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="status-badge">
          <span className="status-dot"></span>
          {apiConnected ? 'API Connected' : 'API Disconnected'}
        </div>
      </div>
    </header>
  );
}
