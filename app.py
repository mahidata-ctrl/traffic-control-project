import streamlit as st
import time
import streamlit.components.v1 as components

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Railway Dispatch", layout="wide")

st.title("🚉 AI-Powered Precise Train Tracking System")

# 2. LIVE DATABASE (Requirement 3)
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

# SIDEBAR: Permanent Notifications (Requirement 1)
st.sidebar.header("🕹️ Dispatch Control")
t_no = st.sidebar.selectbox("Select Active Train ID", list(train_db.keys()))
current_train = train_db[t_no]

st.sidebar.divider()
st.sidebar.subheader("🔔 Live Dispatch Orders")
pilot_placeholder = st.sidebar.empty()
sm_placeholder = st.sidebar.empty()

# 3. MAIN UI LAYOUT
track_area = st.empty()

# 4. SIMULATION EXECUTION
if st.button("▶️ Launch AI Precision Simulation"):
    rec_speed = current_train['speed'] + 7
    
    for i in range(len(stations)):
        # Generate the Vertical Track UI
        track_html = f"""
        <div style="font-family: Arial; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
        """
        for idx, s in enumerate(stations):
            icon = "🚅" if idx == i else ""
            line_color = "#1e3d59" if idx <= i else "#bdc3c7"
            track_html += f"""
            <div style="border-left: 5px solid {line_color}; margin-left: 30px; padding: 20px; position: relative;">
                <span style="font-size: 30px; position: absolute; left: -25px; top: 15px;">{icon}</span>
                <div style="font-weight: bold; font-size: 20px; color: #1e3d59;">{s['name']}</div>
                <div style="color: gray;">Scheduled: {s['time']}</div>
            </div>
            """
        track_html += "</div>"
        
        # Displaying with Components to prevent raw code/flashing
        with track_area:
            components.html(track_html, height=500)
        
        # Updating Sidebar Notifications (Requirement 1)
        pilot_placeholder.warning(f"""
        🧑‍✈️ **LOCO PILOT:** Maintain: **{rec_speed} km/h** Gap: {current_train['front']}km clear.
        """)
        
        sm_placeholder.info(f"🚉 **STATION MASTER:** {stations[i]['name']} clearance active.")
        
        # Wait 4 seconds for readability
        time.sleep(4.0)
        
    st.balloons()
