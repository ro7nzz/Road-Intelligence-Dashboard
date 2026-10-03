import React from 'react';

const formatPercent = (value) => {
  if (typeof value !== 'number') return '--';
  return `${value.toFixed(2)}%`;
};

const formatScore = (value) => {
  if (typeof value !== 'number') return '--';
  return value.toFixed(2);
};

export default function ResultsPanel({ analysisResult, loading }) {
  if (loading) {
    return (
      <div
        className="glass-panel"
        style={{
          padding: '24px',
          minHeight: '420px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <h3
          style={{
            fontSize: '1.1rem',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Analysis & Prioritization Output
        </h3>

        <div
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            border: '1px dashed var(--border-color)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            padding: '40px'
          }}
        >
          <div>
            <div
              style={{
                fontSize: '1.2rem',
                color: 'var(--accent-orange)',
                marginBottom: '12px'
              }}
            >
              ANALYZING
            </div>

            <h4
              style={{
                fontSize: '1.1rem',
                color: 'var(--text-primary)',
                marginBottom: '8px'
              }}
            >
              RoadAI is processing the image...
            </h4>

            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.88rem'
              }}
            >
              YOLO detection, severity calculation and repair prioritization are running.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div
        className="glass-panel"
        style={{
          padding: '24px',
          minHeight: '420px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <h3
          style={{
            fontSize: '1.1rem',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Analysis & Prioritization Output
        </h3>

        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '36px 20px',
            border: '1px dashed var(--border-color)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            textAlign: 'center'
          }}
        >
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 127, 31, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              color: 'var(--accent-orange)',
              marginBottom: '16px'
            }}
          >
            AI
          </div>

          <h4
            style={{
              fontSize: '1.1rem',
              color: 'var(--text-primary)',
              marginBottom: '8px'
            }}
          >
            No Analysis Results Yet
          </h4>

          <p
            style={{
              maxWidth: '420px',
              color: 'var(--text-secondary)',
              fontSize: '0.88rem',
              marginBottom: '24px'
            }}
          >
            Select a road image, adjust the contextual factor scores, and click Run Analysis.
            The real RoadAI pipeline output will appear here.
          </p>
        </div>
      </div>
    );
  }

  const {
    filename,
    image_width,
    image_height,
    detections = [],
    severity = {},
    contextual_factors = {},
    priority = {},
    recommendations = [],
  } = analysisResult;

  const priorityScore = priority.final_priority_score;
  const priorityLevel = priority.priority_level || 'Unknown';
  const severityScore = severity.aggregated_severity;

  const timeline =
    priorityLevel === 'Critical'
      ? 'Site inspection within 24-48 hours'
      : priorityLevel === 'High'
        ? 'Maintenance crew inspection within 1 week'
        : 'Routine maintenance review';

  const priorityColor =
    priorityLevel === 'Critical'
      ? '#f87171'
      : priorityLevel === 'High'
        ? '#fbbf24'
        : priorityLevel === 'Moderate'
          ? '#fb923c'
          : '#4ade80';

  return (
    <div
      className="glass-panel"
      style={{
        padding: '24px',
        minHeight: '420px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}
    >
      <div>
        <h3
          style={{
            fontSize: '1.1rem',
            marginBottom: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Analysis & Prioritization Output
        </h3>

        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '0.82rem',
            margin: 0
          }}
        >
          {filename} | {image_width} x {image_height}
        </p>
      </div>

      {/* Main score cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
          gap: '12px'
        }}
      >
        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            backgroundColor: 'rgba(255,255,255,0.03)'
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            Detected Damages
          </div>
          <div
            style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: 'var(--text-primary)',
              marginTop: '5px'
            }}
          >
            {detections.length}
          </div>
        </div>

        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            backgroundColor: 'rgba(255,255,255,0.03)'
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            Damage Severity
          </div>
          <div
            style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: 'var(--accent-orange)',
              marginTop: '5px'
            }}
          >
            {formatScore(severityScore)} / 100
          </div>
        </div>

        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            backgroundColor: 'rgba(255,255,255,0.03)'
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            Priority Score
          </div>
          <div
            style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: priorityColor,
              marginTop: '5px'
            }}
          >
            {formatScore(priorityScore)} / 100
          </div>
        </div>

        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            border: `1px solid ${priorityColor}55`,
            backgroundColor: `${priorityColor}12`
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            Priority Level
          </div>
          <div
            style={{
              fontSize: '1.2rem',
              fontWeight: '700',
              color: priorityColor,
              marginTop: '8px'
            }}
          >
            {priorityLevel}
          </div>
        </div>
      </div>

      {/* Detection details */}
      <section>
        <h4 style={{ marginBottom: '10px', color: 'var(--text-primary)' }}>
          Detected Damage Details
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {detections.map((detection, index) => {
            const severityItem = severity.detections_severity?.[index];

            return (
              <div
                key={`${detection.class_id}-${index}`}
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'rgba(255,255,255,0.025)'
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    gap: '12px',
                    marginBottom: '8px'
                  }}
                >
                  <strong style={{ color: 'var(--text-primary)' }}>
                    {detection.class_name}
                  </strong>

                  <span style={{ color: 'var(--accent-orange)' }}>
                    {(detection.confidence * 100).toFixed(2)}% confidence
                  </span>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
                    gap: '6px',
                    color: 'var(--text-secondary)',
                    fontSize: '0.78rem'
                  }}
                >
                  <span>
                    Severity: {formatScore(severityItem?.calculated_severity)} / 100
                  </span>

                  <span>
                    Box area: {formatPercent(severityItem?.box_area_ratio)}
                  </span>

                  <span>
                    Class ID: {detection.class_id}
                  </span>

                  <span>
                    Base severity: {formatScore(severityItem?.base_severity)}
                  </span>
                </div>

                {detection.box && (
                  <div
                    style={{
                      marginTop: '8px',
                      color: 'var(--text-muted)',
                      fontSize: '0.74rem'
                    }}
                  >
                    Box: ({detection.box.x_min}, {detection.box.y_min}) to (
                    {detection.box.x_max}, {detection.box.y_max})
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Contextual factors */}
      <section>
        <h4 style={{ marginBottom: '10px', color: 'var(--text-primary)' }}>
          Contextual Factors
        </h4>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
            gap: '8px'
          }}
        >
          {Object.entries(contextual_factors).map(([name, value]) => (
            <div
              key={name}
              style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'rgba(255,255,255,0.025)',
                border: '1px solid var(--border-color)',
                fontSize: '0.8rem'
              }}
            >
              <div style={{ color: 'var(--text-muted)' }}>
                {name.replaceAll('_', ' ')}
              </div>
              <strong style={{ color: 'var(--text-primary)' }}>
                {formatScore(value)} / 100
              </strong>
            </div>
          ))}
        </div>
      </section>

      {/* Weighted contributions */}
      <section>
        <h4 style={{ marginBottom: '10px', color: 'var(--text-primary)' }}>
          Priority Contribution Breakdown
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {(priority.factor_contributions || []).map((factor) => (
            <div
              key={factor.factor_name}
              style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                backgroundColor: 'rgba(255,255,255,0.025)',
                display: 'grid',
                gridTemplateColumns: '1fr auto',
                gap: '8px',
                fontSize: '0.8rem'
              }}
            >
              <div>
                <div style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                  {factor.factor_name.replaceAll('_', ' ')}
                </div>
                <div style={{ color: 'var(--text-muted)' }}>
                  Score {formatScore(factor.score)} x Weight {factor.weight}
                </div>
              </div>

              <strong style={{ color: 'var(--accent-orange)' }}>
                +{formatScore(factor.contribution)}
              </strong>
            </div>
          ))}
        </div>
      </section>

      {/* Recommendations */}
      <section>
        <h4 style={{ marginBottom: '10px', color: 'var(--text-primary)' }}>
          Maintenance Recommendations
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {recommendations.map((recommendation, index) => (
            <div
              key={index}
              style={{
                padding: '11px 13px',
                borderLeft: '3px solid var(--accent-orange)',
                backgroundColor: 'rgba(255,127,31,0.06)',
                color: 'var(--text-secondary)',
                fontSize: '0.82rem',
                borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
              }}
            >
              {recommendation}
            </div>
          ))}
        </div>
      </section>

      {/* Inspection timeline */}
      <section
        style={{
          padding: '14px',
          borderRadius: 'var(--radius-md)',
          border: `1px solid ${priorityColor}55`,
          backgroundColor: `${priorityColor}0d`
        }}
      >
        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
          Recommended Response Timeline
        </div>

        <div
          style={{
            marginTop: '5px',
            fontWeight: '700',
            color: priorityColor
          }}
        >
          {timeline}
        </div>
      </section>

      {/* Explanation */}
      <section>
        <h4 style={{ marginBottom: '10px', color: 'var(--text-primary)' }}>
          Explainable Analysis
        </h4>

        <div
          style={{
            padding: '14px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(255,255,255,0.025)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.8rem',
            lineHeight: '1.6'
          }}
        >
          <strong>Severity:</strong>{' '}
          {severity.explanation || 'No severity explanation returned.'}
          <br />
          <br />
          <strong>Priority:</strong>{' '}
          {priority.explanation || 'No priority explanation returned.'}
        </div>
      </section>
    </div>
  );
}
