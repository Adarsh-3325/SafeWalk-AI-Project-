import React, { useState } from 'react';
import { 
  Search, 
  MapPin, 
  Navigation, 
  Clock, 
  Calendar, 
  Sliders, 
  ArrowUpDown, 
  Zap, 
  ShieldCheck, 
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const DELHI_PRESETS = [
  { label: 'CP ➔ India Gate', origin: 'Connaught Place, New Delhi', dest: 'India Gate, New Delhi', tag: 'Central' },
  { label: 'Hauz Khas ➔ Saket', origin: 'Hauz Khas Village, Delhi', dest: 'Saket Metro Station, Delhi', tag: 'South' },
  { label: 'Karol Bagh ➔ Chandni Chowk', origin: 'Karol Bagh, Delhi', dest: 'Chandni Chowk, Delhi', tag: 'Old Delhi' },
  { label: 'AIIMS ➔ Lajpat Nagar', origin: 'AIIMS Hospital, Delhi', dest: 'Central Market Lajpat Nagar, Delhi', tag: 'Medical' },
  { label: 'Dwarka Mor ➔ Cyber City', origin: 'Dwarka Mor, Delhi', dest: 'Cyber City, Gurgaon', tag: 'Transit' },
  { label: 'DU North Campus ➔ Red Fort', origin: 'Delhi University North Campus', dest: 'Red Fort, Delhi', tag: 'Heritage' }
];

export default function RouteSearchPanel({
  origin,
  setOrigin,
  destination,
  setDestination,
  hourOfDay,
  setHourOfDay,
  isWeekend,
  setIsWeekend,
  weights,
  setWeights,
  onSearch,
  loading
}) {
  const [showWeights, setShowWeights] = useState(false);

  const handleSwap = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handlePresetSelect = (preset) => {
    setOrigin(preset.origin);
    setDestination(preset.dest);
    onSearch(preset.origin, preset.dest);
  };

  const isNightHour = hourOfDay >= 21 || hourOfDay <= 5;

  return (
    <div className="glass-panel" style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Search Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Navigation size={18} color="#10b981" />
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700 }}>
            Safety Route Navigator
          </h2>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Delhi Spatial Engine
        </span>
      </div>

      {/* Quick Presets Pills */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
          <Zap size={13} color="#f59e0b" />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Quick Delhi Corridors:
          </span>
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {DELHI_PRESETS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handlePresetSelect(p)}
              className="btn-secondary"
              style={{
                fontSize: '0.73rem',
                padding: '4px 9px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)'
              }}
            >
              📍 {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Group */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', position: 'relative' }}>
        {/* Origin */}
        <div style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            display: 'flex',
            alignItems: 'center',
            color: '#10b981'
          }}>
            <MapPin size={16} />
          </div>
          <input
            type="text"
            placeholder="Starting Point / Landmark (e.g. Connaught Place)"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            style={{
              width: '100%',
              padding: '11px 14px 11px 38px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-glass)',
              color: 'var(--text-primary)',
              fontSize: '0.88rem',
              outline: 'none',
              transition: 'border 0.2s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#10b981'}
            onBlur={(e) => e.target.style.borderColor = 'var(--border-glass)'}
          />
        </div>

        {/* Swap Button */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '-4px 0' }}>
          <button
            onClick={handleSwap}
            title="Swap Origin and Destination"
            style={{
              background: 'rgba(30, 41, 59, 0.9)',
              border: '1px solid var(--border-glass)',
              color: 'var(--text-secondary)',
              borderRadius: '50%',
              width: '26px',
              height: '26px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              zIndex: 2,
              transition: 'all 0.2s'
            }}
          >
            <ArrowUpDown size={13} />
          </button>
        </div>

        {/* Destination */}
        <div style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            display: 'flex',
            alignItems: 'center',
            color: '#ef4444'
          }}>
            <MapPin size={16} />
          </div>
          <input
            type="text"
            placeholder="Destination Point / Landmark (e.g. India Gate)"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            style={{
              width: '100%',
              padding: '11px 14px 11px 38px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-glass)',
              color: 'var(--text-primary)',
              fontSize: '0.88rem',
              outline: 'none',
              transition: 'border 0.2s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#ef4444'}
            onBlur={(e) => e.target.style.borderColor = 'var(--border-glass)'}
          />
        </div>
      </div>

      {/* Environmental & Temporal Factors */}
      <div style={{ 
        background: 'rgba(0, 0, 0, 0.2)', 
        borderRadius: 'var(--radius-sm)', 
        padding: '12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={14} color={isNightHour ? '#f59e0b' : '#06b6d4'} />
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>
              Travel Time: <span style={{ color: '#10b981', fontFamily: 'var(--font-mono)' }}>{String(hourOfDay).padStart(2, '0')}:00 hrs</span>
            </span>
          </div>
          {isNightHour && (
            <span className="badge badge-risky" style={{ fontSize: '0.65rem' }}>
              <AlertCircle size={10} /> Night Risk Mode
            </span>
          )}
        </div>

        <input
          type="range"
          min="0"
          max="23"
          value={hourOfDay}
          onChange={(e) => setHourOfDay(Number(e.target.value))}
          style={{ width: '100%' }}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
          <span>00:00 (Midnight)</span>
          <span>12:00 (Noon)</span>
          <span>23:00 (Late Night)</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.8rem' }}>
            <input
              type="checkbox"
              checked={isWeekend}
              onChange={(e) => setIsWeekend(e.target.checked)}
              style={{ accentColor: '#10b981', cursor: 'pointer' }}
            />
            <span>Weekend Footfall Profile</span>
          </label>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {isWeekend ? 'Sat/Sun density' : 'Weekday baseline'}
          </span>
        </div>
      </div>

      {/* Advanced Route Weighting Drawer */}
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px' }}>
        <button
          onClick={() => setShowWeights(!showWeights)}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            fontSize: '0.78rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            padding: '4px 0'
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sliders size={13} color="#10b981" /> Decision Ranking Weights
          </span>
          {showWeights ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {showWeights && (
          <div style={{ 
            marginTop: '10px', 
            padding: '10px', 
            background: 'rgba(0,0,0,0.25)', 
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', marginBottom: '2px' }}>
                <span>🛡️ ML Safety Score ({Math.round(weights.safety * 100)}%)</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={weights.safety}
                onChange={(e) => setWeights({ ...weights, safety: Number(e.target.value) })}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', marginBottom: '2px' }}>
                <span>⏱️ Travel Time ({Math.round(weights.time * 100)}%)</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.6"
                step="0.05"
                value={weights.time}
                onChange={(e) => setWeights({ ...weights, time: Number(e.target.value) })}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', marginBottom: '2px' }}>
                <span>📍 Distance ({Math.round(weights.distance * 100)}%)</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.4"
                step="0.05"
                value={weights.distance}
                onChange={(e) => setWeights({ ...weights, distance: Number(e.target.value) })}
              />
            </div>
          </div>
        )}
      </div>

      {/* Primary Action Button */}
      <button
        onClick={() => onSearch(origin, destination)}
        disabled={loading || !origin.trim() || !destination.trim()}
        className="btn-primary glow-emerald"
        style={{ width: '100%', padding: '13px', fontSize: '0.98rem' }}
      >
        {loading ? (
          <>
            <span style={{ 
              display: 'inline-block', 
              width: '16px', 
              height: '16px', 
              border: '2px solid #ffffff', 
              borderTopColor: 'transparent', 
              borderRadius: '50%', 
              animation: 'spin 0.8s linear infinite' 
            }} />
            <span>Analyzing Delhi Spatial Risk...</span>
          </>
        ) : (
          <>
            <Search size={18} />
            <span>EVALUATE SAFEST ROUTE</span>
          </>
        )}
      </button>
    </div>
  );
}
