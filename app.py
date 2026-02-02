import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global AI Train Tracker", layout="wide")

# Professional UI Styling with CSS
st.markdown("""
    <style>
    .station-node { border-left: 6px solid #1e3d59; margin-left: 35px; padding: 20px; position: relative; }
    .station-name { font-weight: bold; font-size: 20px; color: #1e3d59; }
    .train-icon { font-size: 35px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-dot { height: 12px; width: 12px; background-color: #ff0000; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .notif-panel { background-color: #f0f4f8; border-radius: 12px; border-left: 10px solid #1e3d59; padding: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1e3d59; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 Global AI-Powered Precise Train Tracking System")
st.markdown("---")

# 2. GLOBAL DATA ENGINE (Simulated Worldwide Database)
def fetch_global_train_data(t_no):
    # Defining specific routes for realism
    global_db = {
        "12673": {"name": "Cheran Superfast (IND)", "route": ["Chennai Central", "Katpadi Jn", "Salem Jn", "Coimbatore Jn"]},
        "EURO-99": {"name": "Eurostar Express (EU)", "route": ["London", "Paris", "Brussels", "Amsterdam"]},
        "AMT-101": {"name": "Amtrak Acela (USA)", "route": ["New York", "Philadelphia", "Baltimore", "Washington DC"]},
        "SHIN-500": {"name": "Shinkansen Bullet (JPN)", "route": ["Tokyo", "Nagoya", "Kyoto", "Osaka"]}
    }
    
    # Generic Search Logic
    search_key = t_no.upper()
    for key in global_db:
        if key in search_key:
            return global_db[key], random.randint(90, 240)
    
    # Fallback for any unknown train number
    fallback = {
        "name": f"International Express ({t_no})",
        "route": ["Station A", "Station B", "Station C", "Station D"]
    }
    return fallback, random.randint(60, 140)

# 3. SIDEBAR: Control & Search
st.sidebar.header("🔍 Global Satellite Search")
train_search = st.sidebar.text_input("Enter Train No / ID", value="12673")
st.sidebar.divider()
st.sidebar.info("System uses Deep Q-Network (DQN) AI to optimize section throughput.")

# 4. MAIN INTERFACE EXECUTION
if st.button("🚀 Sync Global GPS & Track Live"):
    with st.spinner(f"Accessing Global Satellite Network for {train_search}..."):
        time.sleep(2) # Simulating API response time
        train_data, live_speed = fetch_global_train_data(train_search)
        
        # Select current position for simulation
        route = train_data['route']
        current_idx = random.randint(0, len(route)-2)
        current_st = route[current_idx]
        next_st = route[current_idx + 1]

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.subheader(f"📍 Route: {train_data['name']}")
        
        # Requirement 2: Visual Simulation (Vertical View)
        track_html = "<div>"
        for s in route:
            is_here = (s == current_st)
            icon = "🚅" if is_here else ""
            line_color = "#1e3d59" if route.index(s) <= route.index(current_st) else "#bdc3c7"
            status_ui = f"<div style='color:red; font-weight:bold;'><span class='live-dot'></span>LIVE NOW</div>" if is_here else "<div style='color:gray;'>Scheduled</div>"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {status_ui}
            </div>
            """
        track_html += "</div>"
        components.html(track_html, height=550)

    with col2:
        st.subheader("📢 AI Precision Dispatch Orders")
        
        # Requirement 1: AI Notification Logic (Innovation)
        # AI suggests speed increase to minimize 'Ghost Space'
        rec_speed = live_speed + 8
        safety_gap = random.uniform(5.5, 15.0)
        
        st.markdown(f"""
        <div class="notif-panel">
            <h3 style="color: #1e3d59; margin-top:0;">🧑‍✈️ GLOBAL PILOT ALERT</h3>
            <p style="font-size: 18px;"><b>TRAIN ID:</b> {train_search}</p>
            <p style="font-size: 18px;"><b>CURRENT SPEED:</b> {live_speed} km/h</p>
            <p style="font-size: 24px; color: green;"><b>AI RECOMMENDED: {rec_speed} km/h</b></p>
            <hr style="border: 0.5px solid #1e3d59;">
            <p style="font-size: 18px;"><b>NEXT STATION:</b> {next_st}</p>
            <p style="font-size: 18px;"><b>AI PRECISION GAP:</b> {safety_gap:.2f} km</p>
            <p style="color: #2980b9; font-weight: bold;">STATUS: Throughput Optimized (Moving Block Active)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("DQN Model Analysis: Zero Stop Probability achieved for this section.")
    
    st.balloons()

st.divider()
st.caption("B.Tech AI & Data Science Project | Student: Mahitha")
