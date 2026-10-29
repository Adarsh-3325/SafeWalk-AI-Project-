import React from 'react';
import { Shield, Radio, Bell, History, AlertTriangle, Moon, Sun, Sparkles, Navigation } from 'lucide-react';

export default function Header({ 
  backendOnline, 
  onOpenSOS, 
  onOpenHistory, 
  onOpenReportsModal,
  theme,
  toggleTheme,
  demoMode
}) {
  return (
    <header className="glass-panel" style={{ 
      margin: '12px 16px', 
      padding: '12px 20px', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px',
      position: 'relative',
      zIndex: 100
    }}>
      {/* Brand Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ 
          position: 'relative', 
          width: '42px', 
          height: '42px', 
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(16, 185, 129, 0.45)'
        }}>
          <Shield size={24} color="#ffffff" strokeWidth={2.5} />
          <span style={{ 
            position: 'absolute', 
            top: '-2px', 
            right: '-2px', 
            width: '10px', 
            height: '10px', 
            borderRadius: '50%', 
            background: '#06b6d4',
            border: '2px solid #090d16'
          }} />
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ 
              fontFamily: 'var(--font-display)', 
              fontSize: '1.4rem', 
              fontWeight: 800, 
              letterSpacing: '-0.02em',
              background: 'linear-gradient(90deg, #ffffff 0%, #a7f3d0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: 'inline-block'
            }}>
              SafeWalk <span style={{ color: '#10b981', WebkitTextFillColor: '#10b981' }}>AI</span>
            </h1>
            <span className="badge badge-very-safe" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
              <Sparkles size={11} /> ML Core v2.0
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            Machine Learning-Powered Safety-Aware Urban Navigation & Risk Assessment
          </p>
        </div>
      </div>

      {/* Status & Actions Hub */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        {/* Backend Heartbeat */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '6px', 
          padding: '6px 12px',
          borderRadius: 'var(--radius-full)',
          background: backendOnline ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
          border: `1px solid ${backendOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
          fontSize: '0.75rem',
          fontWeight: 600,
          color: backendOnline ? '#10b981' : '#f59e0b'
        }}>
          <span style={{ 
            width: '7px', 
            height: '7px', 
            borderRadius: '50%', 
            background: backendOnline ? '#10b981' : '#f59e0b',
            boxShadow: `0 0 8px ${backendOnline ? '#10b981' : '#f59e0b'}` 
          }} />
          {backendOnline ? 'FastAPI Live' : 'Simulation Mode'}
        </div>

        {/* Delhi Region Active */}
        <div style={{ 
          display: 'none',
          alignItems: 'center', 
          gap: '5px', 
          padding: '6px 12px',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          fontSize: '0.75rem',
          fontWeight: 600,
          color: '#06b6d4',
          '@media (min-width: 768px)': { display: 'flex' }
        }}>
          <Navigation size={12} /> Delhi NCR Spatial Grid
        </div>

        {/* Report Hazard Modal Trigger */}
        <button 
          onClick={onOpenReportsModal}
          className="btn-secondary"
          title="Submit Delhi Community Safety Alert"
          style={{ fontSize: '0.8rem', padding: '6px 12px' }}
        >
          <Bell size={14} color="#f59e0b" /> Report Hazard
        </button>

        {/* Search History */}
        <button 
          onClick={onOpenHistory}
          className="btn-secondary"
          title="View Search History"
          style={{ fontSize: '0.8rem', padding: '6px 12px' }}
        >
          <History size={14} /> History
        </button>

        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          className="btn-secondary"
          title="Toggle Light/Dark Theme"
          style={{ padding: '6px 10px' }}
        >
          {theme === 'dark' ? <Sun size={15} color="#fbbf24" /> : <Moon size={15} color="#6366f1" />}
        </button>

        {/* Emergency SOS High-Decibel Button */}
        <button 
          onClick={onOpenSOS}
          className="btn-sos glow-sos"
          title="Emergency SOS Toolkit & Siren Alarm"
        >
          <AlertTriangle size={15} /> SOS EMERGENCY
        </button>
      </div>
    </header>
  );
}
