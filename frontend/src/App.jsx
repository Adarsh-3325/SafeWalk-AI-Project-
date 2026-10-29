import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import RouteSearchPanel from './components/RouteSearchPanel';
import MapView from './components/MapView';
import RouteCards from './components/RouteCards';
import SafetyAnalytics from './components/SafetyAnalytics';
import CommunityReports from './components/CommunityReports';
import EmergencyToolkit from './components/EmergencyToolkit';
import SearchHistoryModal from './components/SearchHistoryModal';
import TurnByTurnSimulator from './components/TurnByTurnSimulator';
import { 
  checkBackendHealth, 
  searchSafetyRoutes, 
  fetchCommunityReports, 
  fetchSearchHistory 
} from './api/client';
import { 
  Compass, 
  BarChart2, 
  Bell, 
  Shield, 
  Sparkles, 
  Info, 
  AlertOctagon,
  ExternalLink
} from 'lucide-react';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [backendOnline, setBackendOnline] = useState(false);

  // Search parameters
  const [origin, setOrigin] = useState('Connaught Place, New Delhi');
  const [destination, setDestination] = useState('India Gate, New Delhi');
  const [hourOfDay, setHourOfDay] = useState(21);
  const [isWeekend, setIsWeekend] = useState(false);
  const [weights, setWeights] = useState({ safety: 0.70, time: 0.20, distance: 0.10 });

  // Route results
  const [routesData, setRoutesData] = useState(null);
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [loading, setLoading] = useState(false);

  // App active view
  const [activeTab, setActiveTab] = useState('navigation'); // 'navigation' | 'analytics' | 'reports'

  // Modals & Tools
  const [showSOS, setShowSOS] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [activeSimulationRoute, setActiveSimulationRoute] = useState(null);

  // Data lists
  const [communityReports, setCommunityReports] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  // 1. Initial Load & Backend Health Check
  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setBackendOnline(health.online);

      const reports = await fetchCommunityReports();
      setCommunityReports(reports);

      const history = await fetchSearchHistory();
      setSearchHistory(history);

      // Trigger initial route search
      handleSearch('Connaught Place, New Delhi', 'India Gate, New Delhi');
    }
    init();
  }, []);

  // 2. Theme Toggle Effect
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(t => (t === 'dark' ? 'light' : 'dark'));
  };

  // 3. Search Handler
  const handleSearch = async (orig = origin, dest = destination) => {
    if (!orig || !dest) return;
    setLoading(true);
    try {
      const result = await searchSafetyRoutes({
        origin: orig,
        destination: dest,
        hour_of_day: hourOfDay,
        is_weekend: isWeekend ? 1 : 0,
        weights
      });

      if (result.success && result.data) {
        setRoutesData(result.data);
        setSelectedRouteId(result.data.recommended_route_id || result.data.routes[0]?.route_id);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Re-rank dynamically when weights change
  useEffect(() => {
    if (routesData && routesData.routes) {
      handleSearch(origin, destination);
    }
  }, [hourOfDay, isWeekend, weights]);

  const handleReportSubmitted = (newReport) => {
    setCommunityReports(prev => [newReport, ...prev]);
  };

  const handleSelectHistory = (orig, dest) => {
    setOrigin(orig);
    setDestination(dest);
    handleSearch(orig, dest);
  };

  const routes = routesData?.routes || [];
  const recommendedRouteId = routesData?.recommended_route_id || routes[0]?.route_id;
  const activeSelectedRoute = routes.find(r => r.route_id === selectedRouteId) || routes[0];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* HUD Header */}
      <Header
        backendOnline={backendOnline}
        onOpenSOS={() => setShowSOS(true)}
        onOpenHistory={() => setShowHistory(true)}
        onOpenReportsModal={() => setShowReportModal(true)}
        theme={theme}
        toggleTheme={toggleTheme}
        demoMode={routesData?.demo_mode}
      />

      {/* Main Viewport Container */}
      <main style={{ flex: 1, padding: '0 16px 20px 16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        
        {/* Navigation Tabs Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setActiveTab('navigation')}
              className={activeTab === 'navigation' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.84rem', padding: '8px 16px' }}
            >
              <Compass size={15} /> Navigation & Live Map
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.84rem', padding: '8px 16px' }}
            >
              <BarChart2 size={15} /> Multi-Factor AI Analytics
            </button>

            <button
              onClick={() => setActiveTab('reports')}
              className={activeTab === 'reports' ? 'btn-primary' : 'btn-secondary'}
              style={{ fontSize: '0.84rem', padding: '8px 16px' }}
            >
              <Bell size={15} /> Community Hazard Feed
            </button>
          </div>

          {/* Quick Metrics Bar */}
          {activeSelectedRoute && (
            <div className="glass-panel" style={{ padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.78rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Active Evaluation:</span>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{activeSelectedRoute.name}</span>
              <span style={{ color: '#10b981', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
                🛡️ {Number(activeSelectedRoute.safety_score).toFixed(1)}/100
              </span>
            </div>
          )}
        </div>

        {/* TAB 1: Navigation & Live Map */}
        {activeTab === 'navigation' && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'minmax(340px, 420px) 1fr', 
            gap: '16px',
            alignItems: 'start'
          }}>
            {/* Left Column: Search & Route Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <RouteSearchPanel
                origin={origin}
                setOrigin={setOrigin}
                destination={destination}
                setDestination={setDestination}
                hourOfDay={hourOfDay}
                setHourOfDay={setHourOfDay}
                isWeekend={isWeekend}
                setIsWeekend={setIsWeekend}
                weights={weights}
                setWeights={setWeights}
                onSearch={handleSearch}
                loading={loading}
              />

              {activeSimulationRoute && (
                <TurnByTurnSimulator
                  route={activeSimulationRoute}
                  onClose={() => setActiveSimulationRoute(null)}
                />
              )}

              <RouteCards
                routes={routes}
                recommendedRouteId={recommendedRouteId}
                selectedRouteId={selectedRouteId}
                onSelectRoute={(id) => setSelectedRouteId(id)}
                onStartSimulation={(route) => setActiveSimulationRoute(route)}
              />
            </div>

            {/* Right Column: Full Interactive Leaflet Map */}
            <div className="glass-panel" style={{ padding: '6px', height: 'calc(100vh - 170px)', minHeight: '520px', position: 'sticky', top: '16px' }}>
              <MapView
                routes={routes}
                selectedRouteId={selectedRouteId}
                onSelectRoute={(id) => setSelectedRouteId(id)}
                communityReports={communityReports}
              />
            </div>
          </div>
        )}

        {/* TAB 2: Multi-Factor AI Analytics */}
        {activeTab === 'analytics' && (
          <SafetyAnalytics routes={routes} />
        )}

        {/* TAB 3: Community Hazard Feed */}
        {activeTab === 'reports' && (
          <CommunityReports
            reports={communityReports}
            onReportSubmitted={handleReportSubmitted}
          />
        )}
      </main>

      {/* Footer & Disclaimer */}
      <footer style={{ 
        padding: '12px 20px', 
        borderTop: '1px solid var(--border-glass)', 
        background: 'rgba(9, 13, 22, 0.9)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px',
        fontSize: '0.74rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Shield size={14} color="#10b981" />
          <span><b>SafeWalk AI</b> • Final Year Capstone Project • Spatial Machine Learning Route Intelligence</span>
        </div>
        <div>
          <span>⚠️ Safety scores are estimates computed from real-world crime, lighting lux & crowd datasets. Always stay vigilant.</span>
        </div>
      </footer>

      {/* Emergency SOS Modal */}
      {showSOS && (
        <EmergencyToolkit
          onClose={() => setShowSOS(false)}
          userCoords={{
            lat: activeSelectedRoute?.origin_lat || 28.6304,
            lng: activeSelectedRoute?.origin_lng || 77.2177
          }}
        />
      )}

      {/* Search History Modal */}
      {showHistory && (
        <SearchHistoryModal
          history={searchHistory}
          onSelectHistory={handleSelectHistory}
          onClose={() => setShowHistory(false)}
        />
      )}

      {/* Citizen Hazard Report Modal */}
      {showReportModal && (
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
          <div style={{ width: '100%', maxWidth: '780px' }}>
            <CommunityReports
              reports={communityReports}
              onReportSubmitted={(rep) => {
                handleReportSubmitted(rep);
                setShowReportModal(false);
              }}
              onClose={() => setShowReportModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
