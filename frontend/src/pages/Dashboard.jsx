import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../services/apiConfig';
import Header from '../components/Header';
import StatCard from '../components/StatCard';
import AnalysisUpload from '../components/AnalysisUpload';
import ContextFactors from '../components/ContextFactors';
import ResultsPanel from '../components/ResultsPanel';

async function fetchDashboardStats() {
  const response = await fetch(API_ENDPOINTS.ANALYSES);

  if (!response.ok) {
    throw new Error('Unable to load dashboard statistics.');
  }

  const analyses = await response.json();

  const stats = {
    total: Array.isArray(analyses) ? analyses.length : 0,
    critical: 0,
    high: 0,
    detections: 0,
  };

  if (Array.isArray(analyses)) {
    analyses.forEach((analysis) => {
      const level = analysis?.priority?.priority_level;

      if (level === 'Critical') {
        stats.critical += 1;
      } else if (level === 'High') {
        stats.high += 1;
      }

      if (Array.isArray(analysis?.detections)) {
        stats.detections += analysis.detections.length;
      }
    });
  }

  return stats;
}

export default function Dashboard({ mode = 'dashboard' }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const [factors, setFactors] = useState({
    location_risk: 50,
    road_importance: 50,
    traffic: 50,
    complaints: 20,
    historical_recurrence: 20,
  });

  const [notification, setNotification] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [dashboardStats, setDashboardStats] = useState({
    total: undefined,
    critical: undefined,
    high: undefined,
    detections: undefined,
  });

  useEffect(() => {
    fetchDashboardStats()
      .then((stats) => {
        setDashboardStats(stats);
      })
      .catch((error) => {
        console.error('RoadAI dashboard statistics error:', error);
      });
  }, []);

  const handleRunAnalysis = async () => {
    if (!selectedFile) {
      setNotification({
        type: 'warning',
        text: 'Please select a road image file before running analysis.'
      });
      return;
    }

    setLoading(true);
    setNotification(null);

    try {
      const formData = new FormData();

      formData.append('file', selectedFile);
      formData.append('location_risk', factors.location_risk);
      formData.append('road_importance', factors.road_importance);
      formData.append('traffic', factors.traffic);
      formData.append('complaints', factors.complaints);
      formData.append(
        'historical_recurrence',
        factors.historical_recurrence
      );

      const response = await fetch(API_ENDPOINTS.ANALYZE, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || 'RoadAI analysis failed. Please try again.'
        );
      }

      setAnalysisResult(data);

      setNotification({
        type: 'success',
        text: `Analysis completed successfully for "${selectedFile.name}".`
      });

      fetchDashboardStats()
        .then((stats) => {
          setDashboardStats(stats);
        })
        .catch((error) => {
          console.error('RoadAI dashboard refresh error:', error);
        });

    } catch (error) {
      console.error('RoadAI analysis error:', error);

      setAnalysisResult(null);

      setNotification({
        type: 'error',
        text: error.message || 'Unable to connect to the RoadAI backend.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        flex: 1,
        padding: '30px',
        maxWidth: '1400px',
        margin: '0 auto',
        width: '100%'
      }}
    >
      <Header />

      {mode === 'dashboard' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '20px',
            marginBottom: '32px'
          }}
        >
          <StatCard
            title="Total Analyses"
            icon="📑"
            color="indigo"
            value={dashboardStats.total}
            subtitle="Stored assessments"
            index={0}
          />

          <StatCard
            title="Critical Issues"
            icon="🚨"
            color="rose"
            value={dashboardStats.critical}
            subtitle="Critical priority"
            index={1}
          />

          <StatCard
            title="High Priority"
            icon="⚠️"
            color="amber"
            value={dashboardStats.high}
            subtitle="High priority"
            index={2}
          />

          <StatCard
            title="Detected Damages"
            icon="🔍"
            color="cyan"
            value={dashboardStats.detections}
            subtitle="Across all analyses"
            index={3}
          />
        </div>
      )}

      {notification && (
        <div
          style={{
            backgroundColor:
              notification.type === 'warning'
                ? 'rgba(245, 158, 11, 0.15)'
                : notification.type === 'error'
                  ? 'rgba(239, 68, 68, 0.15)'
                  : notification.type === 'success'
                    ? 'rgba(34, 197, 94, 0.15)'
                    : 'rgba(99, 102, 241, 0.15)',
            border:
              notification.type === 'warning'
                ? '1px solid rgba(245, 158, 11, 0.3)'
                : notification.type === 'error'
                  ? '1px solid rgba(239, 68, 68, 0.3)'
                  : notification.type === 'success'
                    ? '1px solid rgba(34, 197, 94, 0.3)'
                    : '1px solid rgba(99, 102, 241, 0.3)',
            color:
              notification.type === 'warning'
                ? '#fbbf24'
                : notification.type === 'error'
                  ? '#fca5a5'
                  : notification.type === 'success'
                    ? '#86efac'
                    : '#a5b4fc',
            padding: '14px 20px',
            borderRadius: 'var(--radius-md)',
            marginBottom: '24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.9rem'
          }}
        >
          <span>{notification.text}</span>

          <button
            onClick={() => setNotification(null)}
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              fontSize: '1.1rem',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(450px, 1fr))',
          gap: '28px',
          alignItems: 'start'
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '24px'
          }}
        >
          <AnalysisUpload
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
          />

          <ContextFactors
            factors={factors}
            setFactors={setFactors}
          />

          <button
            className="btn-primary"
            onClick={handleRunAnalysis}
            disabled={loading}
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '1.05rem',
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'wait' : 'pointer'
            }}
          >
            <span>{loading ? '⏳' : '▶'}</span>{' '}
            {loading
              ? 'Analyzing Road Damage...'
              : 'Run RoadAI Analysis'}
          </button>
        </div>

        <div>
          <ResultsPanel
            analysisResult={analysisResult}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}