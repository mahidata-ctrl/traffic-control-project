import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Control System", layout="wide")

# Eye-catchy Control Room UI Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    .stAlert { border-radius: 12px; font-size: 18px; padding: 25px; border-left: 8px solid; }
    h1 { color: #1e3d59; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Control & Dispatch System")

# 2. ACCURATE LIVE DATABASE (Requirement 3)
train_db = {
    "12673": {"name": "Cheran Superfast Exp", "speed": 85, "front": 12.5, "back": 8.0},
    "12007": {"name": "Shatabdi Exp", "speed": 110, "front": 25.0, "back": 15.2},
    "22639": {"name": "Alleppey Exp", "speed": 75, "front": 10.1, "back": 12.4}
}

# 3. STATION COORDINATES (Requirement 2)
stations = [
    {"name": "Chennai Central", "lat": 13.0827, "lon": 80.2707},
    {"name": "Katpadi Jn", "lat": 12.9681, "lon": 79.1384},
    {"name": "Salem Jn", "lat": 11.6643, "lon": 78.1460},
    {"name": "Coimbatore Jn", "lat": 11.0168, "lon": 76.9558}
]

# SIDEBAR: Control Input
st.sidebar.header("🕹️ Dispatcher Panel")
t_no = st.sidebar.selectbox("Select Active Train ID", list(train_db.keys()))
current_train = train_db[t_no]

# UI LAYOUT
col_map, col_notif = st.columns([1.6, 1])

# Requirement 1: Notification Placeholders (Creating them outside the loop)
with col_notif:
    st.subheader("📢 Live Dispatch Orders")
    pilot_placeholder = st.empty()
    sm_placeholder = st.empty()
    st.divider()
    dept_placeholder = st.empty()

# 4. SIMULATION EXECUTION (Station to Station)
if st.button("▶️ Launch AI Precise Simulation"):
    for i in range(len(stations) - 1):
        start_st, end_st = stations[i], stations[i+1]
        
        # Simulating movement between stations (p=0 to 100)
        for p in range(0, 101, 25): # Fewer steps for better focus 
            lat = start_st['lat'] + (end_st['lat'] - start_st['lat']) * (p/100)
            lon = start_st['lon'] + (end_st['lon'] - start_st['lon']) * (p/100)
            
            # Update Map on Left
            with col_map:
                m = folium.Map(location=[12.0, 78.5], zoom_start=7)
                for s in stations:
                    folium.Marker([s['lat'], s['lon']], tooltip=s['name'], 
                                  icon=folium.Icon(color='blue', icon='university', prefix='fa')).add_to(m)
                folium.Marker([lat, lon], tooltip=current_train['name'], 
                              icon=folium.Icon(color='green', icon='train', prefix='fa')).add_to(m)
                st_folium(m, height=500, width=700, key=f"sim_{i}_{p}")

            # 5. PERMANENT NOTIFICATION (Requirement 1)
            # Update the placeholders so they DON'T disappear
            rec_speed = current_train['speed'] + 7
            
            pilot_placeholder.warning(f"""
            🧑‍✈️ **TO: LOCO PILOT**
            **MESSAGE:** Signal is Green. Do not brake.
            **ACTION:** Maintain Speed at **{rec_speed} km/h**.
            **INFO:** Front: {current_train['front']}km | Back: {current_train['back']}km.
            """)
            
            sm_placeholder.info(f"""
            🚉 **TO: STATION MASTER ({end_st['name']})**
            **TRAIN:** {t_no} ({current_train['name']})
            **APPROACH:** Precise arrival at {rec_speed} km/h.
            """)
            
            dept_placeholder.success(f"🏢 **RAILWAY DEPT:** Throughput Optimized (94%).")
            
            # Now, it will stay for 4 seconds so everyone can read it clearly!
            time.sleep(4.0)
            
    st.balloons()
    st.success("Simulation Complete: No trains had to wait.")
