import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# High-Visibility CSS for Dark Theme
st.markdown("""
    <style>
    /* Main Dark Background */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Styling - Clean Dark Slate */
    section[data-testid="stSidebar"] { 
        background-color: #161b22 !important; 
        border-right: 1px solid #30363d; 
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Vertical Tracker UI - Ultra Visibility */
    .station-node { border-left: 4px solid #58a6ff; margin-left: 45px; padding: 25px; position: relative; }
    .station-name { font-weight: bold; font-size: 22px; color: #ffffff !important; text-shadow: 1px 1px 2px #000; }
    .train-icon { font-size: 38px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-text { color: #ff4b4b !important; font-weight: bold; font-size: 18px; text-transform: uppercase; }
    .scheduled-text { color: #8b949e !important; font-size: 16px; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Notification Panels - Exact Match from your Screenshot */
    .status-box { padding: 22px; border-radius: 12px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 15px rgba(0,0,0,0.4); }
    
    .weather-panel { background-color: #e3f2fd; border-color: #2196f3; color: #0d47a1; } /* Blue */
    .health-panel { background-color: #fff3e0; border-color: #ff9800; color: #e65100; }  /* Orange */
    .energy-panel { background-color: #e8f5e9; border-color: #4caf50; color: #1b5e20; }  /* Green */
    .pis-panel { background-color: #1e3d59; border-color: #58a6ff; color: #ffffff; }     /* Dark Blue */
    
    /* Global Sync Button */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        background: linear-gradient(90deg, #1f6feb, #58a6ff); 
        color: white !important; 
        font-weight: bold; 
        height: 55px; 
        font-size: 18px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - Matching Image 2 Logic
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train ID / Number", value="12673")
    st.markdown("---")
    st.markdown("## 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.info("System: Moving Block Signaling Active")

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    # Simulated Global Real-time Data (Enhancements 2, 3, 4)
    weather_list = [("Heavy Rain 🌧️", 28.5), ("Cloudy Sky ☁️", 15.2), ("Dense Fog 🌫️", 34.0)]
    weather, gap = random.choice(weather_list)
    energy_saved = random.randint(12, 22)
    
    with st.spinner("Connecting to Global Satellite Feed..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Real-Time GPS Tracking")
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_live = (s == stations[curr_idx])
            icon = "🚅" if is_live else ""
            line_color = "#58a6ff" if stations.index(s) <= curr_idx else "#30363d"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {"<div class='live-text'>● LIVE NOW</div>" if is_live else "<div class='scheduled-text'>Scheduled</div>"}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=500)

    with col_data:
        st.subheader("📢 AI Analytics Feed")
        
        # 1. Weather Panel (Blue)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Response: Safety Gap increased to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance (Orange)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Analysis: Predictive sensors show optimal performance.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Green)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Efficiency: Active</b><br>
            Fuel Saved: <b>{energy_saved}%</b> via AI Precise Throttle Control.
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction (Dark Blue)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Arriving at {stations[curr_idx+1]} in {random.randint(10, 40)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
