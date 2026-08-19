import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from typing import List, Dict, Any

def render_safety_charts(routes: List[Dict[str, Any]], metadata: Dict[str, Any] = None):
    if not routes:
        return

    st.markdown("### 📊 Route Safety Factor Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Safety Score Comparison")
        route_names = [r["name"] for r in routes]
        safety_scores = [r["safety_score"] for r in routes]
        final_scores = [r["final_score"] for r in routes]

        fig1 = go.Figure(data=[
            go.Bar(name="ML Safety Score", x=route_names, y=safety_scores, marker_color="#10B981"),
            go.Bar(name="Final Decision Score", x=route_names, y=final_scores, marker_color="#3B82F6")
        ])
        fig1.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 100], title="Score"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Multi-Factor Risk Profile Breakdown")
        categories = ["Crime Risk", "Lighting Score", "Crowd Score", "Weather Risk", "Time Risk", "Report Risk"]
        
        fig2 = go.Figure()
        for r in routes:
            values = [
                r["crime_risk"],
                r["lighting_score"],
                r["crowd_score"],
                r["weather_risk"],
                r["time_risk"],
                r["report_risk"]
            ]
            fig2.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=r["name"]
            ))

        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=30, r=30, t=20, b=40),
            height=320
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Feature Importance Chart if metadata exists
    if metadata and "feature_importances" in metadata:
        st.markdown("#### 🧠 Machine Learning Model Feature Weightings")
        fi = metadata["feature_importances"]
        top_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:8]
        feat_df = {"Feature": [x[0] for x in top_fi], "Importance": [x[1] for x in top_fi]}
        
        fig3 = px.bar(
            feat_df,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale="Viridis",
            title="Top Factors Influencing Safety Score Predictions"
        )
        fig3.update_layout(yaxis=dict(autorange="reversed"), height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig3, use_container_width=True)
