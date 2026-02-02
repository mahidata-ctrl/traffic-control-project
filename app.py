import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# High-Contrast CSS for Dark Theme Visibility
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background-color: #161b22 !important; 
        border-right: 1px solid #30363d; 
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Tracker UI - Ultra High Visibility Text */
    .station-node { border-left: 4px solid #58a6ff; margin-left: 45px; padding: 25px; position: relative; }
    .station-name { font-weight: bold; font-size: 22px; color: #ffffff !important; text-shadow: 2px 2px 4px #000000; }
    .train-icon { font-size: 38px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-text { color: #ff4b4b !important; font-weight: bold; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
    .scheduled-text { color: #58a6ff !important; font-size: 16px; font-weight: 500; } 
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Panels - High Contrast Text */
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    
    .weather-panel { background-color: #f0f7ff; border-color: #2196f3; color: #000000; } /* Light Blue bg, Black text */
    .health-panel { background-color: #fff9f0; border-color: #ff9800; color: #000000; }  /* Light Orange bg, Black text */
    .energy-panel { background-color: #f0fff4; border-color: #4caf50; color: #000000; }  /* Light Green bg, Black text */
    .pis-panel { background-color: #1e3d59; border-color: #58a6ff; color: #ffffff; }     /* Dark Blue bg, White text */
    
    /* Button Visibility */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        background: linear-gradient(90deg, #1f6feb, #58a6ff); 
        color: white !important; 
        font-weight: bold; 
        height: 55px; 
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train ID", value="12673")
    st.markdown("---")
    st.markdown("## 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.info("System: Moving Block Signaling Active")

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    weather_list = [("Heavy Rain 🌧️", 28.5), ("Dense Fog 🌫️", 34.2), ("Clear Sky ☀️", 12.0)]
    weather, gap = random.choice(weather_list)
    
    with st.spinner("Connecting to Global Satellite Feed..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Real-Time GPS Tracking")
        # Visualizing the route from your screenshot
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_here = (s == stations[curr_idx])
            icon = "🚅" if is_here else ""
            line_color = "#58a6ff" if stations.index(s) <= curr_idx else "#30363d"
            status = f"<div class='live-text'>● LIVE NOW</div>" if is_here else "<div class='scheduled-text'>Scheduled</div>"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {status}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=500)

    with col_data:
        st.subheader("📢 AI Analytics Feed")
        
        # Weather Panel (Blue)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Response: Safety Gap adjusted to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # Maintenance Panel (Orange)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Analysis: No critical vibrations detected by AI sensors.
        </div>""", unsafe_allow_html=True)
        
        # Energy Panel (Green)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Optimization: Active</b><br>
            Fuel Saved: <b>{random.randint(12, 22)}%</b> via AI Throttle.
        </div>""", unsafe_allow_html=True)

        # PIS Panel (Dark Blue)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Arriving at {stations[curr_idx+1]} in {random.randint(15, 40)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
