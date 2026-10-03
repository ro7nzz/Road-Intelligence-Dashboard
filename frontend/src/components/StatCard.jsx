import React, { useState } from 'react';
import AnimatedCounter from './AnimatedCounter';

const colorMap = {
  indigo: {
    icon: '#818cf8',
    glow: 'rgba(99, 102, 241, 0.18)',
    line: '#818cf8',
  },
  rose: {
    icon: '#fb7185',
    glow: 'rgba(244, 63, 94, 0.18)',
    line: '#fb7185',
  },
  amber: {
    icon: '#fbbf24',
    glow: 'rgba(245, 158, 11, 0.18)',
    line: '#fbbf24',
  },
  cyan: {
    icon: '#22d3ee',
    glow: 'rgba(6, 182, 212, 0.18)',
    line: '#22d3ee',
  },
};

const sparklineData = {
  indigo: '0,30 10,27 20,29 30,20 40,23 50,15 60,18 70,10 80,14 90,6 100,9',
  rose: '0,29 10,25 20,27 30,18 40,21 50,12 60,17 70,9 80,13 90,5 100,8',
  amber: '0,28 10,26 20,23 30,25 40,17 50,19 60,12 70,15 80,8 90,11 100,5',
  cyan: '0,31 10,28 20,30 30,22 40,24 50,17 60,19 70,12 80,15 90,7 100,10',
};

export default function StatCard({
  title,
  icon,
  color = 'indigo',
  value,
  subtitle = 'Live database',
  index = 0,
}) {
  const [isHovered, setIsHovered] = useState(false);

  const colors = colorMap[color] || colorMap.indigo;
  const points = sparklineData[color] || sparklineData.indigo;

  return (
    <div
      className="glass-panel roadAI-stat-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'relative',
        overflow: 'hidden',
        padding: '22px',
        minHeight: '160px',
        animationDelay: `${index * 80}ms`,
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        boxShadow: isHovered
          ? `0 16px 40px rgba(0, 0, 0, 0.28), 0 0 24px ${colors.glow}`
          : 'var(--shadow-sm)',
        borderColor: isHovered
          ? colors.icon
          : 'var(--border-color)',
        transition:
          'transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: '-35px',
          right: '-35px',
          width: '110px',
          height: '110px',
          borderRadius: '50%',
          background: colors.glow,
          filter: 'blur(25px)',
          pointerEvents: 'none',
        }}
      />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: colors.glow,
            color: colors.icon,
            fontSize: '1.25rem',
            fontWeight: '700',
          }}
        >
          {icon}
        </div>

        <span
          style={{
            fontSize: '0.7rem',
            fontWeight: '700',
            letterSpacing: '0.08em',
            color: colors.icon,
          }}
        >
          LIVE
        </span>
      </div>

      <div
        style={{
          marginTop: '16px',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            fontSize: '2rem',
            fontWeight: '800',
            lineHeight: 1,
            color: 'var(--text-primary)',
          }}
        >
          <AnimatedCounter
            value={value}
            duration={800}
          />
        </div>

        <div
          style={{
            marginTop: '8px',
            fontSize: '0.82rem',
            fontWeight: '600',
            color: 'var(--text-primary)',
          }}
        >
          {title}
        </div>

        <div
          style={{
            marginTop: '3px',
            fontSize: '0.72rem',
            color: 'var(--text-secondary)',
          }}
        >
          {subtitle}
        </div>
      </div>

      <svg
        className="roadAI-sparkline"
        viewBox="0 0 100 35"
        preserveAspectRatio="none"
        aria-hidden="true"
        style={{
          position: 'absolute',
          left: '22px',
          right: '22px',
          bottom: '8px',
          width: 'calc(100% - 44px)',
          height: '34px',
          opacity: isHovered ? 0.8 : 0.45,
          transition: 'opacity 200ms ease',
          pointerEvents: 'none',
        }}
      >
        <polyline
          points={points}
          fill="none"
          stroke={colors.line}
          strokeWidth="1.8"
          vectorEffect="non-scaling-stroke"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}