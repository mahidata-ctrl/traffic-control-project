import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Precision System", layout="wide")

# CSS for "Where is my Train" Style & Blinking Effects
st.markdown("""
    <style>
    .station-node { border-left: 6px solid #1e3d59; margin-left: 35px; padding: 20px; position: relative; }
    .station-name { font-weight: bold; font-size: 20px; color: #1e3d59; }
    .train-icon { font-size: 35px; position: absolute; left: -25px; top: 15px; z-index: 10; }
    .live-dot { height: 12px; width: 12px; background-color: #ff0000; border-radius: 50%; display: inline-block; margin-right: 8px; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .notif-panel { background-color: #fdf2e9; border-radius: 12px; border-left: 10px solid #e67e22; padding: 25px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Control (Free Real-Time Mode)")

# 2. DATABASE & DATA FETCHING LOGIC (Free Simulation)
stations = ["Chennai Central", "Katpadi Jn", "Salem Jn", "Coimbatore Jn"]

def get_simulated_live_data(train_no):
    # This simulates fetching real-time speed and location without a paid API
    base_speed = 85 if train_no == "12673" else 105
    live_speed = base_speed + random.randint(-8, 12) # Simulating fluctuations
    # Randomly picking a station as "Current Location" for demo
    current_loc = stations[random.randint(0, 2)]
    return live_speed, current_loc

# 3. SIDEBAR: Control Panel
st.sidebar.header("📡 Live Satellite Feed")
t_no = st.sidebar.selectbox("Select Active Train ID", ["12673 (Cheran Exp)", "12007 (Shatabdi Exp)"])
train_id = t_no.split(" ")[0]

# 4. MAIN INTERFACE
col_track, col_notif = st.columns([1, 1.3])

# Initial Placeholders
with col_track:
    st.subheader("📍 Real-Time Route Progress")
    track_placeholder = st.empty()

with col_notif:
    st.subheader("📢 AI Pilot Notifications")
    notif_placeholder = st.empty()

# 5. EXECUTION: When Button is Clicked
if st.button("▶️ Sync Live GPS & Launch AI Control"):
    # Simulated API Call
    with st.spinner("Connecting to Railway GPS Server..."):
        time.sleep(1.5)
        live_speed, live_st = get_simulated_live_data(train_id)

    # Generate Tracker UI
    track_html = "<div>"
    for s in stations:
        is_here = (s == live_st)
        icon = "🚅" if is_here else ""
        color = "#1e3d59" if stations.index(s) <= stations.index(live_st) else "#bdc3c7"
        status = f"<div style='color:#e67e22; font-weight:bold;'><span class='live-dot'></span>LIVE NOW</div>" if is_here else "<div style='color:gray;'>Scheduled</div>"
        
        track_html += f"""
        <div class="station-node" style="border-left-color: {color};">
            <span class="train-icon">{icon}</span>
            <div class="station-name">{s}</div>
            {status}
        </div>
        """
    track_html += "</div>"
    
    with track_placeholder:
        components.html(track_html, height=600)

    # AI Speed Logic (Innovation for Throughput)
    rec_speed = live_speed + 6 # AI suggests slight increase to fill 'Ghost Space'
    gap = random.uniform(8.5, 15.0) # Precise headway distance
    
    with notif_placeholder:
        st.markdown(f"""
        <div class="notif-panel">
            <h3 style="color: #d35400; margin-top:0;">🧑‍✈️ LOCO PILOT ALERT</h3>
            <p style="font-size: 18px;"><b>LIVE SPEED:</b> {live_speed} km/h</p>
            <p style="font-size: 22px; color: green;"><b>AI RECOMMENDED: {rec_speed} km/h</b></p>
            <p style="font-size: 18px;"><b>PRECISE GAP:</b> {gap:.2f} km from Front Train.</p>
            <hr style="border: 0.5px solid #e67e22;">
            <p style="font-size: 16px; color: #2980b9;"><b>STATION MASTER:</b> Line clear for optimized transit.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.balloons()
    st.success(f"AI Optimization Complete: Section Throughput improved by {random.randint(12, 18)}%.")

st.divider()
st.caption("Final Year Project: B.Tech AI & Data Science | Mahitha")
