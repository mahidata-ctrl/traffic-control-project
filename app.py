import streamlit as st
import time

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Railway Dispatch", layout="wide")

# CSS to mimic "Where is my Train" UI
st.markdown("""
    <style>
    .station-node { border-left: 5px solid #1e3d59; margin-left: 50px; padding: 20px; position: relative; }
    .station-name { font-weight: bold; font-size: 18px; color: #1e3d59; }
    .train-icon { font-size: 30px; position: absolute; left: -22px; transition: 2s; }
    .notif-card { background-color: #fdf2e9; border-left: 8px solid #e67e22; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
    .pilot-title { color: #d35400; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Tracking System")

# 2. LIVE DATABASE (Requirement 3)
train_db = {
    "12673": {"name": "Cheran Superfast Exp", "speed": 85, "front": 12.5, "back": 8.0, "status": "On-Time"},
    "12007": {"name": "Shatabdi Exp", "speed": 110, "front": 25.0, "back": 15.2, "status": "Early"}
}

stations = [
    {"name": "Chennai Central", "time": "06:10 AM"},
    {"name": "Katpadi Jn", "time": "08:15 AM"},
    {"name": "Salem Jn", "time": "10:45 AM"},
    {"name": "Coimbatore Jn", "time": "01:20 PM"}
]

# SIDEBAR
st.sidebar.header("🕹️ Dispatch Control")
t_no = st.sidebar.selectbox("Select Active Train ID", list(train_db.keys()))
current_train = train_db[t_no]

# 3. LAYOUT
col_track, col_notif = st.columns([1, 1.2])

with col_track:
    st.subheader("📍 Live Route Progress")
    track_placeholder = st.empty()

with col_notif:
    st.subheader("📢 Real-Time Pilot & Station Orders")
    # This keeps notifications visible (Requirement 1)
    notif_placeholder = st.empty()

# 4. SIMULATION EXECUTION (Requirement 2)
if st.button("▶️ Launch AI Precision Simulation"):
    # AI Logic for Speed Optimization
    rec_speed = current_train['speed'] + 7
    
    for i in range(len(stations)):
        # Generate the Vertical Track UI
        track_html = "<div>"
        for idx, s in enumerate(stations):
            # If train is at this station
            icon = "🚅" if idx == i else ""
            track_html += f"""
            <div class="station-node">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s['name']}</div>
                <div style="color: gray;">Scheduled: {s['time']}</div>
            </div>
            """
        track_html += "</div>"
        
        # Update Track View (No Flashing)
        track_placeholder.markdown(track_html, unsafe_allow_html=True)
        
        # Update Permanent Notification (Requirement 1)
        notif_html = f"""
        <div class="notif-card">
            <p class="pilot-title">🧑‍✈️ LOCO PILOT ALERT: {current_train['name']}</p>
            <p style="font-size: 18px;"><b>STATUS:</b> SIGNAL CLEAR. DO NOT STOP.</p>
            <p style="font-size: 18px;"><b>AI RECOMMENDED SPEED:</b> <span style="color:green;">{rec_speed} km/h</span></p>
            <p><b>DISTANCE:</b> Front Train: {current_train['front']}km | Back Train: {current_train['back']}km</p>
            <hr>
            <p style="color: #2980b9;"><b>🚉 STATION MASTER ({stations[i]['name']}):</b> All clear for high-speed transit.</p>
        </div>
        """
        notif_placeholder.markdown(notif_html, unsafe_allow_html=True)
        
        # 4 Seconds so people can actually read it
        time.sleep(4.0)
        
    st.balloons()
    st.success("Throughput Optimized: Section Transit Completed.")
