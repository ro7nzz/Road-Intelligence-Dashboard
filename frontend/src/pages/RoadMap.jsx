import React, { useEffect, useMemo, useState } from 'react';
import { API_ENDPOINTS } from '../services/apiConfig';

export default function RoadMap() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAnalyses = async () => {
      try {
        setLoading(true);
        setError('');

        const response = await fetch(API_ENDPOINTS.ANALYSES);

        if (!response.ok) {
          throw new Error(`Failed to load road intelligence (${response.status})`);
        }

        const data = await response.json();
        setAnalyses(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message || 'Unable to load road intelligence.');
      } finally {
        setLoading(false);
      }
    };

    loadAnalyses();
  }, []);

  const stats = useMemo(() => {
    const result = {
      total: analyses.length,
      critical: 0,
      high: 0,
      moderate: 0,
      low: 0,
      detections: 0,
    };

    analyses.forEach((analysis) => {
      const level = analysis.priority?.priority_level;
      const detections = Array.isArray(analysis.detections)
        ? analysis.detections.length
        : 0;

      result.detections += detections;

      if (level === 'Critical') result.critical += 1;
      else if (level === 'High') result.high += 1;
      else if (level === 'Moderate') result.moderate += 1;
      else if (level === 'Low') result.low += 1;
    });

    return result;
  }, [analyses]);

  const priorityRows = [
    { label: 'Critical', count: stats.critical, className: 'roadmap-critical' },
    { label: 'High', count: stats.high, className: 'roadmap-high' },
    { label: 'Moderate', count: stats.moderate, className: 'roadmap-moderate' },
    { label: 'Low', count: stats.low, className: 'roadmap-low' },
  ];

  return (
    <main className="roadmap-page">
      <div className="roadmap-header">
        <div>
          <div className="roadmap-eyebrow">ROADAi / ROAD INTELLIGENCE</div>
          <h1>Road Map</h1>
          <p>
            Operational overview of detected road damage and repair-priority
            assessments.
          </p>
        </div>

        <div className="roadmap-status">
          <span className="roadmap-status-dot"></span>
          LIVE DATABASE
        </div>
      </div>

      {loading && (
        <div className="roadmap-state">
          <div className="roadmap-spinner"></div>
          <h3>Loading road intelligence...</h3>
          <p>Fetching analysis records from the RoadAI backend.</p>
        </div>
      )}

      {!loading && error && (
        <div className="roadmap-state roadmap-error">
          <div className="roadmap-state-icon">!</div>
          <h3>Unable to load road intelligence</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          <section className="roadmap-stat-grid">
            <div className="roadmap-stat-card">
              <span>Total Analyses</span>
              <strong>{stats.total}</strong>
              <small>Stored assessments</small>
            </div>

            <div className="roadmap-stat-card">
              <span>Detected Issues</span>
              <strong>{stats.detections}</strong>
              <small>Across all analyses</small>
            </div>

            <div className="roadmap-stat-card">
              <span>High + Critical</span>
              <strong>{stats.high + stats.critical}</strong>
              <small>Priority assessments</small>
            </div>

            <div className="roadmap-stat-card">
              <span>Database Status</span>
              <strong>ONLINE</strong>
              <small>FastAPI + SQLite</small>
            </div>
          </section>

          <section className="roadmap-main-grid">
            <div className="roadmap-panel">
              <div className="roadmap-panel-header">
                <div>
                  <h2>Priority Intelligence</h2>
                  <p>Current distribution of repair-priority assessments.</p>
                </div>
              </div>

              <div className="roadmap-priority-list">
                {priorityRows.map((item) => {
                  const percentage =
                    stats.total > 0
                      ? Math.round((item.count / stats.total) * 100)
                      : 0;

                  return (
                    <div className="roadmap-priority-row" key={item.label}>
                      <div className="roadmap-priority-top">
                        <span className={item.className}>{item.label}</span>
                        <strong>
                          {item.count} <small>({percentage}%)</small>
                        </strong>
                      </div>

                      <div className="roadmap-progress">
                        <div
                          className={`roadmap-progress-fill ${item.className}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="roadmap-panel roadmap-location-panel">
              <div className="roadmap-panel-header">
                <div>
                  <h2>Geographic Coverage</h2>
                  <p>Location data status for current assessments.</p>
                </div>
              </div>

              <div className="roadmap-location-visual">
                <div className="roadmap-grid-lines"></div>

                <div className="roadmap-map-center">
                  <div className="roadmap-map-icon">◎</div>
                  <strong>Location Data Unavailable</strong>
                  <span>
                    Current records contain contextual location risk, but not
                    latitude, longitude, address, or road ID.
                  </span>
                </div>
              </div>

              <div className="roadmap-info-note">
                <span>i</span>
                <p>
                  RoadAI does not fabricate geographic positions. A true
                  geographic road map can be enabled in a future version when
                  coordinate data is available.
                </p>
              </div>
            </div>
          </section>

          <section className="roadmap-panel roadmap-recent-panel">
            <div className="roadmap-panel-header">
              <div>
                <h2>Recent Road Assessments</h2>
                <p>Latest records available in the RoadAI database.</p>
              </div>

              <span className="roadmap-record-count">
                {Math.min(8, analyses.length)} shown
              </span>
            </div>

            {analyses.length === 0 ? (
              <div className="roadmap-empty">
                No road assessments are available yet.
              </div>
            ) : (
              <div className="roadmap-assessment-list">
                {analyses.slice(0, 8).map((analysis) => (
                  <div className="roadmap-assessment" key={analysis.id}>
                    <div className="roadmap-assessment-id">
                      <strong>#{analysis.id}</strong>
                      <span>{analysis.filename || 'Unknown image'}</span>
                    </div>

                    <div>
                      <span className="roadmap-assessment-label">
                        Detections
                      </span>
                      <strong>
                        {Array.isArray(analysis.detections)
                          ? analysis.detections.length
                          : 0}
                      </strong>
                    </div>

                    <div>
                      <span className="roadmap-assessment-label">
                        Severity
                      </span>
                      <strong>
                        {analysis.severity?.aggregated_severity ?? '—'}
                      </strong>
                    </div>

                    <div>
                      <span className="roadmap-assessment-label">
                        Priority
                      </span>
                      <strong>
                        {analysis.priority?.final_priority_score ?? '—'}
                      </strong>
                    </div>

                    <div>
                      <span
                        className={`roadmap-level ${(
                          analysis.priority?.priority_level || ''
                        ).toLowerCase()}`}
                      >
                        {analysis.priority?.priority_level || 'Unknown'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}
