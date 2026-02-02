import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# High Contrast Dark Mode CSS
st.markdown("""
    <style>
    /* Dark Theme for the entire App */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Vertical Track UI - High Visibility */
    .station-node { border-left: 3px solid #58a6ff; margin-left: 45px; padding: 25px; position: relative; }
    .station-name { font-weight: bold; font-size: 20px; color: #f0f6fc; }
    .train-icon { font-size: 35px; position: absolute; left: -24px; top: 15px; z-index: 10; }
    .live-text { color: #ff7b72; font-weight: bold; font-size: 15px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Neon Style Notification Panels */
    .status-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid; box-shadow: 0px 0px 15px rgba(0,0,0,0.5); }
    
    .weather-panel { background-color: #0d1117; border-color: #58a6ff; color: #58a6ff; } /* Neon Blue */
    .health-panel { background-color: #0d1117; border-color: #d29922; color: #d29922; }  /* Neon Orange */
    .energy-panel { background-color: #0d1117; border-color: #3fb950; color: #3fb950; }  /* Neon Green */
    .pis-panel { background-color: #161b22; border-color: #bc8cff; color: #bc8cff; }     /* Neon Purple */
    
    /* High Visibility Button */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        background-color: #238636; 
        color: white; 
        font-weight: bold; 
        border: none; 
        height: 50px;
        box-shadow: 0px 4px 15px rgba(35, 134, 54, 0.3);
    }
    
    /* Methodology Box */
    .sidebar-info-box {
        background-color: #21262d;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("### 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train ID / No", value="12673")
    st.markdown("---")
    st.markdown("### 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.markdown("""<div class="sidebar-info-box"><b>System Status:</b> Moving Block Signaling Active</div>""", unsafe_allow_html=True)

# 3. MAIN DASHBOARD
st.title("🚅 AI-Powered Precise Train Control (Dark Pro)")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    # Simulated Analytics
    weather_list = [("Dense Fog 🌫️", 35.5), ("Heavy Rain 🌧️", 24.8), ("Clear Night 🌙", 12.5)]
    weather, gap = random.choice(weather_list)
    energy = random.randint(15, 25)
    
    with st.spinner("Establishing Secure Satellite Link..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Real-Time GPS Tracking")
        stations = ["Chennai", "Arakkonam", "Katpadi", "Jolarpettai"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_here = (s == stations[curr_idx])
            icon = "🚅" if is_here else ""
            line_color = "#58a6ff" if stations.index(s) <= curr_idx else "#30363d"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {"<div class='live-text'>● LIVE NOW</div>" if is_here else "<div style='color:#8b949e;'>Scheduled</div>"}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=450)

    with col_data:
        st.subheader("📢 AI Precision Dispatch Orders")
        
        # 1. Weather Integration (Neon Blue)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Response: Optimized Safety Gap to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance (Neon Orange)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Diagnostics: Vibration levels within AI safety limits.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Neon Green)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Efficiency: Active</b><br>
            Fuel Saved: <b>{energy}%</b> via AI Precise Throttle.
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction (Neon Purple)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Arriving at {stations[curr_idx+1]} in {random.randint(10, 40)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
