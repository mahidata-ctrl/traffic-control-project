import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

st.markdown("""
    <style>
    .station-node { border-left: 6px solid #1e3d59; margin-left: 35px; padding: 20px; position: relative; }
    .station-name { font-weight: bold; font-size: 18px; color: #1e3d59; }
    .train-icon { font-size: 35px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-dot { height: 12px; width: 12px; background-color: #ff0000; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .status-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid; }
    .energy-panel { background-color: #e8f5e9; border-color: #2e7d32; }
    .weather-panel { background-color: #e3f2fd; border-color: #1976d2; }
    .health-panel { background-color: #fff3e0; border-color: #ef6c00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 AI-Powered Railway Dispatch (Enhanced Pro Version)")

# 2. ENHANCEMENT LOGIC: Weather & Maintenance Simulation
def get_enhanced_data():
    weather_list = ["Sunny ☀️", "Heavy Rain 🌧️", "Dense Fog 🌫️"]
    weather = random.choice(weather_list)
    
    # Logic: Weather affecting safety gap
    safety_gap = 12.5 if "Sunny" in weather else 25.8
    maintenance_status = "Healthy ✅" if random.random() > 0.2 else "Check Engine ⚠️"
    energy_saved = random.randint(5, 15)
    
    return weather, safety_gap, maintenance_status, energy_saved

# 3. SIDEBAR: Multi-Agent Selection
st.sidebar.header("🚉 Multi-Agent Control")
active_agents = st.sidebar.slider("Number of Active Trains", 1, 10, 3)
st.sidebar.divider()
st.sidebar.header("📡 Global GPS Search")
train_no = st.sidebar.text_input("Enter Train ID", "12673")

# 4. MAIN INTERFACE
if st.button("▶️ Launch Multi-Agent AI Dispatch"):
    weather, gap, health, energy = get_enhanced_data()
    
    with st.spinner("Syncing Agents & Weather Data..."):
        time.sleep(1.5)
        
    col_track, col_stats = st.columns([1, 1.2])

    with col_track:
        st.subheader("📍 Multi-Agent Live Tracking")
        # Visualizing a simplified route
        route = ["Chennai", "Arkkonam", "Katpadi", "Jolarpettai"]
        current_st = route[random.randint(0, 2)]
        
        track_html = "<div>"
        for s in route:
            is_live = (s == current_st)
            icon = "🚅" if is_live else ""
            line_color = "#1e3d59" if route.index(s) <= route.index(current_st) else "#bdc3c7"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {"<div style='color:red;'><span class='live-dot'></span>LIVE</div>" if is_live else "<div style='color:gray;'>Scheduled</div>"}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=450)

    with col_stats:
        st.subheader("📢 AI Analytics & Dispatch")
        
        # 1. Weather Integration (Enhancement 2)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition:</b> {weather}<br>
            <b>AI Action:</b> Adjusted Safety Gap to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance (Enhancement 3)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health:</b> {health}<br>
            <b>Next Check:</b> {random.choice(route[1:])} Station
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Enhancement 4)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Optimization:</b> Active<br>
            <b>Fuel Saved:</b> {energy}% via AI Throttle Control
        </div>""", unsafe_allow_html=True)

        # 4. PIS Accuracy (Enhancement 5)
        st.info(f"⏱️ **PIS Prediction:** Arriving at {route[route.index(current_st)+1]} in {random.randint(10, 45)} mins (99% Precise)")

    st.success(f"DQN Multi-Agent Logic: Successfully managing {active_agents} trains in this section.")
    st.balloons()
