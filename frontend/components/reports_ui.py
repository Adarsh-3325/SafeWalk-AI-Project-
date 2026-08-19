import requests
import streamlit as st
from typing import List, Dict, Any

def render_report_submission_form(backend_url: str):
    st.markdown("### 📢 Report a Community Safety Issue")
    st.caption("Help improve neighborhood navigation safety by reporting poorly lit areas, harassment incidents, or hazards.")

    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                ["Poor Lighting", "Harassment", "Suspicious Activity", "Accident", "Theft", "Unsafe Area", "Road Block", "Other"]
            )
            severity = st.slider("Severity Level (1 = Low Hazard, 5 = Critical Risk)", 1, 5, 2)

        with col2:
            lat = st.number_input("Latitude", value=37.7749, format="%.6f")
            lng = st.number_input("Longitude", value=-122.4194, format="%.6f")

        description = st.text_area("Description / Additional Details", placeholder="Describe the safety concern...")
        submitted = st.form_submit_button("Submit Safety Report", use_container_width=True)

        if submitted:
            payload = {
                "category": category,
                "severity": severity,
                "description": description,
                "latitude": lat,
                "longitude": lng
            }
            try:
                res = requests.post(f"{backend_url}/api/reports", json=payload, timeout=5)
                if res.status_code == 201:
                    st.success("Thank you! Your safety report has been submitted and stored successfully.")
                else:
                    st.error(f"Failed to submit report: {res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Backend connection error: {e}")

def render_recent_reports(backend_url: str):
    st.markdown("### 📋 Active Community Safety Reports")
    try:
        res = requests.get(f"{backend_url}/api/reports", timeout=5)
        if res.status_code == 200:
            reports = res.json()
            if not reports:
                st.info("No active community reports found.")
                return

            report_data = []
            for r in reports[:15]:
                report_data.append({
                    "ID": r["id"],
                    "Category": r["category"],
                    "Severity": f"{r['severity']}/5",
                    "Description": r.get("description", ""),
                    "Latitude": r["latitude"],
                    "Longitude": r["longitude"],
                    "Date": r.get("created_at", "")[:10] if r.get("created_at") else ""
                })
            st.dataframe(report_data, use_container_width=True)
        else:
            st.warning("Unable to fetch community reports.")
    except Exception as e:
        st.warning(f"Backend connection error: {e}")
