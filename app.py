import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Control System", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stAlert { border-radius: 10px; border-left: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚉 AI-Powered Precise Train Traffic Control & Notifications")
st.markdown("### Innovation: Dynamic Signal Management for Maximum Throughput")

# 2. LIVE TRAIN DATABASE (Requirement 3: Accurate Details)
train_db = {
    "12673": {"name": "Cheran Superfast Exp", "speed": 85, "front": 12.5, "back": 8.0, "status": "On-Time"},
    "12007": {"name": "Shatabdi Exp", "speed": 110, "front": 25.0, "back": 15.2, "status": "Early"},
    "22639": {"name": "Alleppey Exp", "speed": 75, "front": 10.1, "back": 12.4, "status": "Delayed"}
}

# 3. STATION DATA (Requirement 2: Station to Station)
route_stations = [
    {"name": "Chennai Central", "lat": 13.0827, "lon": 80.2707},
    {"name": "Katpadi Jn", "lat": 12.9681, "lon": 79.1384},
    {"name": "Salem Jn", "lat": 11.6643, "lon": 78.1460},
    {"name": "Coimbatore Jn", "lat": 11.0168, "lon": 76.9558}
]

# SIDEBAR: Control Panel
st.sidebar.header("🚆 Train Dispatch Center")
t_no = st.sidebar.selectbox("Select Active Train ID", list(train_db.keys()))
current_train = train_db[t_no]

st.sidebar.write(f"**Selected:** {current_train['name']}")
st.sidebar.write(f"**Current Status:** {current_train['status']}")

# UI LAYOUT
col_map, col_notif = st.columns([2, 1])

with col_notif:
    st.subheader("🔔 Real-Time Notifications")
    notif_pilot = st.empty()
    notif_sm = st.empty()
    notif_dept = st.empty()

# 4. SIMULATION EXECUTION (Requirement 2)
if st.button("▶️ Launch AI Precise Simulation"):
    for i in range(len(route_stations) - 1):
        start, end = route_stations[i], route_stations[i+1]
        
        # Simulating smooth movement between stations
        for p in range(0, 101, 10):
            # Calculate live coordinate
            lat = start['lat'] + (end['lat'] - start['lat']) * (p/100)
            lon = start['lon'] + (end['lon'] - start['lon']) * (p/100)
            
            with col_map:
                # Map Visualization
                m = folium.Map(location=[12.0, 78.5], zoom_start=7)
                for s in route_stations:
                    folium.Marker([s['lat'], s['lon']], tooltip=s['name'], 
                                  icon=folium.Icon(color='blue', icon='university', prefix='fa')).add_to(m)
                
                # Dynamic Marker for moving train
                folium.Marker([lat, lon], tooltip=current_train['name'], 
                              icon=folium.Icon(color='green', icon='train', prefix='fa')).add_to(m)
                st_folium(m, height=450, width=750, key=f"sim_{i}_{p}")

            # 5. NOTIFICATION LOGIC (Requirement 1)
            rec_speed = current_train['speed'] + 7
            
            notif_pilot.warning(f"""
            🧑‍✈️ **TO: Loco Pilot ({current_train['name']})**
            Action: Maintain **{rec_speed} km/h**.  
            Front: {current_train['front']}km | Back: {current_train['back']}km.  
            **Message:** Signal is CLEAR via AI Headway. Do not halt.
            """)
            
            notif_sm.info(f"""
            🚉 **TO: Station Master ({end['name']})**
            Train {t_no} approaching.  
            Arrival predicted in 10 mins. Platform optimization active.
            """)
            
            notif_dept.success(f"""
            🏢 **TO: Railway Dept**
            Throughput maximized. Ghost space reduced by 35%.  
            Current Capacity usage: 92%.
            """)
            
            time.sleep(0.5)
            
    st.balloons()
    st.success(f"Train {t_no} successfully completed section transit with optimized throughput.")
