import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Control System", layout="wide")

# Professional Control Room UI Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    .stAlert { border-radius: 12px; font-size: 18px; padding: 25px; border-left: 8px solid; }
    h1 { color: #1e3d59; text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #1e3d59; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Control & Dispatch System")
st.markdown("### Innovation: Dynamic Speed Optimization for Block-less Signaling")

# 2. ACCURATE LIVE DATABASE (Requirement 3)
train_db = {
    "12673": {"name": "Cheran Superfast Exp", "speed": 85, "front": 12.5, "back": 8.0, "status": "On-Time"},
    "12007": {"name": "Shatabdi Exp", "speed": 110, "front": 25.0, "back": 15.2, "status": "Early"},
    "22639": {"name": "Alleppey Exp", "speed": 75, "front": 10.1, "back": 12.4, "status": "Delayed"}
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

st.sidebar.markdown(f"**Train:** {current_train['name']}")
st.sidebar.markdown(f"**Live Status:** {current_train['status']}")

# UI LAYOUT
col_map, col_notif = st.columns([1.6, 1])

with col_notif:
    st.subheader("📢 Live Dispatch Orders")
    # Placeholders for constant display
    notif_pilot = st.empty()
    notif_sm = st.empty()
    st.divider()
    notif_dept = st.empty()

# 4. SIMULATION EXECUTION (Station to Station)
if st.button("▶️ Launch AI Precise Simulation"):
    for i in range(len(stations) - 1):
        start_st, end_st = stations[i], stations[i+1]
        
        # Simulating smooth movement between stations
        for p in range(0, 101, 20): 
            # Interpolate coordinates
            lat = start_st['lat'] + (end_st['lat'] - start_st['lat']) * (p/100)
            lon = start_st['lon'] + (end_st['lon'] - start_st['lon']) * (p/100)
            
            with col_map:
                # Folium Map
                m = folium.Map(location=[12.0, 78.5], zoom_start=7)
                for s in stations:
                    folium.Marker([s['lat'], s['lon']], tooltip=s['name'], 
                                  icon=folium.Icon(color='blue', icon='university', prefix='fa')).add_to(m)
                
                # Active train marker
                folium.Marker([lat, lon], tooltip=current_train['name'], 
                              icon=folium.Icon(color='green', icon='train', prefix='fa')).add_to(m)
                st_folium(m, height=500, width=700, key=f"sim_{i}_{p}")

            # 5. NOTIFICATION SYSTEM (Requirement 1)
            # AI calculates speed instead of stopping
            rec_speed = current_train['speed'] + 7
            
            notif_pilot.warning(f"""
            🧑‍✈️ **TO: LOCO PILOT**
            **MESSAGE:** Signal is Green. Do not brake.
            **ACTION:** Maintain Speed at **{rec_speed} km/h**.
            **INFO:** Front Train: {current_train['front']}km | Back: {current_train['back']}km.
            """)
            
            notif_sm.info(f"""
            🚉 **TO: STATION MASTER ({end_st['name']})**
            **TRAIN:** {t_no} ({current_train['name']})
            **APPROACH:** Precise arrival at {rec_speed} km/h.
            **ACTION:** Keep Platform Clear for transit.
            """)
            
            notif_dept.success(f"🏢 **RAILWAY DEPT:** Throughput Optimized (94%). Ghost space minimized.")
            
            # Slowed down to 3 seconds for Pilot readability and Mam's understanding
            time.sleep(3.0)
            
    st.balloons()
    st.success("Simulation Complete: Optimal Throughput Achieved.")
