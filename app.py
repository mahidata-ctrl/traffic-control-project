import streamlit as st
import time

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Railway Dispatch", layout="wide")

# CSS for Vertical Tracking UI
st.markdown("""
    <style>
    .station-node { border-left: 5px solid #1e3d59; margin-left: 20px; padding: 10px; position: relative; }
    .station-name { font-weight: bold; font-size: 16px; color: #1e3d59; }
    .train-icon { font-size: 25px; position: absolute; left: -20px; top: 5px; }
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

# SIDEBAR: Permanent Notification Area (Requirement 1)
st.sidebar.header("🕹️ Dispatch Control")
t_no = st.sidebar.selectbox("Select Active Train ID", list(train_db.keys()))
current_train = train_db[t_no]

# Notification Placeholders in Sidebar to avoid flashing
st.sidebar.divider()
st.sidebar.subheader("🔔 Dispatch Orders")
pilot_notif = st.sidebar.empty()
sm_notif = st.sidebar.empty()

# 3. MAIN UI LAYOUT
track_placeholder = st.empty()

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
        
        # Displaying the Progress in the main area
        track_placeholder.markdown(track_html, unsafe_allow_html=True)
        
        # Permanent Sidebar Notifications
        pilot_notif.warning(f"""
        🧑‍✈️ **LOCO PILOT:** Maintain: **{rec_speed} km/h** Front Dist: {current_train['front']}km
        """)
        
        sm_notif.info(f"🚉 **STATION MASTER:** {stations[i]['name']} clear.")
        
        # 4-Second Wait so everyone can read it clearly
        time.sleep(4.0)
        
    st.sidebar.success("Simulation Completed!")
    st.balloons()
