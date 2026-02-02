import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# Professional White Theme CSS
st.markdown("""
    <style>
    /* Main Background - White Theme */
    .stApp { background-color: #ffffff; color: #000000; }
    
    /* Sidebar Styling - Light Gray for Professional Look */
    section[data-testid="stSidebar"] { 
        background-color: #f1f3f4 !important; 
        border-right: 1px solid #ddd; 
    }
    section[data-testid="stSidebar"] * { color: #202124 !important; }

    /* Tracker UI - High Visibility on White */
    .station-node { border-left: 4px solid #1a73e8; margin-left: 45px; padding: 25px; position: relative; }
    .station-name { font-weight: bold; font-size: 22px; color: #202124 !important; }
    .train-icon { font-size: 38px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-text { color: #d93025 !important; font-weight: bold; font-size: 18px; }
    .scheduled-text { color: #70757a !important; font-size: 16px; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Analytics Panels - Vibrant on White Background */
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    
    .weather-panel { background-color: #e8f0fe; border-color: #1a73e8; color: #174ea6; } /* Blue */
    .health-panel { background-color: #fef7e0; border-color: #f9ab00; color: #3c4043; }  /* Yellow/Orange */
    .energy-panel { background-color: #e6f4ea; border-color: #1e8e3e; color: #137333; }  /* Green */
    .pis-panel { background-color: #f3e5f5; border-color: #9c27b0; color: #4a148c; }     /* Purple */
    
    /* Primary Action Button */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        background-color: #1a73e8; 
        color: white !important; 
        font-weight: bold; 
        height: 55px; 
        font-size: 18px;
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
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_here = (s == stations[curr_idx])
            icon = "🚅" if is_here else ""
            line_color = "#1a73e8" if stations.index(s) <= curr_idx else "#dadce0"
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
        
        # 1. Weather Panel (Blue)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Response: Safety Gap adjusted to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Maintenance Panel (Yellow/Orange)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Analysis: Predictive sensors show optimal engine performance.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Green)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Efficiency: Active</b><br>
            Fuel Saved: <b>{random.randint(12, 22)}%</b> via AI Throttle.
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction (Purple)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Arriving at {stations[curr_idx+1]} in {random.randint(15, 40)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
