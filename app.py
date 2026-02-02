import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Toy Train Tracker", layout="wide")

# High-Visibility Dark Theme with Detailed Station UI
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Vertical Track Design */
    .track-container { position: relative; padding-left: 60px; margin-top: 20px; }
    .vertical-line { position: absolute; left: 75px; top: 0; bottom: 0; width: 4px; background-color: #30363d; z-index: 1; }
    .active-line { position: absolute; left: 75px; top: 0; width: 4px; background-color: #58a6ff; z-index: 2; transition: height 1.5s ease-in-out; }
    
    /* Station Nodes */
    .station-node { position: relative; margin-bottom: 100px; z-index: 3; }
    .dot { position: absolute; left: 10px; top: 12px; height: 16px; width: 16px; background-color: #8b949e; border-radius: 50%; border: 3px solid #0e1117; }
    .active-dot { background-color: #58a6ff; box-shadow: 0 0 15px #58a6ff; border-color: #ffffff; }
    
    /* Toy Train Icon Movement */
    .train-toy { font-size: 40px; position: absolute; left: 0px; z-index: 10; transition: top 1.5s ease-in-out; }
    
    /* Detailed Station Info */
    .station-info { margin-left: 45px; background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 5px solid #30363d; }
    .station-name { font-weight: bold; font-size: 20px; color: #ffffff !important; }
    .station-details { font-size: 14px; color: #58a6ff !important; font-weight: 500; margin-top: 4px; }
    .live-tag { color: #ff4b4b !important; font-weight: bold; font-size: 15px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* AI Status Panels */
    .status-box { padding: 18px; border-radius: 12px; margin-bottom: 12px; border-left: 10px solid; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .weather-panel { background-color: #f0f7ff; border-color: #2196f3; color: #000000; }
    .health-panel { background-color: #fff9f0; border-color: #ff9800; color: #000000; }
    .energy-panel { background-color: #f0fff4; border-color: #4caf50; color: #000000; }
    
    /* Launch Button Visibility */
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #1f6feb, #58a6ff); color: white !important; font-weight: bold; height: 50px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Sync")
    train_id = st.text_input("Enter Train ID", value="12673 - Cheran SF Exp")
    st.divider()
    st.markdown("## 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.info("System: Moving Block Signaling Active")

# 3. STATION DATA
railway_data = [
    {"name": "Chennai Central", "arr": "--:--", "dep": "22:10", "pf": "PF 10", "dist": "0 km"},
    {"name": "Arakkonam Jn", "arr": "23:08", "dep": "23:10", "pf": "PF 3", "dist": "69 km"},
    {"name": "Katpadi Jn", "arr": "23:58", "dep": "00:01", "pf": "PF 1", "dist": "130 km"},
    {"name": "Jolarpettai Jn", "arr": "01:23", "dep": "01:25", "pf": "PF 2", "dist": "214 km"},
    {"name": "Salem Jn", "arr": "02:57", "dep": "03:00", "pf": "PF 4", "dist": "334 km"}
]

# 4. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    tracker_placeholder = st.empty()
    
    for idx in range(len(railway_data)):
        with tracker_placeholder.container():
            col_track, col_ai = st.columns([1.3, 1])
            
            with col_track:
                st.subheader(f"📍 GPS Live Tracking")
                
                track_html = f"""
                <div class="track-container">
                    <div class="vertical-line"></div>
                    <div class="active-line" style="height: {idx * 140}px;"></div>
                    <div class="train-toy" style="top: {idx * 140}px;">🚅</div>
                """
                for i, station in enumerate(railway_data):
                    is_active = (i <= idx)
                    dot_style = "active-dot" if is_active else ""
                    live_label = "<span class='live-tag'>● LIVE NOW</span>" if i == idx else ""
                    
                    track_html += f"""
                    <div class="station-node">
                        <div class="dot {dot_style}"></div>
                        <div class="station-info" style="border-left-color: {'#58a6ff' if is_active else '#30363d'}">
                            <div class="station-name">{station['name']} {live_label}</div>
                            <div class="station-details">
                                Arr: {station['arr']} | Dep: {station['dep']} | {station['pf']} | {station['dist']}
                            </div>
                        </div>
                    </div>"""
                track_html += "</div>"
                components.html(track_html, height=800)

            with col_ai:
                st.subheader("📢 AI Analytics Feed")
                
                # Dynamic Enhancement Logic
                weather_list = [("Heavy Rain 🌧️", 28.5), ("Clear Sky ☀️", 12.0), ("Dense Fog 🌫️", 34.0)]
                weather, gap = weather_list[idx % 3]
                
                st.markdown(f"""<div class="status-box weather-panel">
                    <b>☁️ Weather Condition: {weather}</b><br>
                    AI Safety Action: Gap adjusted to <b>{gap} km</b>
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="status-box health-panel">
                    <b>🔧 Engine Health: Healthy ✅</b><br>
                    DQN Model: Section Throughput Optimized to 94%.
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"""<div class="status-box energy-panel">
                    <b>⚡ Energy Optimization: Active</b><br>
                    Fuel Saved: <b>{random.randint(12, 22)}%</b> via AI Throttle.
                </div>""", unsafe_allow_html=True)
            
            time.sleep(3) 
            
    st.balloons()
    st.success("Simulation Complete: Optimal Section Throughput Achieved.")
