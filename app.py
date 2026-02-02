import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Live Simulator", layout="wide")

# High-Visibility Dark Theme CSS for Tracking Visibility
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Vertical Track Design */
    .track-container { position: relative; padding-left: 60px; margin-top: 20px; }
    .vertical-line { position: absolute; left: 75px; top: 0; bottom: 0; width: 4px; background-color: #30363d; z-index: 1; }
    .active-line { position: absolute; left: 75px; top: 0; width: 4px; background-color: #58a6ff; z-index: 2; transition: height 1.5s ease-in-out; }
    
    /* Station Nodes */
    .station-node { position: relative; margin-bottom: 80px; z-index: 3; }
    .dot { position: absolute; left: 10px; top: 8px; height: 14px; width: 14px; background-color: #8b949e; border-radius: 50%; border: 3px solid #0e1117; }
    .active-dot { background-color: #58a6ff; box-shadow: 0 0 15px #58a6ff; border-color: #ffffff; }
    
    /* Moving Train Icon */
    .train-icon { font-size: 35px; position: absolute; left: 0px; z-index: 10; transition: top 1.5s ease-in-out; }
    
    .station-info { margin-left: 45px; }
    .station-name { font-weight: bold; font-size: 22px; color: #f0f6fc; }
    .live-tag { color: #ff7b72; font-weight: bold; font-size: 16px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Analytics Panels */
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .weather-panel { background-color: #f0f7ff; border-color: #2196f3; color: #000000; }
    .health-panel { background-color: #fff9f0; border-color: #ff9800; color: #000000; }
    .energy-panel { background-color: #f0fff4; border-color: #4caf50; color: #000000; }
    .pis-panel { background-color: #1e3d59; border-color: #58a6ff; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - Global GPS Search
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train ID / Number", value="12673")
    st.divider()
    st.markdown("### 💡 AI Methodology")
    st.write("DQN AI optimizes 'Ghost Space' to maximize track throughput.")
    st.info("System: Moving Block Signaling Enabled")

# 3. MAIN DASHBOARD
st.title("🚉 AI-Powered Live Train Movement Simulator")

if st.button("🛰️ Start Real-Time Simulation"):
    # Real-Time Stations List
    stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn", "Salem Jn"]
    
    # Placeholder for Dynamic Movement
    track_placeholder = st.empty()
    
    # Movement Simulation Loop
    for idx in range(len(stations)):
        with track_placeholder.container():
            col_map, col_ai = st.columns([1, 1.2])
            
            with col_map:
                st.subheader(f"📍 GPS Live Status: {train_id}")
                
                # Vertical Movement Visuals
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
                st.subheader("📢 AI Precision Dispatch Orders")
                
                # Dynamic AI Analytics Feed
                weather_info = [("Clear Sky ☀️", 12.5), ("Heavy Rain 🌧️", 24.8), ("Dense Fog 🌫️", 35.0)]
                weather, gap = weather_info[idx % 3]
                
                st.markdown(f"""<div class="status-box weather-panel">
                    <b>☁️ Weather: {weather}</b><br>
                    AI Action: Safety Gap adjusted to <b>{gap} km</b>
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="status-box health-panel">
                    <b>🔧 Engine Health: Healthy ✅</b><br>
                    Real-time vibration analysis completed.
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="status-box energy-panel">
                    <b>⚡ Energy Optimization: Active</b><br>
                    Fuel Saved: <b>{random.randint(10, 20)}%</b> via AI Throttle.
                </div>""", unsafe_allow_html=True)

                if idx < len(stations) - 1:
                    st.markdown(f"""<div class="status-box pis-panel">
                        <b>🔮 PIS Precise Arrival</b><br>
                        Expected at {stations[idx+1]} in {random.randint(15, 30)} mins.
                    </div>""", unsafe_allow_html=True)
            
            # Simulation delay to show movement
            time.sleep(2.5) 
            
    st.balloons()
    st.success("Simulation Complete: All Agents safely dispatched with maximum throughput.")
