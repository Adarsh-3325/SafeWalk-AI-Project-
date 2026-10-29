import React, { useState, useRef, useEffect } from 'react';
import { 
  AlertTriangle, 
  Phone, 
  PhoneCall, 
  Volume2, 
  VolumeX, 
  Copy, 
  Check, 
  ShieldAlert, 
  Radio, 
  X, 
  UserCheck, 
  MapPin 
} from 'lucide-react';

export default function EmergencyToolkit({ onClose, userCoords = { lat: 28.6304, lng: 77.2177 } }) {
  const [sirenActive, setSirenActive] = useState(false);
  const [copied, setCopied] = useState(false);
  const [fakeCallActive, setFakeCallActive] = useState(false);
  const [callAnswered, setCallAnswered] = useState(false);
  const [callDuration, setCallDuration] = useState(0);

  const audioCtxRef = useRef(null);
  const oscRef = useRef(null);
  const sirenIntervalRef = useRef(null);

  // Web Audio API synthesized siren
  const startSiren = () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sawtooth';
      gain.gain.value = 0.4;
      osc.connect(gain);
      gain.connect(ctx.destination);

      let freq = 800;
      let goingUp = true;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      osc.start();

      sirenIntervalRef.current = setInterval(() => {
        if (goingUp) {
          freq += 80;
          if (freq >= 1400) goingUp = false;
        } else {
          freq -= 80;
          if (freq <= 700) goingUp = true;
        }
        if (osc) {
          osc.frequency.setValueAtTime(freq, ctx.currentTime);
        }
      }, 50);

      audioCtxRef.current = ctx;
      oscRef.current = osc;
      setSirenActive(true);
    } catch (err) {
      console.warn('Audio API unavailable:', err);
    }
  };

  const stopSiren = () => {
    if (sirenIntervalRef.current) clearInterval(sirenIntervalRef.current);
    if (oscRef.current) {
      try { oscRef.current.stop(); } catch (e) {}
    }
    if (audioCtxRef.current) {
      try { audioCtxRef.current.close(); } catch (e) {}
    }
    setSirenActive(false);
  };

  useEffect(() => {
    return () => {
      stopSiren();
    };
  }, []);

  // Fake call timer
  useEffect(() => {
    let interval;
    if (callAnswered) {
      interval = setInterval(() => {
        setCallDuration(d => d + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [callAnswered]);

  const handleCopyDistressMessage = () => {
    const time = new Date().toLocaleTimeString();
    const msg = `🚨 EMERGENCY ALERT: I feel unsafe at Delhi location (Lat: ${userCoords.lat}, Lng: ${userCoords.lng}) at ${time}. Map link: https://maps.google.com/?q=${userCoords.lat},${userCoords.lng} - SafeWalk AI Distress Protocol.`;
    navigator.clipboard.writeText(msg);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(5, 8, 16, 0.85)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
      padding: '16px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '520px',
        padding: '24px',
        border: '1.5px solid rgba(239, 68, 68, 0.4)',
        boxShadow: '0 0 40px rgba(239, 68, 68, 0.3)',
        position: 'relative'
      }}>
        {/* Close Button */}
        <button
          onClick={() => {
            stopSiren();
            onClose();
          }}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #ef4444'
          }}>
            <AlertTriangle size={20} color="#ef4444" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ef4444' }}>
              Emergency SOS Response Hub
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Instant distress triggers, speed dials & deterrence tools for Delhi pedestrians.
            </p>
          </div>
        </div>

        {/* Fake Call Active Screen */}
        {fakeCallActive ? (
          <div style={{
            background: '#090d16',
            borderRadius: '16px',
            padding: '20px',
            textAlign: 'center',
            border: '1px solid rgba(255,255,255,0.1)',
            marginBottom: '16px'
          }}>
            {!callAnswered ? (
              <>
                <div style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                  margin: '0 auto 12px auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  animation: 'pulse-glow 1.5s infinite'
                }}>
                  <PhoneCall size={30} color="#fff" />
                </div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Security Dispatch / Family</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '4px 0 16px 0' }}>Incoming Call...</p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
                  <button
                    onClick={() => setCallAnswered(true)}
                    className="btn-primary"
                    style={{ background: '#10b981', borderRadius: '50%', width: '52px', height: '52px', padding: 0 }}
                  >
                    <Phone size={22} />
                  </button>
                  <button
                    onClick={() => { setFakeCallActive(false); setCallAnswered(false); }}
                    className="btn-sos"
                    style={{ borderRadius: '50%', width: '52px', height: '52px', padding: 0 }}
                  >
                    <PhoneCall size={22} style={{ transform: 'rotate(135deg)' }} />
                  </button>
                </div>
              </>
            ) : (
              <>
                <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#10b981' }}>Call in Progress</h4>
                <p style={{ fontSize: '1.2rem', fontFamily: 'var(--font-mono)', margin: '8px 0' }}>
                  {Math.floor(callDuration / 60)}:{String(callDuration % 60).padStart(2, '0')}
                </p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  Simulating active call deterrent. Speak loudly: <i>"Yes, I'm almost at the metro station, see you in 2 mins."</i>
                </p>
                <button
                  onClick={() => { setFakeCallActive(false); setCallAnswered(false); setCallDuration(0); }}
                  className="btn-sos"
                  style={{ width: '100%' }}
                >
                  End Call
                </button>
              </>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* 1-Click Distress Broadcast */}
            <div style={{
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ef4444', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Radio size={14} /> 1-Click GPS Distress Message
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Lat: {userCoords.lat}, Lng: {userCoords.lng}
                </span>
              </div>
              <p style={{ fontSize: '0.73rem', color: 'var(--text-secondary)' }}>
                Copies an urgent emergency alert containing your current coordinates and live Google Maps beacon to send via SMS / WhatsApp.
              </p>
              <button
                onClick={handleCopyDistressMessage}
                className="btn-secondary"
                style={{ width: '100%', fontSize: '0.82rem', borderColor: '#ef4444' }}
              >
                {copied ? (
                  <>
                    <Check size={14} color="#10b981" /> Distress Message Copied to Clipboard!
                  </>
                ) : (
                  <>
                    <Copy size={14} /> Copy Urgent GPS Distress Alert
                  </>
                )}
              </button>
            </div>

            {/* Deterrent Tools: High-Decibel Siren & Fake Call */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {/* Loud Siren */}
              <button
                onClick={sirenActive ? stopSiren : startSiren}
                className={sirenActive ? "btn-sos glow-sos" : "btn-secondary"}
                style={{ padding: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}
              >
                {sirenActive ? <VolumeX size={20} /> : <Volume2 size={20} color="#ef4444" />}
                <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>
                  {sirenActive ? 'SILENCE ALARM' : 'SOUND SIREN'}
                </span>
              </button>

              {/* Fake Incoming Call */}
              <button
                onClick={() => setFakeCallActive(true)}
                className="btn-secondary"
                style={{ padding: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}
              >
                <PhoneCall size={20} color="#06b6d4" />
                <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>TRIGGER FAKE CALL</span>
              </button>
            </div>

            {/* Official Delhi Emergency Speed Dials */}
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
                Official Delhi Helpline Direct Dials:
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <a
                  href="tel:112"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', fontSize: '0.78rem', justifyContent: 'flex-start' }}
                >
                  <Phone size={13} color="#ef4444" /> <b>112</b> - National Emergency
                </a>
                <a
                  href="tel:1091"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', fontSize: '0.78rem', justifyContent: 'flex-start' }}
                >
                  <Phone size={13} color="#f59e0b" /> <b>1091</b> - Women Helpline
                </a>
                <a
                  href="tel:100"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', fontSize: '0.78rem', justifyContent: 'flex-start' }}
                >
                  <Phone size={13} color="#3b82f6" /> <b>100</b> - Police Control
                </a>
                <a
                  href="tel:102"
                  className="btn-secondary"
                  style={{ textDecoration: 'none', fontSize: '0.78rem', justifyContent: 'flex-start' }}
                >
                  <Phone size={13} color="#10b981" /> <b>102</b> - Ambulance
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
