import streamlit as st
from typing import Dict, Any, List

def render_route_card(route: Dict[str, Any], is_recommended: bool = False):
    safety_score = route["safety_score"]
    risk_level = route["risk_level"]
    final_score = route["final_score"]

    # Color definitions
    if safety_score >= 80:
        badge_bg = "#DEF7EC"
        badge_color = "#03543F"
        border_color = "#10B981"
    elif safety_score >= 60:
        badge_bg = "#E1EFFE"
        badge_color = "#1E40AF"
        border_color = "#3B82F6"
    elif safety_score >= 40:
        badge_bg = "#FEF08A"
        badge_color = "#854D0E"
        border_color = "#F59E0B"
    else:
        badge_bg = "#FDE8E8"
        badge_color = "#9B1C1C"
        border_color = "#EF4444"

    rec_tag = """<span style="background-color: #10B981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 8px;">★ RECOMMENDED</span>""" if is_recommended else ""

    positive_items_html = "".join([f"<li style='color:#065F46;'>✓ {f}</li>" for f in route.get("positive_factors", [])])
    risk_items_html = "".join([f"<li style='color:#991B1B;'>⚠ {f}</li>" for f in route.get("top_risk_factors", [])])

    card_html = f"""
    <div style="
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #1E293B; font-size: 18px;">
                    {route['name']} {rec_tag}
                </h3>
                <p style="margin: 4px 0 0 0; color: #64748B; font-size: 13px;">
                    Distance: <b>{route['distance_km']} km</b> &nbsp;|&nbsp; ETA: <b>{route['duration_minutes']} mins</b>
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: 800; color: {border_color};">
                    {safety_score}<span style="font-size: 14px; font-weight: normal; color: #64748B;">/100</span>
                </div>
                <span style="
                    background-color: {badge_bg};
                    color: {badge_color};
                    padding: 2px 10px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                ">
                    {risk_level}
                </span>
            </div>
        </div>

        <hr style="margin: 12px 0; border: none; border-top: 1px solid #F1F5F9;">

        <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <div>
                <strong style="color: #334155;">Why this route?</strong>
                <ul style="margin: 4px 0 0 0; padding-left: 18px; font-size: 12px;">
                    {positive_items_html or "<li style='color:#64748B;'>Standard route safety baseline</li>"}
                </ul>
            </div>
            {"<div style='max-width: 45%;'><strong style='color: #991B1B;'>Risk Factors:</strong><ul style='margin: 4px 0 0 0; padding-left: 18px; font-size: 12px;'>" + risk_items_html + "</ul></div>" if risk_items_html else ""}
        </div>

        <div style="margin-top: 10px; background-color: #F8FAFC; padding: 6px 12px; border-radius: 6px; font-size: 12px; color: #475569; display: flex; justify-content: space-between;">
            <span>Overall Decision Score: <b>{final_score}</b></span>
            <span>Crime Risk: <b>{route['crime_risk']}/100</b> | Lighting: <b>{route['lighting_score']}/100</b></span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
