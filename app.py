import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# Modern Colorful CSS Styling
st.markdown("""
    <style>
    /* Main Background & Sidebar */
    .stApp { background-color: #f8f9fa; }
    section[data-testid="stSidebar"] { background-color: #1e2a38 !important; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label { color: white !important; }
    
    /* Vertical Track UI */
    .station-node { border-left: 5px solid #3498db; margin-left: 45px; padding: 30px; position: relative; }
    .station-name { font-weight: bold; font-size: 20px; color: #2c3e50; }
    .train-icon { font-size: 40px; position: absolute; left: -28px; top: 15px; z-index: 10; }
    .live-dot { height: 14px; width: 14px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }

    /* Enhanced Multi-Color Notification Panels */
    .status-box { padding: 22px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .weather-panel { background-color: #e3f2fd; border-color: #2196f3; color: #0d47a1; } /* Blue */
    .health-panel { background-color: #fff3e0; border-color: #ff9800; color: #e65100; }  /* Orange */
    .energy-panel { background-color: #e8f5e9; border-color: #4caf50; color: #1b5e20; }  /* Green */
    .pis-panel { background-color: #f3e5f5; border-color: #9c27b0; color: #4a148c; }     /* Purple */
    
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2980b9; color: white; font-weight: bold; border: none; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AI-Powered Railway Dispatch (Pro Enhancement)")
st.markdown("---")

# 2. ENHANCEMENT SIMULATION LOGIC
def get_pro_analytics():
    weather_data = [
        ("Clear Sky ☀️", 12.5, "Standard Buffer"),
        ("Heavy Rain 🌧️", 24.2, "Safety Gap Increased"),
        ("Dense Fog 🌫️", 35.8, "Emergency Safety Protocol")
    ]
    w_choice = random.choice(weather_data)
    health_status = "Healthy ✅" if random.random() > 0.15 else "Service Required 🛠️"
    fuel_save = random.randint(10, 25)
    return w_choice, health_status, fuel_save

# 3. SIDEBAR: Multi-Agent & Global Search
with st.sidebar:
    st.markdown("# 📊 Multi-Agent Control")
    agents = st.slider("Number of Active Train Agents", 1, 20, 5)
    st.markdown("---")
    st.markdown("# 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train ID / No", value="12677")
    st.info("System: DQN-MARL Optimization Enabled")

# 4. MAIN DASHBOARD
if st.button("🚀 Launch AI Multi-Agent Dispatch"):
    (weather, gap, action), health, energy = get_pro_analytics()
    
    with st.spinner("Processing Global Network Data..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Multi-Agent Live Tracking")
        # Route Logic
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn", "Salem Jn"]
        curr_idx = random.randint(0, 3)
        current_loc = stations[curr_idx]
        next_loc = stations[curr_idx + 1]
        
        track_html = "<div>"
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
        st.subheader("📢 AI Analytics & Dispatch Orders")
        
        # 1. Weather Integration
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            <b>AI Response:</b> {action} (Gap: {gap} km)
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health Status: {health}</b><br>
            <b>Diagnostic:</b> Vibration and Temp within AI-defined limits.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Efficiency
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Optimization: Active</b><br>
            <b>Fuel Saved: {energy}%</b> via AI Precise Throttle Control.
        </div>""", unsafe_allow_html=True)

        # 4. PIS Integration
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Estimated Arrival at <b>{next_loc}</b> in {random.randint(12, 35)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
    st.success(f"System: Successfully managing {agents} trains using Multi-Agent Reinforcement Learning.")

st.divider()
st.caption("B.Tech Artificial Intelligence & Data Science | Project by Mahitha")
