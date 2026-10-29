import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Layers, Eye, EyeOff, MapPin, ShieldAlert, Lightbulb, Users, Radio, Navigation, Maximize2 } from 'lucide-react';
import { SPATIAL_LAYERS_DATA } from '../api/client';

// Fix Leaflet default marker icons issue in React/bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// 100% Keyless, High-Resolution Map Tile Providers (No API Key Required)
const MAP_STYLES = {
  google: {
    name: 'Google Maps Road',
    url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attribution: '&copy; Google Maps'
  },
  osm: {
    name: 'OpenStreetMap',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors'
  },
  dark: {
    name: 'Esri Dark Canvas',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, DeLorme, NAVTEQ'
  },
  satellite: {
    name: 'Satellite Hybrid',
    url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attribution: '&copy; Google Satellite'
  }
};

const RISK_COLORS = {
  'Very Safe': '#10b981',
  'Safe': '#3b82f6',
  'Moderate': '#f59e0b',
  'Risky': '#f97316',
  'High Risk': '#ef4444'
};

export default function MapView({
  routes = [],
  selectedRouteId,
  onSelectRoute,
  communityReports = [],
  onMapClickSetCoords
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersGroupRef = useRef({});
  const polylineLayersRef = useRef({});

  const [mapStyle, setMapStyle] = useState('google');
  const [showCrimes, setShowCrimes] = useState(true);
  const [showLighting, setShowLighting] = useState(true);
  const [showCrowd, setShowCrowd] = useState(true);
  const [showReports, setShowReports] = useState(true);
  const [clickToPinMode, setClickToPinMode] = useState(null); // 'origin' | 'destination' | null

  // 1. Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const defaultCenter = [28.6304, 77.2177]; // Connaught Place, New Delhi
    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: 13,
      zoomControl: false
    });

    L.control.zoom({ position: 'bottomright' }).add_to = function(m) {
      L.Control.prototype.addTo.call(this, m);
    };
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Add Base Tile Layer
    const tileLayer = L.tileLayer(MAP_STYLES[mapStyle].url, {
      attribution: MAP_STYLES[mapStyle].attribution,
      maxZoom: 19
    }).addTo(map);

    mapInstanceRef.current = map;
    layersGroupRef.current.tileLayer = tileLayer;
    layersGroupRef.current.routesGroup = L.featureGroup().addTo(map);
    layersGroupRef.current.markersGroup = L.featureGroup().addTo(map);
    layersGroupRef.current.crimeGroup = L.featureGroup().addTo(map);
    layersGroupRef.current.lightingGroup = L.featureGroup().addTo(map);
    layersGroupRef.current.crowdGroup = L.featureGroup().addTo(map);
    layersGroupRef.current.reportsGroup = L.featureGroup().addTo(map);

    // Map Click Listener
    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      if (onMapClickSetCoords) {
        onMapClickSetCoords(lat, lng);
      }
    });

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // 2. Change Tile Style
  useEffect(() => {
    if (!mapInstanceRef.current || !layersGroupRef.current.tileLayer) return;
    layersGroupRef.current.tileLayer.setUrl(MAP_STYLES[mapStyle].url);
  }, [mapStyle]);

  // 3. Render Route Polylines & Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !layersGroupRef.current.routesGroup || !layersGroupRef.current.markersGroup) return;

    const routesGroup = layersGroupRef.current.routesGroup;
    const markersGroup = layersGroupRef.current.markersGroup;
    routesGroup.clearLayers();
    markersGroup.clearLayers();
    polylineLayersRef.current = {};

    if (!routes || routes.length === 0) {
      // Default view
      map.setView([28.6304, 77.2177], 13);
      return;
    }

    const allCoords = [];

    routes.forEach((route, idx) => {
      const isSelected = route.route_id === selectedRouteId || (!selectedRouteId && idx === 0);
      const riskLevel = route.risk_level || 'Moderate';
      const routeColor = RISK_COLORS[riskLevel] || '#10b981';

      const polyline = L.polyline(route.geometry, {
        color: isSelected ? routeColor : '#64748b',
        weight: isSelected ? 6 : 3.5,
        opacity: isSelected ? 0.95 : 0.45,
        dashArray: isSelected ? null : '6, 6',
        lineCap: 'round',
        lineJoin: 'round'
      });

      // Interactive Hover & Click
      polyline.on('click', () => {
        if (onSelectRoute) onSelectRoute(route.route_id);
      });

      polyline.bindTooltip(`
        <div style="font-family: system-ui; padding: 4px;">
          <strong style="color: ${routeColor};">${route.name}</strong><br/>
          <span>🛡️ Safety Score: <b>${route.safety_score}/100</b> (${riskLevel})</span><br/>
          <span>⏱️ ${route.duration_minutes} mins • 📍 ${route.distance_km} km</span>
        </div>
      `, { sticky: true, className: 'custom-map-tooltip' });

      polyline.addTo(routesGroup);
      polylineLayersRef.current[route.route_id] = polyline;

      route.geometry.forEach(pt => allCoords.push(pt));
    });

    // Add Start and End Point Markers with Pulsing Beacons
    const firstRoute = routes[0];
    const startPt = [firstRoute.origin_lat, firstRoute.origin_lng];
    const destPt = [firstRoute.dest_lat, firstRoute.dest_lng];

    // Origin Marker (Emerald Green Pulse)
    const originIcon = L.divIcon({
      className: 'custom-beacon-origin',
      html: `
        <div style="position: relative; width: 24px; height: 24px;">
          <div style="position: absolute; width: 24px; height: 24px; border-radius: 50%; background: #10b981; opacity: 0.3; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
          <div style="position: absolute; top: 4px; left: 4px; width: 16px; height: 16px; border-radius: 50%; background: #10b981; border: 2.5px solid #ffffff; box-shadow: 0 0 10px rgba(16,185,129,0.8);"></div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    L.marker(startPt, { icon: originIcon })
      .bindPopup(`<b>📍 Origin:</b><br/>${firstRoute.origin_address || 'Starting Location'}`)
      .addTo(markersGroup);

    // Destination Marker (Crimson Flag Beacon)
    const destIcon = L.divIcon({
      className: 'custom-beacon-dest',
      html: `
        <div style="position: relative; width: 24px; height: 24px;">
          <div style="position: absolute; width: 24px; height: 24px; border-radius: 50%; background: #ef4444; opacity: 0.3; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
          <div style="position: absolute; top: 4px; left: 4px; width: 16px; height: 16px; border-radius: 50%; background: #ef4444; border: 2.5px solid #ffffff; box-shadow: 0 0 10px rgba(239,68,68,0.8);"></div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    L.marker(destPt, { icon: destIcon })
      .bindPopup(`<b>🏁 Destination:</b><br/>${firstRoute.destination_address || 'Destination Point'}`)
      .addTo(markersGroup);

    // Fit map bounds to view all route corridors smoothly
    if (allCoords.length > 0) {
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16, animate: true });
    }
  }, [routes, selectedRouteId]);

  // 4. Render Spatial Layers (Crime, Lighting, Crowd, Community Reports)
  useEffect(() => {
    const { crimeGroup, lightingGroup, crowdGroup, reportsGroup } = layersGroupRef.current;
    if (!crimeGroup || !lightingGroup || !crowdGroup || !reportsGroup) return;

    // Crime Hotspots
    crimeGroup.clearLayers();
    if (showCrimes) {
      SPATIAL_LAYERS_DATA.crime_hotspots.forEach(c => {
        const circle = L.circleMarker([c.lat, c.lng], {
          radius: 6 + c.severity * 2,
          color: '#ef4444',
          fillColor: '#dc2626',
          fillOpacity: 0.6,
          weight: 1.5
        }).bindPopup(`
          <div style="font-family: system-ui;">
            <b style="color: #ef4444;">⚠️ Historical Crime Risk</b><br/>
            <span>Type: ${c.type}</span><br/>
            <span>Severity: ${c.severity}/5</span><br/>
            <span>Area: ${c.area}</span>
          </div>
        `);
        circle.addTo(crimeGroup);
      });
    }

    // Street Lighting Grid
    lightingGroup.clearLayers();
    if (showLighting) {
      SPATIAL_LAYERS_DATA.lighting_hotspots.forEach(l => {
        const circle = L.circleMarker([l.lat, l.lng], {
          radius: 5,
          color: '#facc15',
          fillColor: '#fef08a',
          fillOpacity: 0.8,
          weight: 1
        }).bindPopup(`
          <div style="font-family: system-ui;">
            <b style="color: #ca8a04;">💡 Street Lighting Sensor</b><br/>
            <span>Coverage Lux: <b>${l.lux}%</b></span><br/>
            <span>Status: ${l.status}</span><br/>
            <span>Location: ${l.street}</span>
          </div>
        `);
        circle.addTo(lightingGroup);
      });
    }

    // Crowd Density Zones
    crowdGroup.clearLayers();
    if (showCrowd) {
      SPATIAL_LAYERS_DATA.crowd_zones.forEach(cz => {
        const circle = L.circle([cz.lat, cz.lng], {
          radius: cz.radius,
          color: '#06b6d4',
          fillColor: '#06b6d4',
          fillOpacity: 0.12,
          weight: 1,
          dashArray: '4, 4'
        }).bindPopup(`
          <div style="font-family: system-ui;">
            <b style="color: #06b6d4;">👥 Public Footfall Activity Zone</b><br/>
            <span>Density Level: <b>${cz.level}</b></span><br/>
            <span>Zone: ${cz.label}</span>
          </div>
        `);
        circle.addTo(crowdGroup);
      });
    }

    // Live Community Hazard Reports
    reportsGroup.clearLayers();
    if (showReports && communityReports) {
      communityReports.forEach(r => {
        if (!r.latitude || !r.longitude) return;
        const reportIcon = L.divIcon({
          className: 'custom-report-pin',
          html: `
            <div style="background: #f59e0b; color: #000; font-size: 10px; font-weight: 800; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; border: 2px solid #fff; box-shadow: 0 0 8px #f59e0b;">
              !
            </div>
          `,
          iconSize: [18, 18],
          iconAnchor: [9, 9]
        });

        L.marker([r.latitude, r.longitude], { icon: reportIcon })
          .bindPopup(`
            <div style="font-family: system-ui; max-width: 200px;">
              <b style="color: #f59e0b;">📢 Citizen Hazard Alert</b><br/>
              <b>Category:</b> ${r.category}<br/>
              <b>Severity:</b> ${r.severity}/5<br/>
              <b>Details:</b> ${r.description || 'Reported hazard'}<br/>
              <small style="color: #94a3b8;">${r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Active'}</small>
            </div>
          `)
          .addTo(reportsGroup);
      });
    }
  }, [showCrimes, showLighting, showCrowd, showReports, communityReports]);

  // Fit bounds helper
  const handleRecenter = () => {
    if (!mapInstanceRef.current || !routes || routes.length === 0) return;
    const allCoords = [];
    routes.forEach(r => r.geometry.forEach(pt => allCoords.push(pt)));
    if (allCoords.length > 0) {
      mapInstanceRef.current.fitBounds(L.latLngBounds(allCoords), { padding: [40, 40], animate: true });
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '440px' }}>
      {/* Map Container */}
      <div 
        ref={mapContainerRef} 
        style={{ width: '100%', height: '100%', minHeight: '440px', borderRadius: 'var(--radius-md)' }} 
      />

      {/* Floating Spatial Layers Control HUD (Top Right) */}
      <div style={{
        position: 'absolute',
        top: '12px',
        right: '12px',
        zIndex: 1000,
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(12px)',
        border: '1px solid var(--border-glass)',
        borderRadius: 'var(--radius-sm)',
        padding: '8px 12px',
        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '4px' }}>
          <span style={{ fontSize: '0.73rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Layers size={12} color="#10b981" /> SPATIAL LAYERS
          </span>
          <button 
            onClick={handleRecenter}
            title="Recenter Map Bounds"
            style={{ background: 'none', border: 'none', color: '#10b981', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <Maximize2 size={12} />
          </button>
        </div>

        {/* Layer Toggles */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 8px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', cursor: 'pointer', color: showCrimes ? '#ef4444' : 'var(--text-muted)' }}>
            <input type="checkbox" checked={showCrimes} onChange={(e) => setShowCrimes(e.target.checked)} style={{ accentColor: '#ef4444' }} />
            <span>Crime Heat</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', cursor: 'pointer', color: showLighting ? '#facc15' : 'var(--text-muted)' }}>
            <input type="checkbox" checked={showLighting} onChange={(e) => setShowLighting(e.target.checked)} style={{ accentColor: '#facc15' }} />
            <span>Lighting Lux</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', cursor: 'pointer', color: showCrowd ? '#06b6d4' : 'var(--text-muted)' }}>
            <input type="checkbox" checked={showCrowd} onChange={(e) => setShowCrowd(e.target.checked)} style={{ accentColor: '#06b6d4' }} />
            <span>Crowd Footfall</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.72rem', cursor: 'pointer', color: showReports ? '#f59e0b' : 'var(--text-muted)' }}>
            <input type="checkbox" checked={showReports} onChange={(e) => setShowReports(e.target.checked)} style={{ accentColor: '#f59e0b' }} />
            <span>Citizen Alerts</span>
          </label>
        </div>

        {/* Map Style Selector */}
        <div style={{ display: 'flex', gap: '4px', marginTop: '4px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '4px' }}>
          {Object.keys(MAP_STYLES).map(key => (
            <button
              key={key}
              onClick={() => setMapStyle(key)}
              style={{
                fontSize: '0.65rem',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid',
                borderColor: mapStyle === key ? '#10b981' : 'rgba(255,255,255,0.1)',
                background: mapStyle === key ? 'rgba(16,185,129,0.2)' : 'rgba(0,0,0,0.3)',
                color: mapStyle === key ? '#10b981' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              {MAP_STYLES[key].name}
            </button>
          ))}
        </div>
      </div>

      {/* Floating Route Safety Legend (Bottom Left) */}
      <div style={{
        position: 'absolute',
        bottom: '12px',
        left: '12px',
        zIndex: 1000,
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(10px)',
        border: '1px solid var(--border-glass)',
        borderRadius: 'var(--radius-sm)',
        padding: '6px 10px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        fontSize: '0.7rem',
        color: 'var(--text-secondary)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '12px', height: '4px', background: '#10b981', borderRadius: '2px' }} />
          <span>Very Safe</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '12px', height: '4px', background: '#3b82f6', borderRadius: '2px' }} />
          <span>Safe</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '12px', height: '4px', background: '#f59e0b', borderRadius: '2px' }} />
          <span>Moderate</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '12px', height: '4px', background: '#ef4444', borderRadius: '2px' }} />
          <span>High Risk</span>
        </div>
      </div>
    </div>
  );
}
