import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Footprints, ShieldCheck, MapPin, X, CheckCircle } from 'lucide-react';

export default function TurnByTurnSimulator({ route, onClose }) {
  if (!route || !route.steps || route.steps.length === 0) return null;

  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  const totalSteps = route.steps.length;
  const progressPercent = Math.round(((currentStep + 1) / totalSteps) * 100);

  useEffect(() => {
    let timer;
    if (isPlaying && currentStep < totalSteps - 1) {
      timer = setTimeout(() => {
        setCurrentStep(s => s + 1);
      }, 3500);
    } else if (currentStep >= totalSteps - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStep, totalSteps]);

  const step = route.steps[currentStep];

  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.95)',
      backdropFilter: 'blur(16px)',
      border: '1.5px solid #10b981',
      borderRadius: 'var(--radius-md)',
      padding: '16px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    }}>
      {/* Simulation Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Footprints size={18} color="#10b981" />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Live Walking Navigation Simulator
          </h4>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={16} />
        </button>
      </div>

      {/* Progress Bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
          <span>Step {currentStep + 1} of {totalSteps}</span>
          <span style={{ fontFamily: 'var(--font-mono)', color: '#10b981', fontWeight: 700 }}>{progressPercent}% Complete</span>
        </div>
        <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
          <div style={{ width: `${progressPercent}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)', transition: 'width 0.5s ease' }} />
        </div>
      </div>

      {/* Current Instruction Display */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: 'var(--radius-sm)',
        padding: '12px',
        border: '1px solid rgba(255,255,255,0.06)'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            background: '#10b981',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '0.8rem',
            flexShrink: 0
          }}>
            {currentStep + 1}
          </div>
          <div>
            <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {step.instruction}
            </p>
            {step.distance_km && (
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                Distance for this segment: {step.distance_km} km
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Simulation Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 12px' }}
          >
            {isPlaying ? <><Pause size={13} /> Pause</> : <><Play size={13} /> Resume</>}
          </button>
          <button
            onClick={() => { setCurrentStep(0); setIsPlaying(true); }}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '6px 10px' }}
          >
            <RotateCcw size={13} /> Restart
          </button>
        </div>

        <span className="badge badge-very-safe" style={{ fontSize: '0.65rem' }}>
          <ShieldCheck size={11} /> Safety Corridor Guard Active
        </span>
      </div>
    </div>
  );
}
