import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  Shield, 
  ShieldCheck, 
  AlertTriangle, 
  Clock, 
  MapPin, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  Sparkles,
  Award,
  CheckCircle2,
  XCircle,
  Eye,
  Footprints
} from 'lucide-react';

const BADGE_CONFIG = {
  'Very Safe': { class: 'badge-very-safe', icon: '🟢', color: '#10b981' },
  'Safe': { class: 'badge-safe', icon: '🔵', color: '#06b6d4' },
  'Moderate': { class: 'badge-moderate', icon: '🟡', color: '#f59e0b' },
  'Risky': { class: 'badge-risky', icon: '🟠', color: '#f97316' },
  'High Risk': { class: 'badge-high-risk', icon: '🔴', color: '#ef4444' }
};

export default function RouteCards({
  routes = [],
  recommendedRouteId,
  selectedRouteId,
  onSelectRoute,
  onStartSimulation
}) {
  const [expandedSteps, setExpandedSteps] = useState({});

  // Trigger celebration confetti on initial recommended route load
  useEffect(() => {
    if (routes && routes.length > 0) {
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.85 },
        colors: ['#10b981', '#06b6d4', '#3b82f6']
      });
    }
  }, [routes]);

  if (!routes || routes.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <Shield size={36} color="#64748b" style={{ margin: '0 auto 12px auto', display: 'block' }} />
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>No Route Evaluated Yet</h3>
        <p style={{ fontSize: '0.82rem', marginTop: '6px' }}>
          Select an Origin and Destination above or click a quick Delhi preset to compute ML safety scores.
        </p>
      </div>
    );
  }

  const toggleSteps = (routeId) => {
    setExpandedSteps(prev => ({ ...prev, [routeId]: !prev[routeId] }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {routes.map((route, idx) => {
        const isRecommended = route.route_id === recommendedRouteId || (!recommendedRouteId && idx === 0);
        const isSelected = route.route_id === selectedRouteId || (!selectedRouteId && isRecommended);
        const riskLevel = route.risk_level || 'Moderate';
        const badgeInfo = BADGE_CONFIG[riskLevel] || BADGE_CONFIG['Moderate'];

        const origLat = route.origin_lat || 28.6304;
        const origLng = route.origin_lng || 77.2177;
        const destLat = route.dest_lat || 28.6129;
        const destLng = route.dest_lng || 77.2295;
        const gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${origLat},${origLng}&destination=${destLat},${destLng}&travelmode=walking`;

        return (
          <div
            key={route.route_id || idx}
            onClick={() => onSelectRoute(route.route_id)}
            className="glass-panel"
            style={{
              padding: '16px 18px',
              border: isRecommended ? '1.5px solid #10b981' : isSelected ? '1.5px solid #3b82f6' : '1px solid var(--border-glass)',
              background: isRecommended ? 'rgba(16, 185, 129, 0.05)' : isSelected ? 'rgba(59, 130, 246, 0.04)' : 'var(--bg-card)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'pointer'
            }}
          >
            {/* Recommended Glow Badge Ribbon */}
            {isRecommended && (
              <div style={{
                position: 'absolute',
                top: 0,
                right: 0,
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#ffffff',
                fontSize: '0.68rem',
                fontWeight: 800,
                padding: '3px 12px 3px 16px',
                borderBottomLeftRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                boxShadow: '0 2px 10px rgba(16,185,129,0.4)',
                letterSpacing: '0.03em'
              }}>
                <Award size={12} /> ★ RECOMMENDED SAFEST ROUTE
              </div>
            )}

            {/* Header: Name, Scores & Badges */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px', marginTop: isRecommended ? '8px' : '0' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    fontFamily: 'var(--font-mono)', 
                    fontSize: '0.75rem', 
                    fontWeight: 700,
                    color: 'var(--text-muted)'
                  }}>
                    #{idx + 1}
                  </span>
                  <h3 style={{ 
                    fontFamily: 'var(--font-display)', 
                    fontSize: '1.08rem', 
                    fontWeight: 700,
                    color: 'var(--text-primary)'
                  }}>
                    {route.name}
                  </h3>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} color="#10b981" /> <b>{route.distance_km} km</b>
                  </span>
                  <span>•</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={13} color="#06b6d4" /> <b>{route.duration_minutes} mins</b> walking
                  </span>
                  <span>•</span>
                  <span>Decision Index: <b style={{ color: '#10b981', fontFamily: 'var(--font-mono)' }}>{route.final_score}</b></span>
                </div>
              </div>

              {/* Safety Score Meter Pill */}
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'flex-end',
                background: 'rgba(0,0,0,0.3)',
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                border: `1px solid ${badgeInfo.color}40`
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                  <span style={{ 
                    fontSize: '1.4rem', 
                    fontWeight: 800, 
                    fontFamily: 'var(--font-mono)',
                    color: badgeInfo.color 
                  }}>
                    {Number(route.safety_score).toFixed(1)}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>/100</span>
                </div>
                <span className={`badge ${badgeInfo.class}`} style={{ fontSize: '0.62rem', padding: '1px 6px' }}>
                  {riskLevel}
                </span>
              </div>
            </div>

            {/* AI Safety Highlights & Identified Risk Factors */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '10px', 
              margin: '12px 0',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(0, 0, 0, 0.2)'
            }}>
              {/* Positive Highlights */}
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                  <CheckCircle2 size={12} /> AI Safety Highlights:
                </span>
                <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0, fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                  {route.positive_factors && route.positive_factors.length > 0 ? (
                    route.positive_factors.map((p, pIdx) => (
                      <li key={pIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '5px', marginTop: '2px' }}>
                        <span style={{ color: '#10b981' }}>✓</span> {p}
                      </li>
                    ))
                  ) : (
                    <li>✓ Standard baseline security corridor</li>
                  )}
                </ul>
              </div>

              {/* Identified Risks */}
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                  <AlertTriangle size={12} /> Identified Risk Factors:
                </span>
                <ul style={{ listStyle: 'none', paddingLeft: 0, margin: 0, fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                  {route.top_risk_factors && route.top_risk_factors.length > 0 ? (
                    route.top_risk_factors.map((r, rIdx) => (
                      <li key={rIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '5px', marginTop: '2px' }}>
                        <span style={{ color: '#f59e0b' }}>⚠</span> {r}
                      </li>
                    ))
                  ) : (
                    <li style={{ color: '#10b981' }}>✓ No critical risks flagged</li>
                  )}
                </ul>
              </div>
            </div>

            {/* Spatial Risk Metrics Matrix */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', margin: '8px 0' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)' }}>Crime Risk</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: route.crime_risk > 30 ? '#ef4444' : '#10b981', fontFamily: 'var(--font-mono)' }}>
                  {Math.round(route.crime_risk || 0)}/100
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)' }}>Lighting Lux</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: route.lighting_score >= 70 ? '#10b981' : '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                  {Math.round(route.lighting_score || 70)}/100
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)' }}>Crowd Footfall</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#06b6d4', fontFamily: 'var(--font-mono)' }}>
                  {Math.round(route.crowd_score || 60)}/100
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)' }}>Citizen Alerts</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: route.report_risk > 25 ? '#f59e0b' : '#10b981', fontFamily: 'var(--font-mono)' }}>
                  {Math.round(route.report_risk || 0)}/100
                </div>
              </div>
            </div>

            {/* Actions Bar */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <a
                  href={gmapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={isRecommended ? "btn-primary" : "btn-secondary"}
                  style={{ fontSize: '0.78rem', padding: '6px 12px', textDecoration: 'none' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink size={13} /> Open in Google Maps
                </a>

                {onStartSimulation && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onStartSimulation(route);
                    }}
                    className="btn-secondary"
                    style={{ fontSize: '0.78rem', padding: '6px 12px' }}
                    title="Simulate walking navigation along route"
                  >
                    <Footprints size={13} color="#10b981" /> Simulate Walk
                  </button>
                )}
              </div>

              {/* Turn-by-Turn Accordion Toggle */}
              {route.steps && route.steps.length > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleSteps(route.route_id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-secondary)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  <span>{expandedSteps[route.route_id] ? 'Hide Steps' : `Steps (${route.steps.length})`}</span>
                  {expandedSteps[route.route_id] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                </button>
              )}
            </div>

            {/* Turn by turn expandable list */}
            {expandedSteps[route.route_id] && route.steps && (
              <div style={{
                marginTop: '10px',
                paddingTop: '10px',
                borderTop: '1px solid rgba(255,255,255,0.06)',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}>
                {route.steps.map((step, sIdx) => (
                  <div key={sIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    <span style={{ 
                      width: '18px', 
                      height: '18px', 
                      borderRadius: '50%', 
                      background: 'rgba(16,185,129,0.15)', 
                      color: '#10b981',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      {sIdx + 1}
                    </span>
                    <div style={{ flex: 1 }}>
                      <span>{step.instruction}</span>
                      {step.distance_km && (
                        <span style={{ color: 'var(--text-muted)', marginLeft: '6px', fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>
                          ({step.distance_km} km)
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
