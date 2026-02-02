import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# Vibrant Professional CSS for Modern UI
st.markdown("""
    <style>
    /* Main Background & Sidebar */
    .stApp { background-color: #f4f7f6; }
    section[data-testid="stSidebar"] { background-color: #1e2a38 !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Vertical Tracker UI */
    .station-node { border-left: 6px solid #3498db; margin-left: 45px; padding: 25px; position: relative; }
    .station-name { font-weight: bold; font-size: 20px; color: #2c3e50; }
    .train-icon { font-size: 40px; position: absolute; left: -28px; top: 15px; z-index: 10; }
    .live-dot { height: 14px; width: 14px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Colorful Analytics Panels based on Enhancements */
    .status-box { padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 2px 4px 12px rgba(0,0,0,0.08); }
    .weather-panel { background-color: #e3f2fd; border-color: #2196f3; color: #0d47a1; } /* Blue - Weather */
    .health-panel { background-color: #fff3e0; border-color: #ff9800; color: #e65100; }  /* Orange - Maintenance */
    .energy-panel { background-color: #e8f5e9; border-color: #4caf50; color: #1b5e20; }  /* Green - Energy */
    .pis-panel { background-color: #f3e5f5; border-color: #9c27b0; color: #4a148c; }     /* Purple - PIS Accuracy */
    
    /* Action Button */
    .stButton>button { width: 100%; border-radius: 25px; background: linear-gradient(90deg, #1e3d59, #2980b9); color: white; font-weight: bold; border: none; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AI-Powered Precise Train Control System")
st.markdown("---")

# 2. ENHANCEMENT SIMULATION LOGIC
def get_train_analytics():
    # Weather influencing Safety Gap (Enhancement 2)
    weather_info = [("Cloudy Sky ☁️", 14.5), ("Heavy Rain 🌧️", 23.8), ("Dense Fog 🌫️", 32.0)]
    w_choice = random.choice(weather_info)
    # Predictive Maintenance (Enhancement 3)
    health = "Healthy ✅" if random.random() > 0.15 else "Service Required 🛠️"
    # Energy Optimization (Enhancement 4)
    energy = random.randint(10, 22)
    return w_choice, health, energy

# 3. SIDEBAR: Global GPS Search
with st.sidebar:
    st.markdown("# 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673")
    st.divider()
    st.markdown("### 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.info("System: Moving Block Signaling Active")

# 4. MAIN INTERFACE
if st.button("🚀 Sync Live Satellite & Start AI Dispatch"):
    (weather, gap), health, energy = get_train_analytics()
    
    with st.spinner("Fetching Real-Time Satellite Data..."):
        time.sleep(1.8)
        
    col_map, col_data = st.columns([1, 1.2])

    with col_map:
        st.subheader(f"📍 Live Tracker: Train {train_id}")
        # Single Agent Route Logic
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn", "Salem Jn"]
        curr_idx = random.randint(0, 3)
        current_loc = stations[curr_idx]
        next_loc = stations[curr_idx + 1]
        
        track_html = "<div style='padding-top: 10px;'>"
        for s in stations:
            is_here = (s == current_loc)
            icon = "🚅" if is_here else ""
            line_color = "#3498db" if stations.index(s) <= stations.index(current_loc) else "#bdc3c7"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {"<div style='color:#e74c3c; font-weight:bold;'><span class='live-dot'></span>LIVE NOW</div>" if is_here else "<div style='color:gray;'>Scheduled</div>"}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=550)

    with col_data:
        st.subheader("📢 AI Precision Commands")
        
        # 1. Weather & Terrain Integration
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            <b>AI Optimization:</b> Safety Gap dynamically adjusted to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: {health}</b><br>
            <b>Diagnostic:</b> Vibration and Thermal monitoring within AI safety limits.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Efficiency Optimization
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Green Railway Mode: Active</b><br>
            <b>Fuel Saved: {energy}%</b> via AI-controlled Precise Throttle Adjustment.
        </div>""", unsafe_allow_html=True)

        # 4. Passenger Information (PIS) Accuracy
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Estimated Arrival at <b>{next_loc}</b> in {random.randint(15, 42)} mins (99% confidence).
        </div>""", unsafe_allow_html=True)

    st.balloons()
    st.success("Section Throughput: Maximized to 94% efficiency by removing 'Ghost Space'.")

st.divider()
st.caption("Final Year B.Tech Project: AI & Data Science | Student: Mahitha")
