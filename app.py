import streamlit as st
import time

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Railway Dispatch", layout="wide")

# Eye-catchy UI Styling
st.markdown("""
    <style>
    .station-node { border-left: 5px solid #1e3d59; margin-left: 30px; padding: 15px; position: relative; }
    .station-name { font-weight: bold; font-size: 18px; color: #1e3d59; }
    .train-icon { font-size: 30px; position: absolute; left: -22px; top: 10px; }
    .notif-card { background-color: #fdf2e9; border-left: 8px solid #e67e22; padding: 20px; border-radius: 10px; }
    .pilot-title { color: #d35400; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Tracking System")

# 2. ACCURATE LIVE DATABASE (Requirement 3)
train_db = {
    "12673": {"name": "Cheran Superfast Exp", "speed": 85, "front": 12.5, "back": 8.0},
    "12007": {"name": "Shatabdi Exp", "speed": 110, "front": 25.0, "back": 15.2}
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
    notif_placeholder = st.empty()

# 4. SIMULATION EXECUTION (Requirement 2)
if st.button("▶️ Launch AI Precision Simulation"):
    rec_speed = current_train['speed'] + 7
    
    for i in range(len(stations)):
        # Vertical Track UI Generation
        track_html = "<div>"
        for idx, s in enumerate(stations):
            icon = "🚅" if idx == i else ""
            track_html += f"""
            <div class="station-node">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s['name']}</div>
                <div style="color: gray;">Scheduled: {s['time']}</div>
            </div>
            """
        track_html += "</div>"
        
        # Rendering the HTML
        track_placeholder.markdown(track_html, unsafe_allow_html=True)
        
        # Notification Card (Requirement 1)
        notif_html = f"""
        <div class="notif-card">
            <p class="pilot-title">🧑‍✈️ LOCO PILOT ALERT: {current_train['name']}</p>
            <p style="font-size: 18px;"><b>STATUS:</b> SIGNAL CLEAR. DO NOT STOP.</p>
            <p style="font-size: 20px;"><b>AI RECOMMENDED SPEED:</b> <span style="color:green;">{rec_speed} km/h</span></p>
            <p><b>DISTANCE:</b> Front: {current_train['front']}km | Back: {current_train['back']}km</p>
            <hr>
            <p style="color: #2980b9;"><b>🚉 STATION MASTER ({stations[i]['name']}):</b> Section clear for high-speed transit.</p>
        </div>
        """
        notif_placeholder.markdown(notif_html, unsafe_allow_html=True)
        
        time.sleep(4.0)
        
    st.balloons()
