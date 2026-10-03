import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../services/apiConfig';

export default function AnalysisHistory() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);
        setError('');

        const response = await fetch(API_ENDPOINTS.ANALYSES);

        if (!response.ok) {
          throw new Error(`Failed to load history (${response.status})`);
        }

        const data = await response.json();
        setAnalyses(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message || 'Unable to load analysis history.');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const openAnalysis = async (id) => {
    try {
      setDetailsLoading(true);

      const response = await fetch(`${API_ENDPOINTS.ANALYSES}/${id}`);

      if (!response.ok) {
        throw new Error(`Failed to load analysis details (${response.status})`);
      }

      const data = await response.json();
      setSelectedAnalysis(data);
    } catch (err) {
      setError(err.message || 'Unable to load analysis details.');
    } finally {
      setDetailsLoading(false);
    }
  };

  const getLevelClass = (level) => {
    switch (level) {
      case 'Critical':
        return 'history-level critical';
      case 'High':
        return 'history-level high';
      case 'Moderate':
        return 'history-level moderate';
      case 'Low':
        return 'history-level low';
      default:
        return 'history-level';
    }
  };

  const formatDate = (value) => {
    if (!value) return '—';

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return value;

    return date.toLocaleString();
  };

  return (
    <main className="history-page">
      <div className="history-header">
        <div>
          <div className="history-eyebrow">ROADAi / RECORDS</div>
          <h1>Analysis History</h1>
          <p>
            Review previously processed road-damage analyses and repair-priority results.
          </p>
        </div>

        <div className="history-count">
          <span>{analyses.length}</span>
          <small>Total Analyses</small>
        </div>
      </div>

      {loading && (
        <div className="history-state">
          <div className="history-spinner"></div>
          <h3>Loading analysis history...</h3>
          <p>Fetching records from the RoadAI backend.</p>
        </div>
      )}

      {!loading && error && !selectedAnalysis && (
        <div className="history-state history-error">
          <div className="history-state-icon">!</div>
          <h3>Unable to load history</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && analyses.length === 0 && (
        <div className="history-state">
          <div className="history-state-icon">AI</div>
          <h3>No Analysis Records</h3>
          <p>Run an analysis from the Dashboard to create your first history record.</p>
        </div>
      )}

      {!loading && !error && analyses.length > 0 && (
        <div className="history-table-wrapper">
          <div className="history-table-header">
            <span>Analysis</span>
            <span>Image</span>
            <span>Detections</span>
            <span>Severity</span>
            <span>Priority</span>
            <span>Created</span>
          </div>

          {analyses.map((analysis) => {
            const priority = analysis.priority || {};
            const severity = analysis.severity || {};

            return (
              <button
                className="history-row"
                key={analysis.id}
                onClick={() => openAnalysis(analysis.id)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  cursor: 'pointer',
                  font: 'inherit',
                  color: 'inherit'
                }}
              >
                <div className="history-id">
                  <strong>#{analysis.id}</strong>
                  <small>Road Damage Analysis</small>
                </div>

                <div className="history-image">
                  <strong>{analysis.filename || 'Unknown image'}</strong>
                  <small>
                    {analysis.image_width || '—'} × {analysis.image_height || '—'}
                  </small>
                </div>

                <div className="history-detections">
                  {Array.isArray(analysis.detections)
                    ? analysis.detections.length
                    : '—'}
                </div>

                <div className="history-severity">
                  <strong>{severity.aggregated_severity ?? '—'}</strong>
                  <small>/ 100</small>
                </div>

                <div>
                  <strong className="history-score">
                    {priority.final_priority_score ?? '—'}
                  </strong>

                  <div className={getLevelClass(priority.priority_level)}>
                    {priority.priority_level || 'Unknown'}
                  </div>
                </div>

                <div className="history-date">
                  {formatDate(analysis.created_at)}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {detailsLoading && (
        <div className="history-modal-backdrop">
          <div className="history-modal">
            <div className="history-spinner"></div>
            <h3>Loading Analysis</h3>
            <p>Retrieving complete analysis details...</p>
          </div>
        </div>
      )}

      {selectedAnalysis && !detailsLoading && (
        <div
          className="history-modal-backdrop"
          onClick={() => setSelectedAnalysis(null)}
        >
          <div
            className="history-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="history-modal-header">
              <div>
                <div className="history-eyebrow">ANALYSIS DETAILS</div>
                <h2>Analysis #{selectedAnalysis.id}</h2>
              </div>

              <button
                className="history-close"
                onClick={() => setSelectedAnalysis(null)}
              >
                ×
              </button>
            </div>

            <div className="history-detail-grid">
              <div className="history-detail-card">
                <span>Image</span>
                <strong>{selectedAnalysis.filename || '—'}</strong>
              </div>

              <div className="history-detail-card">
                <span>Dimensions</span>
                <strong>
                  {selectedAnalysis.image_width || '—'} ×{' '}
                  {selectedAnalysis.image_height || '—'}
                </strong>
              </div>

              <div className="history-detail-card">
                <span>Detections</span>
                <strong>
                  {Array.isArray(selectedAnalysis.detections)
                    ? selectedAnalysis.detections.length
                    : '—'}
                </strong>
              </div>

              <div className="history-detail-card">
                <span>Severity</span>
                <strong>
                  {selectedAnalysis.severity?.aggregated_severity ?? '—'} / 100
                </strong>
              </div>

              <div className="history-detail-card">
                <span>Priority Score</span>
                <strong>
                  {selectedAnalysis.priority?.final_priority_score ?? '—'}
                </strong>
              </div>

              <div className="history-detail-card">
                <span>Priority Level</span>
                <strong className={getLevelClass(
                  selectedAnalysis.priority?.priority_level
                )}>
                  {selectedAnalysis.priority?.priority_level || '—'}
                </strong>
              </div>
            </div>

            <div className="history-detail-section">
              <h3>Contextual Factors</h3>

              <div className="history-factor-grid">
                {Object.entries(selectedAnalysis.contextual_factors || {}).map(
                  ([key, value]) => (
                    <div className="history-factor" key={key}>
                      <span>{key.replaceAll('_', ' ')}</span>
                      <strong>{value}</strong>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="history-detail-section">
              <h3>Maintenance Recommendations</h3>

              <ul>
                {(selectedAnalysis.recommendations || []).map(
                  (recommendation, index) => (
                    <li key={index}>{recommendation}</li>
                  )
                )}
              </ul>
            </div>

            <div className="history-detail-section">
              <h3>Created</h3>
              <p>{formatDate(selectedAnalysis.created_at)}</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
