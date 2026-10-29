import React, { useState } from 'react';
import { 
  Bell, 
  Send, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  Filter,
  PlusCircle,
  X
} from 'lucide-react';
import { submitCommunityReport } from '../api/client';

const CATEGORIES = [
  'Poor Lighting',
  'Harassment',
  'Suspicious Activity',
  'Accident',
  'Theft',
  'Unsafe Area',
  'Road Block',
  'Other'
];

export default function CommunityReports({
  reports = [],
  onReportSubmitted,
  onClose
}) {
  const [category, setCategory] = useState('Poor Lighting');
  const [severity, setSeverity] = useState(3);
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState(28.6304);
  const [longitude, setLongitude] = useState(77.2177);
  const [submitting, setSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('All');

  const handleUseCurrentGPS = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(Number(pos.coords.latitude.toFixed(5)));
          setLongitude(Number(pos.coords.longitude.toFixed(5)));
        },
        () => {
          // Default Delhi Connaught Place
          setLatitude(28.6304);
          setLongitude(77.2177);
        }
      );
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setStatusMsg({ type: 'error', text: 'Please enter a description for the hazard report.' });
      return;
    }

    setSubmitting(true);
    setStatusMsg(null);

    const payload = {
      category,
      severity: Number(severity),
      description: description.trim(),
      latitude: Number(latitude),
      longitude: Number(longitude)
    };

    const res = await submitCommunityReport(payload);
    setSubmitting(false);

    if (res.success) {
      setStatusMsg({ type: 'success', text: '🎉 Safety report submitted & pinned on Delhi spatial grid successfully!' });
      setDescription('');
      if (onReportSubmitted) {
        onReportSubmitted(res.data);
      }
    } else {
      setStatusMsg({ type: 'error', text: res.detail || 'Failed to submit report. Please try again.' });
    }
  };

  const filteredReports = selectedFilter === 'All' 
    ? reports 
    : reports.filter(r => r.category === selectedFilter);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '18px' }}>
      {/* Submission Form */}
      <div className="glass-panel" style={{ padding: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <PlusCircle size={18} color="#10b981" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Report Community Hazard</h3>
          </div>
          {onClose && (
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={18} />
            </button>
          )}
        </div>

        <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
          Help improve Delhi neighborhood walking safety by reporting dark alleys, broken streetlights, or suspicious activity.
        </p>

        {statusMsg && (
          <div style={{
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '12px',
            fontSize: '0.78rem',
            background: statusMsg.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${statusMsg.type === 'success' ? '#10b981' : '#ef4444'}`,
            color: statusMsg.type === 'success' ? '#10b981' : '#ef4444',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            {statusMsg.type === 'success' ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Hazard Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              >
                {CATEGORIES.map((c, idx) => (
                  <option key={idx} value={c} style={{ background: '#0f172a' }}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Severity: <b style={{ color: severity >= 4 ? '#ef4444' : '#f59e0b' }}>{severity}/5</b>
                </label>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
              />
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                GPS Location (Delhi Coordinates)
              </label>
              <button
                type="button"
                onClick={handleUseCurrentGPS}
                style={{ background: 'none', border: 'none', color: '#06b6d4', fontSize: '0.7rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px' }}
              >
                <MapPin size={11} /> Auto-Detect GPS
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <input
                type="number"
                step="0.0001"
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value))}
                placeholder="Latitude"
                style={{
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-mono)'
                }}
              />
              <input
                type="number"
                step="0.0001"
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value))}
                placeholder="Longitude"
                style={{
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-mono)'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Description & Street Details
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the safety concern (e.g. broken streetlights near metro exit 2, dark isolated alleyway)..."
              style={{
                width: '100%',
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-primary)',
                fontSize: '0.8rem',
                outline: 'none',
                resize: 'none'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn-primary"
            style={{ width: '100%', padding: '10px' }}
          >
            {submitting ? 'Submitting Report...' : (
              <>
                <Send size={14} /> Submit Citizen Safety Report
              </>
            )}
          </button>
        </form>
      </div>

      {/* Active Reports Feed */}
      <div className="glass-panel" style={{ padding: '18px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={18} color="#f59e0b" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Active Delhi Community Alerts</h3>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {filteredReports.length} Alerts
          </span>
        </div>

        {/* Category Filters */}
        <div style={{ display: 'flex', gap: '5px', overflowX: 'auto', paddingBottom: '6px', marginBottom: '10px' }}>
          {['All', 'Poor Lighting', 'Harassment', 'Road Block', 'Suspicious Activity'].map((f, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedFilter(f)}
              style={{
                padding: '3px 8px',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.68rem',
                border: '1px solid',
                borderColor: selectedFilter === f ? '#10b981' : 'rgba(255,255,255,0.08)',
                background: selectedFilter === f ? 'rgba(16,185,129,0.15)' : 'rgba(0,0,0,0.2)',
                color: selectedFilter === f ? '#10b981' : 'var(--text-secondary)',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Reports List */}
        <div style={{ flex: 1, overflowY: 'auto', maxHeight: '360px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredReports.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              No active reports in this category.
            </div>
          ) : (
            filteredReports.map((r, idx) => (
              <div
                key={r.id || idx}
                style={{
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid rgba(255,255,255,0.04)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--text-primary)' }}>
                    {r.category}
                  </span>
                  <span className={`badge ${r.severity >= 4 ? 'badge-high-risk' : r.severity >= 3 ? 'badge-risky' : 'badge-moderate'}`} style={{ fontSize: '0.62rem' }}>
                    Severity {r.severity}/5
                  </span>
                </div>

                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '2px 0' }}>
                  {r.description}
                </p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <MapPin size={10} /> {r.latitude?.toFixed(4)}, {r.longitude?.toFixed(4)}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <Clock size={10} /> {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Active Alert'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
