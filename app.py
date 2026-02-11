import streamlit as st
import time
import streamlit.components.v1 as components
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import requests
import json
from geopy.distance import geodesic
import pytz
from dateutil import parser

# Page Configuration
st.set_page_config(
    page_title="🚆 Indian Railways Live Tracker",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; }
    h1, h2, h3, h4, h5, h6 { color: #38bdf8 !important; font-weight: 700 !important; }
    
    .live-train-card {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .live-train-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
    }
    
    .selected-train {
        border-left: 4px solid #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .train-marker {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Indian Railways Colors
IR_COLORS = {
    'Rajdhani': '#FF0000',
    'Shatabdi': '#0000FF',
    'Duronto': '#008000',
    'Garib Rath': '#800080',
    'Jan Shatabdi': '#FFA500',
    'Superfast': '#DC143C',
    'Express': '#228B22',
    'Passenger': '#808080',
    'Special': '#FFD700'
}

# ========== REAL-TIME TRAIN DATA FUNCTIONS ==========

class IndianRailwaysAPI:
    """Mock API for Indian Railways Live Data"""
    
    # Major Indian Railway Stations Coordinates
    STATIONS = {
        'Chennai Central': (13.0827, 80.2707),
        'Mumbai Central': (18.9698, 72.8195),
        'New Delhi': (28.6423, 77.2211),
        'Howrah Junction': (22.5859, 88.3476),
        'Bangalore City': (12.9774, 77.5695),
        'Secunderabad Junction': (17.4399, 78.4983),
        'Ahmedabad Junction': (23.0258, 72.5873),
        'Patna Junction': (25.6093, 85.1238),
        'Lucknow NR': (26.8465, 80.9462),
        'Kolkata': (22.5726, 88.3639),
        'Pune Junction': (18.5204, 73.8567),
        'Jaipur Junction': (26.9124, 75.7873),
        'Nagpur Junction': (21.1458, 79.0882),
        'Bhopal Junction': (23.2599, 77.4126),
        'Visakhapatnam Junction': (17.6868, 83.2185)
    }
    
    # Popular Indian Trains
    TRAINS = [
        {
            'train_no': '12673',
            'name': 'CHERAN SF EXP',
            'type': 'Superfast',
            'source': 'Chennai Central',
            'destination': 'Coimbatore Junction',
            'current_station': 'Katpadi Junction',
            'next_station': 'Jolarpettai Junction',
            'speed': random.randint(75, 95),
            'delay': random.randint(0, 20),
            'status': 'Running',
            'last_update': datetime.now(),
            'route': ['Chennai Central', 'Arakkonam Junction', 'Katpadi Junction', 
                     'Jolarpettai Junction', 'Salem Junction', 'Coimbatore Junction']
        },
        {
            'train_no': '12007',
            'name': 'SHATABDI EXP',
            'type': 'Shatabdi',
            'source': 'Chennai Central',
            'destination': 'Bangalore City',
            'current_station': 'Bangarpet Junction',
            'next_station': 'Krishnarajapuram',
            'speed': random.randint(85, 105),
            'delay': 0,
            'status': 'Running',
            'last_update': datetime.now(),
            'route': ['Chennai Central', 'Katpadi Junction', 'Bangarpet Junction',
                     'Krishnarajapuram', 'Bangalore City']
        },
        {
            'train_no': '12431',
            'name': 'RAJDHANI EXP',
            'type': 'Rajdhani',
            'source': 'New Delhi',
            'destination': 'Howrah Junction',
            'current_station': 'Kanpur Central',
            'next_station': 'Allahabad Junction',
            'speed': random.randint(90, 110),
            'delay': random.randint(5, 15),
            'status': 'Running',
            'last_update': datetime.now(),
            'route': ['New Delhi', 'Kanpur Central', 'Allahabad Junction',
                     'Mughalsarai Junction', 'Howrah Junction']
        },
        {
            'train_no': '11013',
            'name': 'DECCAN EXPRESS',
            'type': 'Express',
            'source': 'Mumbai Central',
            'destination': 'Pune Junction',
            'current_station': 'Karjat',
            'next_station': 'Lonavala',
            'speed': random.randint(65, 85),
            'delay': random.randint(10, 30),
            'status': 'Running',
            'last_update': datetime.now(),
            'route': ['Mumbai Central', 'Dadar', 'Kalyan Junction', 'Karjat',
                     'Lonavala', 'Pune Junction']
        },
        {
            'train_no': '12601',
            'name': 'MYSORE EXP',
            'type': 'Superfast',
            'source': 'Chennai Central',
            'destination': 'Mysore Junction',
            'current_station': 'Bangalore City',
            'next_station': 'Mandya',
            'speed': random.randint(70, 90),
            'delay': random.randint(0, 10),
            'status': 'Running',
            'last_update': datetime.now(),
            'route': ['Chennai Central', 'Bangalore City', 'Mandya', 'Mysore Junction']
        }
    ]
    
    @staticmethod
    def get_live_trains(limit=20):
        """Get live train data with simulated movement"""
        trains = []
        for train in IndianRailwaysAPI.TRAINS:
            # Simulate movement by updating position
            route = train['route']
            current_idx = route.index(train['current_station'])
            
            # Move train along route with probability
            if random.random() > 0.7 and current_idx < len(route) - 1:
                train['current_station'] = route[current_idx + 1]
                train['next_station'] = route[current_idx + 2] if current_idx + 2 < len(route) else 'Terminal'
            
            # Random speed fluctuation
            speed_change = random.uniform(-5, 5)
            train['speed'] = max(10, min(110, train['speed'] + speed_change))
            
            # Random delay changes
            delay_change = random.randint(-5, 5)
            train['delay'] = max(0, train['delay'] + delay_change)
            
            # Get coordinates for current station
            current_coords = IndianRailwaysAPI.STATIONS.get(
                train['current_station'].split(' Junction')[0].split(' Central')[0],
                (random.uniform(8, 37), random.uniform(68, 97))
            )
            
            # Add some randomness to position (simulate between stations)
            lat_offset = random.uniform(-0.5, 0.5)
            lon_offset = random.uniform(-0.5, 0.5)
            current_coords = (current_coords[0] + lat_offset, current_coords[1] + lon_offset)
            
            trains.append({
                **train,
                'latitude': current_coords[0],
                'longitude': current_coords[1],
                'last_update': datetime.now(),
                'color': IR_COLORS.get(train['type'], '#3b82f6')
            })
        
        # Add more random trains
        for i in range(limit - len(trains)):
            train_no = str(random.randint(12000, 12999))
            train_type = random.choice(list(IR_COLORS.keys()))
            source = random.choice(list(IndianRailwaysAPI.STATIONS.keys()))
            destination = random.choice([s for s in IndianRailwaysAPI.STATIONS.keys() if s != source])
            
            trains.append({
                'train_no': train_no,
                'name': f'{train_type} {train_no}',
                'type': train_type,
                'source': source,
                'destination': destination,
                'current_station': random.choice(list(IndianRailwaysAPI.STATIONS.keys())),
                'next_station': random.choice(list(IndianRailwaysAPI.STATIONS.keys())),
                'speed': random.randint(40, 100),
                'delay': random.randint(0, 45),
                'status': random.choice(['Running', 'Delayed', 'On Time', 'Late']),
                'latitude': random.uniform(8, 37),
                'longitude': random.uniform(68, 97),
                'last_update': datetime.now(),
                'color': IR_COLORS.get(train_type, '#3b82f6'),
                'route': []
            })
        
        return trains
    
    @staticmethod
    def get_train_position(train_no):
        """Get specific train's current position"""
        trains = IndianRailwaysAPI.get_live_trains(limit=50)
        for train in trains:
            if train['train_no'] == train_no:
                return train
        return None

# ========== SIDEBAR ==========

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/49/Indian_Railways_Logo.svg/1200px-Indian_Railways_Logo.svg.png", width=100)
    st.title("🇮🇳 Indian Railways")
    
    st.markdown("---")
    
    # Search Train
    st.subheader("🔍 Search Train")
    search_type = st.radio("Search by:", ["Train Number", "Train Name", "Route"])
    
    if search_type == "Train Number":
        train_no = st.text_input("Enter Train Number", "12673")
        if st.button("Track Train"):
            selected_train = IndianRailwaysAPI.get_train_position(train_no)
            if selected_train:
                st.session_state.selected_train = selected_train
                st.success(f"Tracking {selected_train['name']}")
            else:
                st.error("Train not found!")
    
    elif search_type == "Train Name":
        train_name = st.selectbox(
            "Select Train",
            ["CHERAN SF EXP", "SHATABDI EXP", "RAJDHANI EXP", "DECCAN EXPRESS", "MYSORE EXP"]
        )
    
    else:
        from_station = st.selectbox("From", list(IndianRailwaysAPI.STATIONS.keys()))
        to_station = st.selectbox("To", list(IndianRailwaysAPI.STATIONS.keys()))
    
    st.markdown("---")
    
    # Filter Options
    st.subheader("🎯 Filters")
    train_types = st.multiselect(
        "Train Types",
        list(IR_COLORS.keys()),
        default=['Superfast', 'Express', 'Rajdhani']
    )
    
    speed_range = st.slider("Speed Range (km/h)", 0, 150, (40, 120))
    
    delay_filter = st.select_slider(
        "Max Delay",
        options=["On Time", "Up to 15 min", "Up to 30 min", "Up to 1 hr", "Any"]
    )
    
    st.markdown("---")
    
    # Live Stats
    st.subheader("📊 Live Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Trains", "2,850", "↗️ 12")
    with col2:
        st.metric("Avg Speed", "78 km/h", "↗️ 2.3%")
    
    st.metric("Punctuality", "82.5%", "↘️ 1.2%")
    st.metric("Delayed Trains", "317", "↘️ 8")

# ========== MAIN DASHBOARD ==========

st.title("🚆 Indian Railways Live Train Tracker")
st.markdown("Real-time tracking of trains across India with AI-powered insights")

# Initialize session state
if 'selected_train' not in st.session_state:
    st.session_state.selected_train = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# Control Panel
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
with col2:
    st.session_state.auto_refresh = st.toggle("Auto Refresh", value=True)
with col3:
    refresh_rate = st.selectbox("Update Rate", ["5 seconds", "10 seconds", "30 seconds", "1 minute"])
with col4:
    map_style = st.selectbox("Map Style", ["Satellite", "Terrain", "Street", "Dark"])

# ========== LIVE TRAIN MAP ==========

st.markdown("---")
st.subheader("📍 Live Train Positions Across India")

# Get live train data
live_trains = IndianRailwaysAPI.get_live_trains(limit=100)

# Create India map
india_map = folium.Map(
    location=[20.5937, 78.9629],
    zoom_start=5,
    tiles='CartoDB dark_matter' if map_style == "Dark" else 
          'OpenStreetMap' if map_style == "Street" else
          'Stamen Terrain' if map_style == "Terrain" else
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
)

# Add Indian states boundary (simplified)
india_bounds = [
    [6.0, 68.0],  # Southwest (Kanyakumari)
    [35.0, 97.0]   # Northeast (Arunachal)
]

# Add major cities
for city, coords in IndianRailwaysAPI.STATIONS.items():
    folium.CircleMarker(
        location=coords,
        radius=8,
        popup=f"<b>{city}</b><br>Major Railway Station",
        color='#3b82f6',
        fill=True,
        fill_color='#3b82f6',
        fill_opacity=0.6
    ).add_to(india_map)

# Add live train markers
for train in live_trains:
    # Filter by selected criteria
    if train['type'] not in train_types:
        continue
    if not (speed_range[0] <= train['speed'] <= speed_range[1]):
        continue
    if delay_filter != "Any":
        max_delay = {'On Time': 0, 'Up to 15 min': 15, 'Up to 30 min': 30, 'Up to 1 hr': 60}[delay_filter]
        if train['delay'] > max_delay:
            continue
    
    # Calculate marker color based on delay
    if train['delay'] > 30:
        color = '#ef4444'  # Red for high delay
    elif train['delay'] > 15:
        color = '#f59e0b'  # Orange for medium delay
    elif train['delay'] > 5:
        color = '#fbbf24'  # Yellow for minor delay
    else:
        color = '#10b981'  # Green for on-time
    
    # Create custom train icon
    icon_html = f"""
    <div style='
        background: {color};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        border: 3px solid white;
        box-shadow: 0 0 10px {color};
        cursor: pointer;
        animation: pulse 2s infinite;
    '>
        🚆
    </div>
    """
    
    # Calculate bearing for direction
    bearing = random.randint(0, 360)
    
    # Create popup content
    popup_html = f"""
    <div style='font-family: Arial; max-width: 300px;'>
        <h3 style='color: {color}; margin: 0 0 10px 0;'>🚅 {train['name']}</h3>
        <p><b>Train No:</b> {train['train_no']}</p>
        <p><b>Type:</b> {train['type']}</p>
        <p><b>Current Speed:</b> {train['speed']} km/h</p>
        <p><b>Status:</b> 
            <span style='color: {color}; font-weight: bold;'>
                {train['status']} {'(' + str(train['delay']) + ' min delay)' if train['delay'] > 0 else ''}
            </span>
        </p>
        <p><b>From:</b> {train['source']}</p>
        <p><b>To:</b> {train['destination']}</p>
        <p><b>Current:</b> {train['current_station']}</p>
        <p><b>Next:</b> {train['next_station']}</p>
        <p><b>Last Update:</b> {train['last_update'].strftime('%H:%M:%S')}</p>
        <button onclick="selectTrain('{train['train_no']}')" 
                style='background: {color}; color: white; border: none; padding: 8px 16px; 
                       border-radius: 5px; cursor: pointer; margin-top: 10px;'>
            Track This Train
        </button>
    </div>
    <script>
        function selectTrain(trainNo) {{
            window.parent.postMessage({{type: 'selectTrain', trainNo: trainNo}}, '*');
        }}
    </script>
    """
    
    # Add marker to map
    icon = folium.DivIcon(html=icon_html)
    folium.Marker(
        location=[train['latitude'], train['longitude']],
        popup=folium.Popup(popup_html, max_width=350),
        tooltip=f"{train['name']} - {train['speed']} km/h",
        icon=icon
    ).add_to(india_map)

# Display map
map_col, info_col = st.columns([2, 1])

with map_col:
    # Display the map
    folium_static(india_map, width=900, height=600)
    
    # Legend
    st.markdown("""
    <div style='background: rgba(30, 41, 59, 0.8); padding: 10px; border-radius: 10px; margin-top: 10px;'>
        <h4 style='margin: 0 0 10px 0;'>Map Legend</h4>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>
            <div><span style='color: #10b981; font-size: 20px;'>●</span> On Time (≤5 min)</div>
            <div><span style='color: #fbbf24; font-size: 20px;'>●</span> Minor Delay (6-15 min)</div>
            <div><span style='color: #f59e0b; font-size: 20px;'>●</span> Medium Delay (16-30 min)</div>
            <div><span style='color: #ef4444; font-size: 20px;'>●</span> High Delay (>30 min)</div>
            <div><span style='color: #3b82f6; font-size: 20px;'>●</span> Railway Station</div>
            <div><span style='color: #ffffff; font-size: 20px;'>🚆</span> Moving Train</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with info_col:
    st.subheader("🚅 Live Trains Nearby")
    
    # Filter trains for info panel
    filtered_trains = [t for t in live_trains if t['type'] in train_types and 
                      speed_range[0] <= t['speed'] <= speed_range[1]]
    
    # Sort by delay
    filtered_trains.sort(key=lambda x: x['delay'])
    
    for train in filtered_trains[:10]:
        delay_color = '#10b981' if train['delay'] <= 5 else \
                     '#fbbf24' if train['delay'] <= 15 else \
                     '#f59e0b' if train['delay'] <= 30 else '#ef4444'
        
        st.markdown(f"""
        <div class="live-train-card {'selected-train' if st.session_state.selected_train and st.session_state.selected_train['train_no'] == train['train_no'] else ''}" 
             onclick="selectTrain('{train['train_no']}')" style="cursor: pointer;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #38bdf8;">{train['name']}</h4>
                    <p style="margin: 5px 0; color: #94a3b8; font-size: 12px;">
                        {train['train_no']} • {train['type']}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="color: {delay_color}; font-weight: bold;">
                        {train['delay']} min
                    </span>
                    <div style="font-size: 12px; color: #94a3b8;">
                        {train['speed']} km/h
                    </div>
                </div>
            </div>
            <div style="margin-top: 8px; font-size: 13px; color: #cbd5e1;">
                📍 {train['current_station']} → {train['next_station']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== SELECTED TRAIN DETAILS ==========

if st.session_state.selected_train:
    st.markdown("---")
    st.subheader(f"📡 Detailed Tracking: {st.session_state.selected_train['name']}")
    
    train = st.session_state.selected_train
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Speed", f"{train['speed']} km/h", 
                 f"{'↗️ ' if train['speed'] > 80 else '↘️ '}{abs(train['speed'] - 80)}")
    with col2:
        st.metric("Delay", f"{train['delay']} minutes", 
                 "↗️ On Time" if train['delay'] == 0 else f"↘️ +{train['delay']} min")
    with col3:
        st.metric("Distance Covered", f"{random.randint(150, 350)} km", "↗️ 85%")
    with col4:
        st.metric("Next Station ETA", 
                 f"{(datetime.now() + timedelta(minutes=random.randint(15, 45))).strftime('%H:%M')}",
                 f"In {random.randint(15, 45)} min")
    
    # Route Visualization
    st.markdown("### 🗺️ Route Progress")
    
    if train['route']:
        route_data = train['route']
        current_idx = route_data.index(train['current_station']) if train['current_station'] in route_data else 0
        
        # Create progress bar
        progress = (current_idx + 1) / len(route_data)
        st.progress(progress)
        
        # Display stations
        cols = st.columns(len(route_data))
        for idx, station in enumerate(route_data):
            with cols[idx]:
                if idx < current_idx:
                    status = "✅ Passed"
                    color = "#10b981"
                elif idx == current_idx:
                    status = "📍 Current"
                    color = "#3b82f6"
                else:
                    status = "⏳ Upcoming"
                    color = "#94a3b8"
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="width: 30px; height: 30px; background: {color}; 
                         border-radius: 50%; margin: 0 auto 10px; display: flex; 
                         align-items: center; justify-content: center; color: white;">
                        {idx + 1}
                    </div>
                    <div style="font-weight: bold; font-size: 12px;">{station[:15]}</div>
                    <div style="font-size: 10px; color: {color};">{status}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Train Movement Simulation
    st.markdown("### 🎮 Live Movement Simulation")
    
    # Create a simple animation showing train movement
    simulation_html = f"""
    <div style="background: rgba(30, 41, 59, 0.8); padding: 20px; border-radius: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h3 style="margin: 0; color: #38bdf8;">{train['name']}</h3>
                <p style="margin: 5px 0; color: #94a3b8;">Simulating real-time movement</p>
            </div>
            <div style="font-size: 24px; animation: train-moving 2s linear infinite;">🚅</div>
        </div>
        
        <div style="position: relative; height: 100px; background: rgba(59, 130, 246, 0.1); 
             border-radius: 5px; overflow: hidden; margin: 20px 0;">
            <!-- Track -->
            <div style="position: absolute; top: 50%; left: 0; right: 0; height: 4px; 
                 background: linear-gradient(90deg, #3b82f6, #8b5cf6); transform: translateY(-50%);"></div>
            
            <!-- Moving Train -->
            <div id="moving-train" style="position: absolute; top: 50%; left: {progress*90}%; 
                 font-size: 40px; transform: translate(-50%, -50%); transition: left 2s ease;">
                🚅
            </div>
            
            <!-- Stations -->
            <div style="position: absolute; top: 50%; left: 0%; transform: translate(-50%, -50%); 
                 width: 20px; height: 20px; background: #10b981; border-radius: 50%; border: 3px solid white;"></div>
            <div style="position: absolute; top: 50%; left: 30%; transform: translate(-50%, -50%); 
                 width: 20px; height: 20px; background: #10b981; border-radius: 50%; border: 3px solid white;"></div>
            <div style="position: absolute; top: 50%; left: 60%; transform: translate(-50%, -50%); 
                 width: 20px; height: 20px; background: #3b82f6; border-radius: 50%; border: 3px solid white; 
                 box-shadow: 0 0 15px #3b82f6;"></div>
            <div style="position: absolute; top: 50%; left: 90%; transform: translate(-50%, -50%); 
                 width: 20px; height: 20px; background: #94a3b8; border-radius: 50%; border: 3px solid white;"></div>
            <div style="position: absolute; top: 50%; left: 100%; transform: translate(-50%, -50%); 
                 width: 20px; height: 20px; background: #94a3b8; border-radius: 50%; border: 3px solid white;"></div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8;">
            <div>{train['source']}</div>
            <div>{train['current_station']}</div>
            <div>{train['destination']}</div>
        </div>
    </div>
    
    <style>
        @keyframes train-moving {{
            0% {{ transform: translateX(0) rotate(0deg); }}
            25% {{ transform: translateX(5px) rotate(2deg); }}
            50% {{ transform: translateX(0) rotate(0deg); }}
            75% {{ transform: translateX(-5px) rotate(-2deg); }}
            100% {{ transform: translateX(0) rotate(0deg); }}
        }}
    </style>
    
    <script>
        // Animate train movement
        let train = document.getElementById('moving-train');
        let position = {progress * 90};
        let direction = 1;
        
        setInterval(() => {{
            position += direction * 0.5;
            if (position > 95 || position < 5) direction *= -1;
            train.style.left = position + '%';
        }}, 100);
    </script>
    """
    
    components.html(simulation_html, height=200)

# ========== AI PREDICTIONS ==========

st.markdown("---")
st.subheader("🤖 AI-Powered Predictions & Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 20px; border-radius: 12px;">
        <h4 style="color: white; margin-top: 0;">📈 Arrival Prediction</h4>
        <p style="color: #dbeafe;">
            <b>Accuracy:</b> 94.7% ✅<br>
            <b>Next Station:</b> {random.choice(list(IndianRailwaysAPI.STATIONS.keys()))}<br>
            <b>Predicted Arrival:</b> {datetime.now().strftime('%H:%M')}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ea580c, #f97316); padding: 20px; border-radius: 12px;">
        <h4 style="color: white; margin-top: 0;">⚠️ Delay Alert System</h4>
        <p style="color: #ffedd5;">
            <b>Current Risk:</b> Low ✅<br>
            <b>Affected Trains:</b> 42<br>
            <b>Avg Recovery:</b> 18.5 minutes
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #047857, #10b981); padding: 20px; border-radius: 12px;">
        <h4 style="color: white; margin-top: 0;">⚡ Efficiency Score</h4>
        <p style="color: #d1fae5;">
            <b>Current Score:</b> 87/100 🏆<br>
            <b>Fuel Saved:</b> 22%<br>
            <b>Time Optimized:</b> 14.5 minutes
        </p>
    </div>
    """, unsafe_allow_html=True)

# ========== AUTO REFRESH ==========

if st.session_state.auto_refresh:
    refresh_seconds = {'5 seconds': 5, '10 seconds': 10, '30 seconds': 30, '1 minute': 60}[refresh_rate]
    
    if (datetime.now() - st.session_state.last_update).seconds >= refresh_seconds:
        st.session_state.last_update = datetime.now()
        st.rerun()

# ========== FOOTER ==========

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
    <p>🚆 Indian Railways Live Tracker v2.0 | Data updates every 30 seconds | © 2024</p>
    <p>Note: This is a simulation. Real train positions may vary.</p>
</div>
""", unsafe_allow_html=True)

# JavaScript for train selection
st.markdown("""
<script>
    // Listen for train selection from map
    window.addEventListener('message', function(event) {
        if (event.data.type === 'selectTrain') {
            // Store in Streamlit session state
            Streamlit.setComponentValue({trainNo: event.data.trainNo});
        }
    });
    
    // Add click handlers to train cards
    document.addEventListener('click', function(e) {
        const card = e.target.closest('.live-train-card');
        if (card) {
            // Remove previous selection
            document.querySelectorAll('.live-train-card').forEach(c => {
                c.classList.remove('selected-train');
            });
            // Add selection to clicked card
            card.classList.add('selected-train');
        }
    });
</script>
""", unsafe_allow_html=True)
