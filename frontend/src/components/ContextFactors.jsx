import React from 'react';

export default function ContextFactors({ factors, setFactors }) {
  const factorDefinitions = [
    { key: 'location_risk', label: 'Location Risk', desc: 'Hazard / Curve / Intersection risk level', defaultWeight: '10%' },
    { key: 'road_importance', label: 'Road Importance', desc: 'Highway / Arterial classification rank', defaultWeight: '20%' },
    { key: 'traffic', label: 'Traffic Volume', desc: 'Vehicle throughput & peak density', defaultWeight: '15%' },
    { key: 'complaints', label: 'Citizen Complaints', desc: 'Public hazard reports logged', defaultWeight: '5%' },
    { key: 'historical_recurrence', label: 'Historical Recurrence', desc: 'Repeated damage frequency', defaultWeight: '10%' },
  ];

  const handleChange = (key, value) => {
    const num = Math.max(0, Math.min(100, Number(value) || 0));
    setFactors((prev) => ({
      ...prev,
      [key]: num
    }));
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.1rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>⚖️</span> RoadAI Contextual Factors (0–100)
      </h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginBottom: '20px' }}>
        Adjust municipal road environment factors to compute the explainable repair priority score.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {factorDefinitions.map((f) => (
          <div key={f.key} style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', padding: '12px 16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <div>
                <span style={{ fontWeight: '600', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  {f.label}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-indigo)', marginLeft: '8px', fontWeight: '500' }}>
                  Weight: {f.defaultWeight}
                </span>
              </div>

              {/* Number Input Box */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={factors[f.key]}
                  onChange={(e) => handleChange(f.key, e.target.value)}
                  style={{
                    width: '64px',
                    backgroundColor: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '4px 8px',
                    textAlign: 'center',
                    fontSize: '0.88rem',
                    fontWeight: '600'
                  }}
                />
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>
            </div>

            {/* Slider Control */}
            <input
              type="range"
              min="0"
              max="100"
              value={factors[f.key]}
              onChange={(e) => handleChange(f.key, e.target.value)}
            />

            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {f.desc}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
