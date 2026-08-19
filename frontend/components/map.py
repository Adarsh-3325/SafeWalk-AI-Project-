import folium
from streamlit_folium import st_folium
from typing import List, Dict, Any

def render_route_map(
    routes: List[Dict[str, Any]],
    crime_incidents: List[Dict[str, Any]] = None,
    user_reports: List[Dict[str, Any]] = None,
    selected_route_id: str = None
):
    if not routes:
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=13, tiles="CartoDB positron")
        return st_folium(m, width=None, height=500, use_container_width=True)

    first_route = routes[0]
    geom = first_route.get("geometry", [])
    start_lat = first_route.get("origin_lat", geom[0][0] if geom else 37.7749)
    start_lng = first_route.get("origin_lng", geom[0][1] if geom else -122.4194)
    dest_lat = first_route.get("dest_lat", geom[-1][0] if geom else 37.7925)
    dest_lng = first_route.get("dest_lng", geom[-1][1] if geom else -122.4012)

    center_lat = (start_lat + dest_lat) / 2.0
    center_lng = (start_lng + dest_lng) / 2.0

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=13,
        tiles="CartoDB positron"
    )

    # Add Start and End Markers
    folium.Marker(
        location=[start_lat, start_lng],
        popup=f"<b>Start:</b> {first_route['origin_address']}",
        tooltip="Origin Point",
        icon=folium.Icon(color="green", icon="play", prefix="fa")
    ).add_to(m)

    folium.Marker(
        location=[dest_lat, dest_lng],
        popup=f"<b>Destination:</b> {first_route['destination_address']}",
        tooltip="Destination Point",
        icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa")
    ).add_to(m)

    # Route polyline colors
    colors = {
        "Very Safe": "#10B981", # Emerald Green
        "Safe": "#3B82F6",      # Blue
        "Moderate": "#F59E0B",  # Amber
        "Risky": "#F97316",     # Orange
        "High Risk": "#EF4444"  # Red
    }

    # Plot polylines
    for r in routes:
        is_selected = (r["route_id"] == selected_route_id) or (selected_route_id is None and r.get("is_recommended"))
        risk_level = r.get("risk_level", "Moderate")
        color = colors.get(risk_level, "#6B7280")

        weight = 7 if is_selected else 4
        opacity = 0.95 if is_selected else 0.55

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 180px;">
            <h4 style="margin:0 0 5px 0; color: #1E293B;">{r['name']}</h4>
            <b>Safety Score:</b> <span style="color:{color}; font-weight:bold;">{r['safety_score']}/100</span><br>
            <b>Risk Level:</b> {r['risk_level']}<br>
            <b>Distance:</b> {r['distance_km']} km<br>
            <b>ETA:</b> {r['duration_minutes']} min<br>
            <b>Final Score:</b> {r['final_score']}
        </div>
        """

        folium.PolyLine(
            locations=r["geometry"],
            color=color if is_selected else "#94A3B8",
            weight=weight,
            opacity=opacity,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{r['name']} ({r['safety_score']}/100 Safety)"
        ).add_to(m)

    # Optional Crime incident markers overlay
    if crime_incidents:
        for c in crime_incidents[:40]: # Limit for performance
            folium.CircleMarker(
                location=[c["latitude"], c["longitude"]],
                radius=4 + c.get("severity", 1),
                color="#DC2626",
                fill=True,
                fill_color="#EF4444",
                fill_opacity=0.6,
                popup=f"<b>Crime Incident:</b> {c['crime_type']}<br>Severity: {c['severity']}/5",
                tooltip=f"Crime: {c['crime_type']}"
            ).add_to(m)

    # Optional User report markers overlay
    if user_reports:
        for r in user_reports[:30]:
            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                popup=f"<b>Report:</b> {r['category']}<br>{r.get('description', '')}",
                tooltip=f"User Report: {r['category']}",
                icon=folium.Icon(color="purple", icon="exclamation-triangle", prefix="fa")
            ).add_to(m)

    return st_folium(m, width=None, height=520, use_container_width=True)
