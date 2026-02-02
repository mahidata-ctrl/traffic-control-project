import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# Exact Theme Color Matching from your Screenshots
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f8f9fa; }
    
    /* Sidebar Styling (Dark Navy/Slate) */
    section[data-testid="stSidebar"] { 
        background-color: #262730 !important; 
    }
    section[data-testid="stSidebar"] * { 
        color: #ffffff !important; 
    }
    
    /* Vertical Track UI */
    .station-node { border-left: 2px solid #555; margin-left: 45px; padding: 20px; position: relative; }
    .station-name { font-weight: bold; font-size: 18px; color: #333; }
    .train-icon { font-size: 30px; position: absolute; left: -22px; top: 10px; z-index: 10; }
    .live-text { color: red; font-weight: bold; font-size: 14px; margin-top: -5px; }

    /* Exact Card Colors from your Screenshot */
    .status-box { padding: 18px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); }
    
    /* Blue Panel - Weather */
    .weather-panel { background-color: #e3f2fd; border-color: #2196f3; color: #1e3d59; } 
    /* Orange/Cream Panel - Engine Health */
    .health-panel { background-color: #fff3e0; border-color: #ff9800; color: #5d4037; }  
    /* Green Panel - Energy Optimization */
    .energy-panel { background-color: #e8f5e9; border-color: #4caf50; color: #1b5e20; }  
    /* Dark Blue Panel - PIS Prediction */
    .pis-panel { background-color: #1e3d59; border-color: #0d47a1; color: #ffffff; }     
    
    /* Button Styling */
    .stButton>button { 
        background-color: #2980b9; 
        color: white; 
        border-radius: 8px; 
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    
    /* Sidebar Methodology Box */
    .sidebar-info-box {
        background-color: #3e4e5e;
        padding: 15px;
        border-radius: 8px;
        color: #ffffff;
        font-size: 14px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR (Matching Image 2)
with st.sidebar:
    st.markdown("### 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673")
    
    st.markdown("---")
    st.markdown("### 💡 AI Methodology")
    st.markdown("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    
    st.markdown("""
        <div class="sidebar-info-box">
            <b>System:</b> Moving Block Signaling Active
        </div>
    """, unsafe_allow_html=True)

# 3. MAIN INTERFACE
st.title("🚀 AI-Powered Precise Train Control System")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    # Simulated Analytics Data (Enhancements 2, 3, 4, 5)
    weather_list = [("Heavy Rain 🌧️", 25.8), ("Cloudy Sky ☁️", 14.5), ("Dense Fog 🌫️", 32.0)]
    weather, gap = random.choice(weather_list)
    energy_save = random.randint(12, 19)
    
    with st.spinner("Accessing Satellite Real-Time Data..."):
        time.sleep(1.5)
        
    col_left, col_right = st.columns([1, 1.4])

    with col_left:
        st.subheader("📍 Live Tracking Map")
        # Vertical Tracking Logic
        stations = ["Chennai", "Arakkonam", "Katpadi", "Jolarpettai"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_here = (s == stations[curr_idx])
            icon = "🚅" if is_here else ""
            line_color = "#2980b9" if stations.index(s) <= curr_idx else "#ccc"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {"<div class='live-text'>LIVE</div>" if is_here else "<div style='color:gray;'>Scheduled</div>"}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=450)

    with col_right:
        st.subheader("📢 AI Analytics & Dispatch")
        
        # 1. Weather Integration (Blue Card)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Action: Adjusted Safety Gap to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Engine Health / Predictive Maintenance (Orange Card)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Next Check: {stations[curr_idx+1]} Station
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Green Card)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Optimization: Active</b><br>
            Fuel Saved: <b>{energy_save}%</b> via AI Throttle Control
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction (Dark Blue Card)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 PIS Prediction: Arriving at {stations[curr_idx+1]} in {random.randint(15, 45)} mins (99% Precise)</b>
        </div>""", unsafe_allow_html=True)

    st.balloons()
    st.success("DQN Model Analysis: Section throughput optimized.")
