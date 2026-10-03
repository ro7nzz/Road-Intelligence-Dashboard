import React from 'react';

export default function Settings() {
  return (
    <main className="settings-page">
      <div className="settings-header">
        <div>
          <div className="settings-eyebrow">ROADAi / SYSTEM</div>
          <h1>Settings</h1>
          <p>RoadAI system configuration and model information.</p>
        </div>

        <div className="settings-status">
          <span></span>
          SYSTEM ONLINE
        </div>
      </div>

      <section className="settings-grid">
        <div className="settings-card">
          <div className="settings-card-icon">AI</div>
          <div>
            <span className="settings-label">Detection Engine</span>
            <h2>YOLO11n</h2>
            <p>Road-damage detection and classification engine.</p>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-icon">API</div>
          <div>
            <span className="settings-label">Backend</span>
            <h2>FastAPI</h2>
            <p>REST API serving RoadAI analysis operations.</p>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-icon">DB</div>
          <div>
            <span className="settings-label">Database</span>
            <h2>SQLite</h2>
            <p>Local persistent storage through SQLAlchemy.</p>
          </div>
        </div>

        <div className="settings-card">
          <div className="settings-card-icon">UI</div>
          <div>
            <span className="settings-label">Frontend</span>
            <h2>React + Vite</h2>
            <p>Interactive RoadAI decision-support interface.</p>
          </div>
        </div>
      </section>

      <section className="settings-panel">
        <div className="settings-panel-header">
          <div>
            <div className="settings-eyebrow">MODEL CONFIGURATION</div>
            <h2>Road Damage Classes</h2>
          </div>
          <span className="settings-badge">4 CLASSES</span>
        </div>

        <div className="settings-class-list">
          <div>
            <strong>D00</strong>
            <span>Longitudinal Crack</span>
          </div>
          <div>
            <strong>D10</strong>
            <span>Transverse Crack</span>
          </div>
          <div>
            <strong>D20</strong>
            <span>Alligator Crack</span>
          </div>
          <div>
            <strong>D40</strong>
            <span>Pothole</span>
          </div>
        </div>
      </section>

      <section className="settings-panel">
        <div className="settings-panel-header">
          <div>
            <div className="settings-eyebrow">DECISION ENGINE</div>
            <h2>Repair Priority System</h2>
          </div>
          <span className="settings-badge">LOCKED</span>
        </div>

        <div className="settings-weight-grid">
          <div><span>Damage Severity</span><strong>40%</strong></div>
          <div><span>Road Importance</span><strong>20%</strong></div>
          <div><span>Traffic</span><strong>15%</strong></div>
          <div><span>Location Risk</span><strong>10%</strong></div>
          <div><span>Historical Recurrence</span><strong>10%</strong></div>
          <div><span>Complaints</span><strong>5%</strong></div>
        </div>
      </section>

      <section className="settings-note">
        <span>i</span>
        <div>
          <strong>System Configuration</strong>
          <p>
            Core RoadAI model, severity calculation, contextual factors and
            priority weights are fixed for the current project configuration.
          </p>
        </div>
      </section>
    </main>
  );
}
