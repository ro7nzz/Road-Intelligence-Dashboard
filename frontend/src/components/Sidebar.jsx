import React from 'react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '&#128202;' },
    { id: 'analysis', label: 'New Analysis', icon: '&#128269;' },
    { id: 'history', label: 'Analysis History', icon: '&#128196;' },
    { id: 'map', label: 'Road Map', icon: '&#128506;&#65039;' },
    { id: 'settings', label: 'Settings', icon: '&#9881;&#65039;' },
  ];

  return (
    <aside style={{
      width: '260px',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-color)',
      padding: '24px 16px',
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      flexShrink: 0
    }}>
      <div style={{
        padding: '0 12px 24px 12px',
        borderBottom: '1px solid var(--border-color)',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, #ff6b00 0%, #ff9f43 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            boxShadow: '0 4px 12px rgba(255, 107, 0, 0.35)'
          }}>
            &#128739;&#65039;
          </div>

          <div>
            <h1
              className="gradient-text"
              style={{
                fontSize: '1.4rem',
                fontWeight: '800',
                lineHeight: '1'
              }}
            >
              RoadAI
            </h1>

            <span style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              fontWeight: '500'
            }}>
              Municipal Intelligence
            </span>
          </div>
        </div>
      </div>

      <nav style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        flex: 1
      }}>
        {navItems.map((item) => {
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                backgroundColor: isActive
                  ? 'rgba(255, 107, 0, 0.14)'
                  : 'transparent',
                color: isActive
                  ? '#ff8a3d'
                  : 'var(--text-secondary)',
                fontWeight: isActive ? '600' : '400',
                fontSize: '0.92rem',
                textAlign: 'left',
                width: '100%',
                transition: 'var(--transition-fast)',
                borderLeft: isActive
                  ? '3px solid #ff6b00'
                  : '3px solid transparent',
                cursor: 'pointer'
              }}
            >
              <span
                style={{ fontSize: '1.1rem' }}
                dangerouslySetInnerHTML={{ __html: item.icon }}
              />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div style={{
        padding: '12px 14px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid var(--border-color)',
        fontSize: '0.75rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{
          fontWeight: '600',
          color: 'var(--text-secondary)',
          marginBottom: '2px'
        }}>
          Final Year Project
        </div>

        <span>YOLO11n &bull; FastAPI &bull; SQLite</span>
      </div>
    </aside>
  );
}
