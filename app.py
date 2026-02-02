import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Indian Rail AI Simulator", layout="wide")

# High-Visibility Dark Theme CSS for Tracking Visibility
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Vertical Track Design - Indian Railway Style */
    .track-container { position: relative; padding-left: 60px; margin-top: 20px; }
    .vertical-line { position: absolute; left: 75px; top: 0; bottom: 0; width: 4px; background-color: #30363d; z-index: 1; }
    .active-line { position: absolute; left: 75px; top: 0; width: 4px; background-color: #58a6ff; z-index: 2; transition: height 1.5s ease-in-out; }
    
    /* Station Nodes */
    .station-node { position: relative; margin-bottom: 80px; z-index: 3; }
    .dot { position: absolute; left: 10px; top: 8px; height: 14px; width: 14px; background-color: #8b949e; border-radius: 50%; border: 3px solid #0e1117; }
    .active-dot { background-color: #58a6ff; box-shadow: 0 0 15px #58a6ff; border-color: #ffffff; }
    
    /* Moving Train Icon (Locomotive) */
    .train-icon { font-size: 35px; position: absolute; left: 0px; z-index: 10; transition: top 1.5s ease-in-out; }
    
    .station-info { margin-left: 45px; }
    .station-name { font-weight: bold; font-size: 22px; color: #f0f6fc; }
    .live-tag { color: #ff7b72; font-weight: bold; font-size: 16px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Analytics Panels based on Enhancements */
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .weather-panel { background-color: #f0f7ff; border-color: #2196f3; color: #000000; }
    .health-panel { background-color: #fff9f0; border-color: #ff9800; color: #000000; }
    .energy-panel { background-color: #f0fff4; border-color: #4caf50; color: #000000; }
    .pis-panel { background-color: #1e3d59; border-color: #58a6ff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - Global GPS Search (Indian Routes)
with st.sidebar:
    st.markdown("## 🛰️ Indian Rail GPS Search")
    train_id = st.text_input("Enter Train ID (e.g., 12673)", value="12673")
    locomotive = st.selectbox("Select Locomotive Type", ["WAP-7", "Vande Bharat", "WAG-9"])
    st.divider()
    st.markdown("### 💡 AI Methodology")
    st.write("DQN AI optimizes Section Throughput in busy Indian Railway corridors.")
    st.info("System: Moving Block Signaling Active")

# 3. MAIN DASHBOARD
st.title(f"🚉 AI-Powered Indian Railway Simulator ({locomotive})")

if st.button("🚀 Start Live Indian Route Simulation"):
    # Real-world Indian Route: Mumbai Central to New Delhi Corridor
    stations = ["Mumbai Central", "Surat Jn", "Vadodara Jn", "Kota Jn", "New Delhi"]
    
    track_placeholder = st.empty()
    
    # Movement Simulation Loop
    for idx in range(len(stations)):
        with track_placeholder.container():
            col_map, col_ai = st.columns([1, 1.2])
            
            with col_map:
                st.subheader(f"📍 GPS Live Tracking: {train_id}")
                
                # Dynamic Vertical Track Construction
                track_html = f"""
                <div class="track-container">
                    <div class="vertical-line"></div>
                    <div class="active-line" style="height: {idx * 110}px;"></div>
                    <div class="train-icon" style="top: {idx * 110}px;">🚅</div>
                """
                for i, s in enumerate(stations):
                    is_active = (i <= idx)
                    dot_style = "active-dot" if is_active else ""
                    live_label = "<div class='live-tag'>● LIVE NOW</div>" if i == idx else "<div style='color:#8b949e;'>Scheduled</div>"
                    
                    track_html += f"""
                    <div class="station-node">
                        <div class="dot {dot_style}"></div>
                        <div class="station-info">
                            <div class="station-name">{s}</div>
                            {live_label}
                        </div>
                    </div>"""
                track_html += "</div>"
                components.html(track_html, height=600)

            with col_ai:
                st.subheader("📢 AI Precision Dispatch Feed")
                
                # Dynamic Enhancement Updates based on Station Progress
                weather_info = [("Clear Sky ☀️", 12.0), ("Heavy Rain 🌧️", 25.5), ("Dense Fog 🌫️", 34.8)]
                weather, gap = weather_info[idx % 3]
                
                # Enhancement 1: Weather Integration
                st.markdown(f"""<div class="status-box weather-panel">
                    <b>☁️ Weather (GPS Sync): {weather}</b><br>
                    AI Safety Gap: <b>{gap} km</b> (DQN Optimized)
                </div>""", unsafe_allow_html=True)
                
                # Enhancement 2: Predictive Maintenance
                st.markdown(f"""<div class="status-box health-panel">
                    <b>🔧 Loco Health ({locomotive}): Healthy ✅</b><br>
                    AI Analytics: Vibration levels stable across section.
                </div>""", unsafe_allow_html=True)
                
                # Enhancement 3: Energy Efficiency
                st.markdown(f"""<div class="status-box energy-panel">
                    <b>⚡ Energy Optimization: Active</b><br>
                    Efficiency: <b>{random.randint(12, 25)}% Power Saved</b> via AI Throttle.
                </div>""", unsafe_allow_html=True)

                # Enhancement 4: PIS Accuracy
                if idx < len(stations) - 1:
                    st.markdown(f"""<div class="status-box pis-panel">
                        <b>🔮 Precise PIS Prediction</b><br>
                        Expected Arrival at {stations[idx+1]} in {random.randint(30, 90)} mins.
                    </div>""", unsafe_allow_html=True)
            
            # Simulated travel time for visual effect
            time.sleep(2.5) 
            
    st.balloons()
    st.success("Simulation Complete: Maximum section throughput achieved.")
