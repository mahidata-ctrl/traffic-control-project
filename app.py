import streamlit as st
import time
import streamlit.components.v1 as components
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import requests
import json
from geopy.distance import geodesic
import pytz
from dateutil import parser
import threading
import queue
import asyncio
import aiohttp
import warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="🚆 Indian Railways Live Tracker",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Headers with glow effect */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00dbde, #fc00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 219, 222, 0.3);
    }
    
    /* Cards */
    .info-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(0, 219, 222, 0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00dbde, #fc00ff);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 219, 222, 0.3);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 219, 222, 0.4);
    }
    
    /* Metrics */
    .metric-box {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #00dbde;
    }
    
    /* Progress bars */
    .progress-container {
        height: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #00dbde, #fc00ff);
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    
    /* Train animation */
    @keyframes trainMove {
        0% { transform: translateX(-100px) rotate(0deg); }
        100% { transform: translateX(calc(100vw + 100px)) rotate(0deg); }
    }
    
    .moving-train {
        position: fixed;
        top: 80px;
        z-index: 1000;
        font-size: 40px;
        animation: trainMove 20s linear infinite;
        filter: drop-shadow(0 0 10px #00dbde);
    }
    
    /* Live indicator */
    .live-pulse {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #ff0000;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00dbde, #fc00ff);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ========== INDIAN RAILWAYS DATA ==========
class IndianRailwaysData:
    """Complete Indian Railways dataset with live simulation"""
    
    # Major Indian Railway Zones
    ZONES = {
        'NR': 'Northern Railway',
        'WR': 'Western Railway',
        'SR': 'Southern Railway',
        'ER': 'Eastern Railway',
        'CR': 'Central Railway',
        'NER': 'North Eastern Railway',
        'NFR': 'Northeast Frontier Railway',
        'ECR': 'East Central Railway',
        'SCR': 'South Central Railway',
        'SWR': 'South Western Railway',
        'NWR': 'North Western Railway',
        'WCR': 'West Central Railway',
        'SECR': 'South East Central Railway'
    }
    
    # Popular trains in India
    POPULAR_TRAINS = [
        # Southern Railway
        {
            'train_no': '12673', 'name': 'CHERAN SF EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'CBE', 'zone': 'SR',
            'speed_range': (75, 110), 'route': ['MAS', 'AJJ', 'KPD', 'JTJ', 'SA', 'CBE']
        },
        {
            'train_no': '12671', 'name': 'NILGIRI EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'MTP', 'zone': 'SR',
            'speed_range': (70, 100), 'route': ['MAS', 'KPD', 'SA', 'ED', 'CBE', 'MTP']
        },
        {
            'train_no': '12675', 'name': 'KOVAI EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'CBE', 'zone': 'SR',
            'speed_range': (80, 110), 'route': ['MAS', 'KPD', 'SA', 'CBE']
        },
        {
            'train_no': '12601', 'name': 'MYSORE EXP', 'type': 'Superfast',
            'source': 'MAS', 'dest': 'MYS', 'zone': 'SR',
            'speed_range': (75, 105), 'route': ['MAS', 'KPD', 'JTJ', 'SA', 'ED', 'MYS']
        },
        
        # Rajdhani/Shatabdi
        {
            'train_no': '12431', 'name': 'RAJDHANI EXP', 'type': 'Rajdhani',
            'source': 'NDLS', 'dest': 'HWH', 'zone': 'NR',
            'speed_range': (90, 130), 'route': ['NDLS', 'CNB', 'ALD', 'MGS', 'HWH']
        },
        {
            'train_no': '12007', 'name': 'SHATABDI EXP', 'type': 'Shatabdi',
            'source': 'MAS', 'dest': 'SBC', 'zone': 'SR',
            'speed_range': (85, 120), 'route': ['MAS', 'KPD', 'KJM', 'SBC']
        },
        {
            'train_no': '12213', 'name': 'DURONTO EXP', 'type': 'Duronto',
            'source': 'NDLS', 'dest': 'ADI', 'zone': 'NR',
            'speed_range': (85, 125), 'route': ['NDLS', 'ADI']
        },
        
        # Other zones
        {
            'train_no': '11013', 'name': 'DECCAN EXP', 'type': 'Express',
            'source': 'BCT', 'dest': 'PUNE', 'zone': 'WR',
            'speed_range': (65, 95), 'route': ['BCT', 'DR', 'KYN', 'KJT', 'LNL', 'PUNE']
        },
        {
            'train_no': '12627', 'name': 'KARNATAKA EXP', 'type': 'Superfast',
            'source': 'NDLS', 'dest': 'SBC', 'zone': 'NR',
            'speed_range': (75, 110), 'route': ['NDLS', 'AGC', 'BPL', 'G', 'SBC']
        },
        {
            'train_no': '12649', 'name': 'GARIB RATH', 'type': 'Garib Rath',
            'source': 'NDLS', 'dest': 'JP', 'zone': 'NR',
            'speed_range': (80, 115), 'route': ['NDLS', 'JP']
        }
    ]
    
    # Indian railway stations with coordinates
    STATIONS = {
        # Southern Railway
        'MAS': {'name': 'Chennai Central', 'lat': 13.0827, 'lon': 80.2707, 'zone': 'SR'},
        'KPD': {'name': 'Katpadi Junction', 'lat': 12.9702, 'lon': 79.1590, 'zone': 'SR'},
        'JTJ': {'name': 'Jolarpettai Junction', 'lat': 12.5667, 'lon': 78.5667, 'zone': 'SR'},
        'SA': {'name': 'Salem Junction', 'lat': 11.6643, 'lon': 78.1460, 'zone': 'SR'},
        'ED': {'name': 'Erode Junction', 'lat': 11.3420, 'lon': 77.7172, 'zone': 'SR'},
        'CBE': {'name': 'Coimbatore Junction', 'lat': 11.0168, 'lon': 76.9558, 'zone': 'SR'},
        'TUP': {'name': 'Tiruppur', 'lat': 11.1075, 'lon': 77.3398, 'zone': 'SR'},
        'MTP': {'name': 'Metupalaiyam', 'lat': 11.3000, 'lon': 76.9500, 'zone': 'SR'},
        'MYS': {'name': 'Mysore Junction', 'lat': 12.3086, 'lon': 76.6531, 'zone': 'SR'},
        'SBC': {'name': 'Bangalore City', 'lat': 12.9774, 'lon': 77.5695, 'zone': 'SR'},
        'AJJ': {'name': 'Arakkonam Junction', 'lat': 13.0846, 'lon': 79.6725, 'zone': 'SR'},
        
        # Northern Railway
        'NDLS': {'name': 'New Delhi', 'lat': 28.6423, 'lon': 77.2211, 'zone': 'NR'},
        'CNB': {'name': 'Kanpur Central', 'lat': 26.4499, 'lon': 80.3319, 'zone': 'NR'},
        'ALD': {'name': 'Allahabad Junction', 'lat': 25.4358, 'lon': 81.8463, 'zone': 'NR'},
        'MGS': {'name': 'Mughalsarai Junction', 'lat': 25.2819, 'lon': 83.1215, 'zone': 'NR'},
        'JP': {'name': 'Jaipur Junction', 'lat': 26.9124, 'lon': 75.7873, 'zone': 'NR'},
        'ADI': {'name': 'Ahmedabad Junction', 'lat': 23.0258, 'lon': 72.5873, 'zone': 'WR'},
        'AGC': {'name': 'Agra Cantonment', 'lat': 27.1617, 'lon': 77.9894, 'zone': 'NR'},
        'BPL': {'name': 'Bhopal Junction', 'lat': 23.2599, 'lon': 77.4126, 'zone': 'WCR'},
        'G': {'name': 'Gwalior Junction', 'lat': 26.2183, 'lon': 78.1828, 'zone': 'NR'},
        
        # Western Railway
        'BCT': {'name': 'Mumbai Central', 'lat': 18.9698, 'lon': 72.8195, 'zone': 'WR'},
        'DR': {'name': 'Dadar', 'lat': 19.0176, 'lon': 72.8561, 'zone': 'WR'},
        'KYN': {'name': 'Kalyan Junction', 'lat': 19.2437, 'lon': 73.1355, 'zone': 'CR'},
        'KJT': {'name': 'Karjat', 'lat': 18.9106, 'lon': 73.3236, 'zone': 'CR'},
        'LNL': {'name': 'Lonavala', 'lat': 18.7528, 'lon': 73.4067, 'zone': 'CR'},
        'PUNE': {'name': 'Pune Junction', 'lat': 18.5204, 'lon': 73.8567, 'zone': 'CR'},
        
        # Eastern Railway
        'HWH': {'name': 'Howrah Junction', 'lat': 22.5859, 'lon': 88.3476, 'zone': 'ER'},
        'SDAH': {'name': 'Sealdah', 'lat': 22.5670, 'lon': 88.3700, 'zone': 'ER'},
        
        # Additional major stations
        'LKO': {'name': 'Lucknow NR', 'lat': 26.8465, 'lon': 80.9462, 'zone': 'NER'},
        'PNBE': {'name': 'Patna Junction', 'lat': 25.6093, 'lon': 85.1238, 'zone': 'ECR'},
        'NGP': {'name': 'Nagpur Junction', 'lat': 21.1458, 'lon': 79.0882, 'zone': 'SECR'},
        'VSKP': {'name': 'Visakhapatnam Junction', 'lat': 17.6868, 'lon': 83.2185, 'zone': 'ECoR'},
        'HYB': {'name': 'Hyderabad Deccan', 'lat': 17.3616, 'lon': 78.4747, 'zone': 'SCR'},
        'KOAA': {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639, 'zone': 'ER'}
    }
    
    # Train types with colors
    TRAIN_TYPES = {
        'Rajdhani': {'color': '#FF0000', 'icon': '👑', 'priority': 1},
        'Shatabdi': {'color': '#0000FF', 'icon': '⚡', 'priority': 2},
        'Duronto': {'color': '#008000', 'icon': '🚀', 'priority': 3},
        'Garib Rath': {'color': '#800080', 'icon': '💰', 'priority': 4},
        'Superfast': {'color': '#DC143C', 'icon': '🚅', 'priority': 5},
        'Express': {'color': '#228B22', 'icon': '🚂', 'priority': 6},
        'Passenger': {'color': '#808080', 'icon': '🚃', 'priority': 7},
        'Special': {'color': '#FFD700', 'icon': '⭐', 'priority': 8}
    }

# ========== REAL-TIME TRAIN SIMULATOR ==========
class LiveTrainSimulator:
    """Simulates real-time train movement across India"""
    
    def __init__(self, num_trains=50):
        self.num_trains = num_trains
        self.trains = []
        self.last_update = datetime.now()
        self.running = True
        self._initialize_trains()
        
        # Start background thread for updates
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _initialize_trains(self):
        """Initialize trains with realistic positions"""
        self.trains = []
        
        # Add popular trains
        for train_info in IndianRailwaysData.POPULAR_TRAINS:
            route = train_info['route']
            if len(route) >= 2:
                current_idx = random.randint(0, len(route) - 2)
                current_station = route[current_idx]
                next_station = route[current_idx + 1]
                
                # Get coordinates and add random offset for between-station movement
                if current_station in IndianRailwaysData.STATIONS:
                    base_lat = IndianRailwaysData.STATIONS[current_station]['lat']
                    base_lon = IndianRailwaysData.STATIONS[current_station]['lon']
                    
                    # Add random offset (simulating movement between stations)
                    lat_offset = random.uniform(-0.3, 0.3)
                    lon_offset = random.uniform(-0.3, 0.3)
                    
                    train = {
                        'train_no': train_info['train_no'],
                        'name': train_info['name'],
                        'type': train_info['type'],
                        'source': train_info['source'],
                        'destination': train_info['dest'],
                        'current_station': current_station,
                        'next_station': next_station,
                        'route': route,
                        'current_idx': current_idx,
                        'speed': random.randint(*train_info['speed_range']),
                        'delay': random.randint(0, 45),
                        'status': 'Running',
                        'latitude': base_lat + lat_offset,
                        'longitude': base_lon + lon_offset,
                        'last_update': datetime.now(),
                        'color': IndianRailwaysData.TRAIN_TYPES[train_info['type']]['color'],
                        'icon': IndianRailwaysData.TRAIN_TYPES[train_info['type']]['icon'],
                        'zone': train_info['zone'],
                        'passengers': random.randint(100, 800),
                        'coach_count': random.randint(12, 24)
                    }
                    self.trains.append(train)
        
        # Add random trains to reach num_trains
        while len(self.trains) < self.num_trains:
            train_no = str(random.randint(12000, 19999))
            train_type = random.choice(list(IndianRailwaysData.TRAIN_TYPES.keys()))
            
            # Random source and destination
            stations = list(IndianRailwaysData.STATIONS.keys())
            source = random.choice(stations)
            dest = random.choice([s for s in stations if s != source])
            
            # Random position in India
            lat = random.uniform(8.0, 37.0)
            lon = random.uniform(68.0, 97.0)
            
            train = {
                'train_no': train_no,
                'name': f'{train_type} {train_no}',
                'type': train_type,
                'source': source,
                'destination': dest,
                'current_station': random.choice(stations),
                'next_station': random.choice(stations),
                'route': [],
                'current_idx': 0,
                'speed': random.randint(40, 100),
                'delay': random.randint(0, 60),
                'status': random.choice(['Running', 'Delayed', 'On Time']),
                'latitude': lat,
                'longitude': lon,
                'last_update': datetime.now(),
                'color': IndianRailwaysData.TRAIN_TYPES[train_type]['color'],
                'icon': IndianRailwaysData.TRAIN_TYPES[train_type]['icon'],
                'zone': random.choice(list(IndianRailwaysData.ZONES.keys())),
                'passengers': random.randint(50, 600),
                'coach_count': random.randint(8, 20)
            }
            self.trains.append(train)
    
    def _update_loop(self):
        """Background thread to update train positions"""
        while self.running:
            time.sleep(2)  # Update every 2 seconds
            self.update_positions()
    
    def update_positions(self):
        """Update all train positions"""
        for train in self.trains:
            # Move train along route if it has one
            if train['route'] and len(train['route']) > 1:
                route = train['route']
                current_idx = train['current_idx']
                
                # Check if reached next station
                if current_idx < len(route) - 1:
                    current_station = route[current_idx]
                    next_station = route[current_idx + 1]
                    
                    # Simulate movement towards next station
                    if current_station in IndianRailwaysData.STATIONS and next_station in IndianRailwaysData.STATIONS:
                        start_lat = IndianRailwaysData.STATIONS[current_station]['lat']
                        start_lon = IndianRailwaysData.STATIONS[current_station]['lon']
                        end_lat = IndianRailwaysData.STATIONS[next_station]['lat']
                        end_lon = IndianRailwaysData.STATIONS[next_station]['lon']
                        
                        # Calculate progress (simplified)
                        progress = random.uniform(0.1, 0.9)  # Random progress between stations
                        
                        train['latitude'] = start_lat + (end_lat - start_lat) * progress
                        train['longitude'] = start_lon + (end_lon - start_lon) * progress
                        
                        # Occasionally move to next station
                        if random.random() < 0.05:  # 5% chance to reach next station
                            train['current_idx'] += 1
                            train['current_station'] = next_station
                            if current_idx + 2 < len(route):
                                train['next_station'] = route[current_idx + 2]
            
            # Random speed changes
            speed_change = random.uniform(-3, 3)
            min_speed, max_speed = 20, 130
            if train['type'] == 'Rajdhani':
                min_speed, max_speed = 80, 130
            elif train['type'] == 'Shatabdi':
                min_speed, max_speed = 75, 120
            elif train['type'] == 'Superfast':
                min_speed, max_speed = 60, 110
            
            train['speed'] = max(min_speed, min(max_speed, train['speed'] + speed_change))
            
            # Random delay changes
            delay_change = random.randint(-3, 5)
            train['delay'] = max(0, train['delay'] + delay_change)
            
            # Update status based on delay
            if train['delay'] > 60:
                train['status'] = 'Heavily Delayed'
            elif train['delay'] > 30:
                train['status'] = 'Delayed'
            elif train['delay'] > 15:
                train['status'] = 'Slightly Delayed'
            else:
                train['status'] = 'On Time'
            
            # Update timestamp
            train['last_update'] = datetime.now()
        
        self.last_update = datetime.now()
    
    def get_all_trains(self, filters=None):
        """Get all trains with optional filtering"""
        trains = self.trains.copy()
        
        if filters:
            # Apply filters
            if filters.get('train_types'):
                trains = [t for t in trains if t['type'] in filters['train_types']]
            
            if filters.get('speed_range'):
                min_speed, max_speed = filters['speed_range']
                trains = [t for t in trains if min_speed <= t['speed'] <= max_speed]
            
            if filters.get('delay_filter') != 'Any':
                max_delay = {
                    'On Time': 5,
                    'Up to 15 min': 15,
                    'Up to 30 min': 30,
                    'Up to 1 hr': 60
                }.get(filters['delay_filter'], 999)
                trains = [t for t in trains if t['delay'] <= max_delay]
            
            if filters.get('zone'):
                trains = [t for t in trains if t['zone'] == filters['zone']]
        
        return trains
    
    def get_train_by_number(self, train_no):
        """Get specific train by number"""
        for train in self.trains:
            if train['train_no'] == train_no:
                return train
        return None
    
    def search_trains(self, query, by='number'):
        """Search trains by various criteria"""
        results = []
        query_lower = query.lower()
        
        for train in self.trains:
            if by == 'number' and query_lower in train['train_no'].lower():
                results.append(train)
            elif by == 'name' and query_lower in train['name'].lower():
                results.append(train)
            elif by == 'station':
                if (query_lower in IndianRailwaysData.STATIONS.get(train['current_station'], {}).get('name', '').lower() or
                    query_lower in IndianRailwaysData.STATIONS.get(train['next_station'], {}).get('name', '').lower()):
                    results.append(train)
        
        return results
    
    def get_statistics(self):
        """Get overall statistics"""
        total_trains = len(self.trains)
        avg_speed = np.mean([t['speed'] for t in self.trains])
        on_time = len([t for t in self.trains if t['delay'] <= 5])
        delayed = len([t for t in self.trains if t['delay'] > 5])
        
        # Count by type
        type_counts = {}
        for train in self.trains:
            type_counts[train['type']] = type_counts.get(train['type'], 0) + 1
        
        # Count by zone
        zone_counts = {}
        for train in self.trains:
            zone_counts[train['zone']] = zone_counts.get(train['zone'], 0) + 1
        
        return {
            'total_trains': total_trains,
            'avg_speed': avg_speed,
            'on_time_percentage': (on_time / total_trains * 100) if total_trains > 0 else 0,
            'delayed_trains': delayed,
            'type_distribution': type_counts,
            'zone_distribution': zone_counts,
            'last_update': self.last_update
        }

# ========== INITIALIZE SIMULATOR ==========
@st.cache_resource
def get_simulator():
    return LiveTrainSimulator(num_trains=100)

simulator = get_simulator()

# ========== SIDEBAR ==========
with st.sidebar:
    # Logo and Title
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/49/Indian_Railways_Logo.svg/800px-Indian_Railways_Logo.svg.png", 
                width=60)
    with col_title:
        st.markdown("<h2 style='margin: 0;'>Indian Railways</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Search Section
    st.subheader("🔍 Search & Track")
    
    search_type = st.radio("Search By:", ["Train Number", "Train Name", "Station", "Route"], horizontal=True)
    
    if search_type == "Train Number":
        train_no = st.text_input("Enter Train Number:", "12673")
        if st.button("Track Train", use_container_width=True):
            selected_train = simulator.get_train_by_number(train_no)
            if selected_train:
                st.session_state.selected_train = selected_train
                st.success(f"Tracking {selected_train['name']}")
            else:
                st.error("Train not found!")
    
    elif search_type == "Train Name":
        train_name = st.selectbox(
            "Select Train:",
            [train['name'] for train in IndianRailwaysData.POPULAR_TRAINS]
        )
        if st.button("Track Selected", use_container_width=True):
            for train in simulator.trains:
                if train['name'] == train_name:
                    st.session_state.selected_train = train
                    st.success(f"Tracking {train['name']}")
                    break
    
    elif search_type == "Station":
        station_name = st.selectbox(
            "Select Station:",
            sorted([s['name'] for s in IndianRailwaysData.STATIONS.values()])
        )
    
    else:  # Route
        col_from, col_to = st.columns(2)
        with col_from:
            from_station = st.selectbox("From:", list(IndianRailwaysData.STATIONS.keys()), 
                                       format_func=lambda x: IndianRailwaysData.STATIONS[x]['name'])
        with col_to:
            to_station = st.selectbox("To:", [s for s in IndianRailwaysData.STATIONS.keys() if s != from_station],
                                     format_func=lambda x: IndianRailwaysData.STATIONS[x]['name'])
    
    st.markdown("---")
    
    # Filters
    st.subheader("🎯 Filters")
    
    train_types = st.multiselect(
        "Train Types:",
        list(IndianRailwaysData.TRAIN_TYPES.keys()),
        default=['Superfast', 'Rajdhani', 'Shatabdi', 'Express']
    )
    
    zones = st.multiselect(
        "Railway Zones:",
        list(IndianRailwaysData.ZONES.keys()),
        format_func=lambda x: IndianRailwaysData.ZONES[x]
    )
    
    speed_range = st.slider("Speed Range (km/h):", 0, 150, (40, 120))
    
    delay_filter = st.select_slider(
        "Delay Status:",
        options=["On Time", "Up to 15 min", "Up to 30 min", "Up to 1 hr", "Any"],
        value="Up to 30 min"
    )
    
    st.markdown("---")
    
    # Live Stats
    st.subheader("📊 Live Statistics")
    
    stats = simulator.get_statistics()
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("Active Trains", f"{stats['total_trains']:,}")
        st.metric("On Time", f"{stats['on_time_percentage']:.1f}%")
    with col_stat2:
        st.metric("Avg Speed", f"{stats['avg_speed']:.0f} km/h")
        st.metric("Delayed", f"{stats['delayed_trains']}")
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("Auto Refresh", value=True, key="auto_refresh")
    refresh_rate = st.select_slider("Refresh Rate:", 
                                   options=["5 seconds", "10 seconds", "30 seconds", "1 minute"],
                                   value="10 seconds")
    
    st.markdown("---")
    
    # System Info
    st.subheader("⚙️ System Info")
    st.info("""
    **AI Model**: Enhanced DQN
    **Tracking**: Simulated Live Data
    **Coverage**: Pan-India
    **Update**: Real-time
    **Version**: 3.0.0
    """)
    
    if st.button("🔄 Force Update", use_container_width=True):
        st.rerun()

# ========== MAIN DASHBOARD ==========
st.title("🚆 Indian Railways Live Train Tracker")
st.markdown("<span class='live-pulse'></span> <span style='color: #ff0000; font-weight: bold;'>LIVE</span> Real-time tracking of trains across India", 
            unsafe_allow_html=True)

# Add moving train animation at top
st.markdown("<div class='moving-train'>🚅</div>", unsafe_allow_html=True)

# Initialize session state
if 'selected_train' not in st.session_state:
    st.session_state.selected_train = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# ========== TOP METRICS ==========
st.markdown("---")
col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)

stats = simulator.get_statistics()

with col_metrics1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Active Trains", f"{stats['total_trains']:,}", "+12")
    st.markdown('</div>', unsafe_allow_html=True)

with col_metrics2:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Avg Speed", f"{stats['avg_speed']:.0f} km/h", "+2.3%")
    st.markdown('</div>', unsafe_allow_html=True)

with col_metrics3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    on_time = stats['on_time_percentage']
    st.metric("Punctuality", f"{on_time:.1f}%", 
             f"{'+' if on_time > 80 else ''}{on_time - 80:.1f}%" if on_time != 0 else "0%")
    st.markdown('</div>', unsafe_allow_html=True)

with col_metrics4:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("Last Update", stats['last_update'].strftime("%H:%M:%S"))
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN CONTENT TABS ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Live Map", "📈 Dashboard", "🚆 Train Details", "📊 Analytics", "🤖 AI Control"])

with tab1:
    # LIVE MAP VIEW
    st.subheader("📍 Live Train Positions Across India")
    
    # Map controls
    col_map_ctrl1, col_map_ctrl2, col_map_ctrl3 = st.columns(3)
    with col_map_ctrl1:
        map_style = st.selectbox("Map Style:", 
                                ["Dark", "Light", "Satellite", "Terrain", "Night"],
                                key="map_style")
    with col_map_ctrl2:
        show_stations = st.toggle("Show Stations", value=True)
    with col_map_ctrl3:
        cluster_trains = st.toggle("Cluster Markers", value=True)
    
    # Create map
    col_map, col_list = st.columns([2, 1])
    
    with col_map:
        # Initialize Folium map centered on India
        if map_style == "Dark":
            tiles = "CartoDB dark_matter"
        elif map_style == "Light":
            tiles = "OpenStreetMap"
        elif map_style == "Satellite":
            tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        elif map_style == "Terrain":
            tiles = "Stamen Terrain"
        else:  # Night
            tiles = "CartoDB dark_matter"
        
        m = folium.Map(location=[22.5937, 79.9629], zoom_start=5, tiles=tiles, 
                      control_scale=True, max_bounds=True)
        
        # Add India bounds
        india_bounds = [[6.0, 68.0], [35.0, 97.0]]
        
        # Filter trains
        filters = {
            'train_types': train_types,
            'speed_range': speed_range,
            'delay_filter': delay_filter,
            'zone': zones[0] if zones else None
        }
        filtered_trains = simulator.get_all_trains(filters)
        
        # Add station markers
        if show_stations:
            for code, station in IndianRailwaysData.STATIONS.items():
                folium.CircleMarker(
                    location=[station['lat'], station['lon']],
                    radius=5,
                    popup=f"""
                    <div style='font-family: Arial;'>
                        <h4 style='color: #3b82f6;'>{station['name']}</h4>
                        <p><b>Code:</b> {code}</p>
                        <p><b>Zone:</b> {station['zone']}</p>
                        <p><b>Type:</b> Major Station</p>
                    </div>
                    """,
                    tooltip=station['name'],
                    color='#3b82f6',
                    fill=True,
                    fill_color='#3b82f6',
                    fill_opacity=0.7
                ).add_to(m)
        
        # Add train markers
        for train in filtered_trains[:100]:  # Limit to 100 markers for performance
            # Determine marker color based on delay
            if train['delay'] > 60:
                color = '#ef4444'  # Red
                size = 12
            elif train['delay'] > 30:
                color = '#f59e0b'  # Orange
                size = 10
            elif train['delay'] > 15:
                color = '#fbbf24'  # Yellow
                size = 8
            else:
                color = '#10b981'  # Green
                size = 8
            
            # Create custom HTML for train marker
            icon_html = f"""
            <div style='
                background: {color};
                width: {size*2}px;
                height: {size*2}px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: {size}px;
                border: 2px solid white;
                box-shadow: 0 0 10px {color};
                cursor: pointer;
                animation: pulse 2s infinite;
            '>
                {train['icon']}
            </div>
            """
            
            # Create popup content
            popup_html = f"""
            <div style='font-family: Arial; max-width: 300px;'>
                <h3 style='color: {color}; margin: 0 0 10px 0;'>{train['icon']} {train['name']}</h3>
                <p><b>Train No:</b> {train['train_no']}</p>
                <p><b>Type:</b> {train['type']}</p>
                <p><b>Current Speed:</b> {train['speed']} km/h</p>
                <p><b>Status:</b> <span style='color: {color};'>{train['status']}</span></p>
                <p><b>Delay:</b> {train['delay']} minutes</p>
                <p><b>Current:</b> {IndianRailwaysData.STATIONS.get(train['current_station'], {}).get('name', train['current_station'])}</p>
                <p><b>Next:</b> {IndianRailwaysData.STATIONS.get(train['next_station'], {}).get('name', train['next_station'])}</p>
                <button onclick="selectTrain('{train['train_no']}')" 
                        style='background: {color}; color: white; border: none; padding: 8px 16px; 
                               border-radius: 5px; cursor: pointer; margin-top: 10px; width: 100%;'>
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
                tooltip=f"{train['name']} - {train['speed']} km/h - {train['delay']} min delay",
                icon=icon
            ).add_to(m)
        
        # Add selected train highlight
        if st.session_state.selected_train:
            selected = st.session_state.selected_train
            folium.CircleMarker(
                location=[selected['latitude'], selected['longitude']],
                radius=15,
                popup=f"SELECTED: {selected['name']}",
                color='#ffffff',
                fill=True,
                fill_color='#ffffff',
                fill_opacity=0.8,
                weight=3
            ).add_to(m)
        
        # Display map
        folium_static(m, width=800, height=600)
        
        # Legend
        st.markdown("""
        <div style='background: rgba(0,0,0,0.7); padding: 15px; border-radius: 10px; margin-top: 10px;'>
            <h4 style='margin: 0 0 10px 0; color: white;'>Map Legend</h4>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; color: white;'>
                <div><span style='color: #10b981; font-size: 20px;'>●</span> On Time (≤15 min)</div>
                <div><span style='color: #fbbf24; font-size: 20px;'>●</span> Minor Delay (16-30 min)</div>
                <div><span style='color: #f59e0b; font-size: 20px;'>●</span> Medium Delay (31-60 min)</div>
                <div><span style='color: #ef4444; font-size: 20px;'>●</span> High Delay (>60 min)</div>
                <div><span style='color: #3b82f6; font-size: 20px;'>●</span> Railway Station</div>
                <div><span style='color: #ffffff; font-size: 20px;'>🔵</span> Selected Train</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_list:
        st.subheader("🚅 Nearby Trains")
        
        # Sort trains by proximity to center of India
        center_lat, center_lon = 22.5937, 79.9629
        filtered_trains.sort(key=lambda t: geodesic((center_lat, center_lon), 
                                                    (t['latitude'], t['longitude'])).km)
        
        for train in filtered_trains[:15]:
            delay_color = '#10b981' if train['delay'] <= 15 else \
                         '#fbbf24' if train['delay'] <= 30 else \
                         '#f59e0b' if train['delay'] <= 60 else '#ef4444'
            
            is_selected = st.session_state.selected_train and \
                         st.session_state.selected_train['train_no'] == train['train_no']
            
            border_color = '#00dbde' if is_selected else delay_color
            
            st.markdown(f"""
            <div class="info-card" onclick="selectTrain('{train['train_no']}')" 
                 style="border-left: 4px solid {border_color}; cursor: pointer;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0; color: #00dbde;">{train['name']}</h4>
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
                    📍 {IndianRailwaysData.STATIONS.get(train['current_station'], {}).get('name', train['current_station'])} 
                    → {IndianRailwaysData.STATIONS.get(train['next_station'], {}).get('name', train['next_station'])}
                </div>
                {'<div style="color: #00dbde; font-size: 12px; margin-top: 5px;">⭐ SELECTED</div>' if is_selected else ''}
            </div>
            """, unsafe_allow_html=True)

with tab2:
    # DASHBOARD VIEW
    st.subheader("📊 Real-time Dashboard")
    
    # Create metrics grid
    col_dash1, col_dash2, col_dash3 = st.columns(3)
    
    with col_dash1:
        st.markdown("### 🚅 Train Types Distribution")
        type_counts = stats['type_distribution']
        fig_type = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            color=list(type_counts.keys()),
            color_discrete_map={k: IndianRailwaysData.TRAIN_TYPES[k]['color'] 
                               for k in type_counts.keys() if k in IndianRailwaysData.TRAIN_TYPES},
            hole=0.4
        )
        fig_type.update_layout(showlegend=True, height=300)
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col_dash2:
        st.markdown("### 🗺️ Zone-wise Distribution")
        zone_counts = stats['zone_distribution']
        fig_zone = px.bar(
            x=list(zone_counts.keys()),
            y=list(zone_counts.values()),
            color=list(zone_counts.keys()),
            labels={'x': 'Zone', 'y': 'Number of Trains'}
        )
        fig_zone.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_zone, use_container_width=True)
    
    with col_dash3:
        st.markdown("### 📈 Speed Distribution")
        speeds = [t['speed'] for t in simulator.trains]
        fig_speed = px.histogram(
            x=speeds,
            nbins=20,
            labels={'x': 'Speed (km/h)', 'y': 'Count'}
        )
        fig_speed.update_layout(height=300)
        st.plotly_chart(fig_speed, use_container_width=True)
    
    # Real-time charts
    st.markdown("### 📊 Live Performance Metrics")
    
    # Create sample time series data
    time_points = pd.date_range(end=datetime.now(), periods=20, freq='5min')
    speed_data = pd.DataFrame({
        'Time': time_points,
        'Avg Speed': np.random.normal(80, 10, 20),
        'Max Speed': np.random.normal(110, 15, 20),
        'Min Speed': np.random.normal(50, 8, 20)
    })
    
    delay_data = pd.DataFrame({
        'Time': time_points,
        'Avg Delay': np.random.exponential(15, 20),
        'Max Delay': np.random.exponential(45, 20),
        'On Time %': 100 - np.random.exponential(20, 20)
    })
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_speed_line = px.line(
            speed_data, x='Time', y=['Avg Speed', 'Max Speed', 'Min Speed'],
            title='Speed Trends (Last 100 minutes)'
        )
        st.plotly_chart(fig_speed_line, use_container_width=True)
    
    with col_chart2:
        fig_delay_line = px.line(
            delay_data, x='Time', y=['Avg Delay', 'Max Delay'],
            title='Delay Trends (Last 100 minutes)'
        )
        st.plotly_chart(fig_delay_line, use_container_width=True)

with tab3:
    # TRAIN DETAILS VIEW
    st.subheader("🚆 Train Details & Tracking")
    
    if st.session_state.selected_train:
        train = st.session_state.selected_train
        
        # Header with train info
        col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
        
        with col_header1:
            st.markdown(f"### {train['icon']} {train['name']}")
            st.markdown(f"**Train No:** {train['train_no']} | **Type:** {train['type']} | **Zone:** {train['zone']}")
        
        with col_header2:
            delay_color = '#10b981' if train['delay'] <= 15 else \
                         '#fbbf24' if train['delay'] <= 30 else \
                         '#f59e0b' if train['delay'] <= 60 else '#ef4444'
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 24px; color: {delay_color}; font-weight: bold;">
                    {train['delay']} min
                </div>
                <div style="font-size: 12px; color: #94a3b8;">DELAY</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_header3:
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 24px; color: #00dbde; font-weight: bold;">
                    {train['speed']} km/h
                </div>
                <div style="font-size: 12px; color: #94a3b8;">SPEED</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed information in columns
        col_detail1, col_detail2, col_detail3 = st.columns(3)
        
        with col_detail1:
            st.markdown("### 📍 Route Information")
            st.markdown(f"""
            - **Source:** {IndianRailwaysData.STATIONS.get(train['source'], {}).get('name', train['source'])}
            - **Destination:** {IndianRailwaysData.STATIONS.get(train['destination'], {}).get('name', train['destination'])}
            - **Current Station:** {IndianRailwaysData.STATIONS.get(train['current_station'], {}).get('name', train['current_station'])}
            - **Next Station:** {IndianRailwaysData.STATIONS.get(train['next_station'], {}).get('name', train['next_station'])}
            - **Distance Covered:** {random.randint(100, 800)} km
            - **Distance Remaining:** {random.randint(50, 400)} km
            """)
        
        with col_detail2:
            st.markdown("### 📊 Train Specifications")
            st.markdown(f"""
            - **Coach Count:** {train['coach_count']}
            - **Passenger Capacity:** {train['passengers']}
            - **Max Speed:** {random.randint(110, 160)} km/h
            - **Avg Speed:** {train['speed']} km/h
            - **Running Status:** {train['status']}
            - **Last Updated:** {train['last_update'].strftime('%H:%M:%S')}
            """)
        
        with col_detail3:
            st.markdown("### ⚙️ Technical Details")
            st.markdown(f"""
            - **Engine Type:** {'Electric' if random.random() > 0.3 else 'Diesel'}
            - **Power:** {random.randint(3000, 6000)} HP
            - **Fuel Efficiency:** {random.randint(4, 8)} km/l
            - **Maintenance Due:** In {random.randint(100, 5000)} km
            - **Signal Status:** {'Green' if random.random() > 0.2 else 'Yellow'}
            - **Track Condition:** {'Good' if random.random() > 0.3 else 'Average'}
            """)
        
        # Route Visualization
        st.markdown("---")
        st.markdown("### 🗺️ Route Progress")
        
        if train['route']:
            # Create a simple route visualization
            route_stations = train['route']
            current_idx = train['current_idx'] if 'current_idx' in train else 0
            
            # Create progress visualization
            progress_html = """
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0;">
                <div style="display: flex; justify-content: space-between; position: relative; padding: 0 20px;">
            """
            
            # Add track line
            progress_html += """
                <div style="position: absolute; top: 50%; left: 0; right: 0; height: 4px; 
                     background: linear-gradient(90deg, #00dbde, #fc00ff); transform: translateY(-50%); 
                     z-index: 1;"></div>
            """
            
            # Add stations
            for idx, station_code in enumerate(route_stations):
                station = IndianRailwaysData.STATIONS.get(station_code, {'name': station_code})
                station_name = station['name']
                
                if idx == current_idx:
                    dot_color = "#00dbde"
                    dot_size = "30px"
                    status = "📍 CURRENT"
                elif idx < current_idx:
                    dot_color = "#10b981"
                    dot_size = "20px"
                    status = "✅ PASSED"
                else:
                    dot_color = "#94a3b8"
                    dot_size = "20px"
                    status = "⏳ UPCOMING"
                
                progress_html += f"""
                <div style="text-align: center; position: relative; z-index: 2; flex: 1;">
                    <div style="width: {dot_size}; height: {dot_size}; background: {dot_color}; 
                         border-radius: 50%; margin: 0 auto 10px; border: 3px solid #0f0c29;"></div>
                    <div style="font-size: 12px; font-weight: bold; color: {dot_color};">
                        {station_name[:15]}
                    </div>
                    <div style="font-size: 10px; color: {dot_color};">{status}</div>
                </div>
                """
            
            progress_html += "</div></div>"
            
            st.markdown(progress_html, unsafe_allow_html=True)
        
        # Live Movement Simulation
        st.markdown("---")
        st.markdown("### 🎮 Live Movement Simulation")
        
        # Create simulation visualization
        sim_html = f"""
        <div style="background: linear-gradient(135deg, #0f0c29, #24243e); padding: 20px; border-radius: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h3 style="margin: 0; color: #00dbde;">{train['name']} - Live Movement</h3>
                    <p style="margin: 5px 0; color: #94a3b8;">Simulating real-time GPS movement</p>
                </div>
                <div style="font-size: 40px; animation: trainMove 3s linear infinite;">🚅</div>
            </div>
            
            <div style="position: relative; height: 100px; background: rgba(0, 219, 222, 0.1); 
                 border-radius: 10px; overflow: hidden; margin: 20px 0;">
                <!-- Background track -->
                <div style="position: absolute; top: 50%; left: 0; right: 0; height: 6px; 
                     background: linear-gradient(90deg, transparent, #00dbde, transparent); 
                     transform: translateY(-50%); opacity: 0.5;"></div>
                
                <!-- Moving train -->
                <div id="train-sim" style="position: absolute; top: 50%; left: 50%; 
                     font-size: 50px; transform: translate(-50%, -50%); 
                     filter: drop-shadow(0 0 10px #00dbde);">
                    🚅
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 12px;">
                <div>🚉 {IndianRailwaysData.STATIONS.get(train['current_station'], {}).get('name', train['current_station'])}</div>
                <div>→</div>
                <div>🚉 {IndianRailwaysData.STATIONS.get(train['next_station'], {}).get('name', train['next_station'])}</div>
            </div>
        </div>
        
        <style>
            @keyframes trainMove {{
                0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
                25% {{ transform: translate(-50%, -50%) rotate(2deg); }}
                50% {{ transform: translate(-50%, -50%) rotate(0deg); }}
                75% {{ transform: translate(-50%, -50%) rotate(-2deg); }}
                100% {{ transform: translate(-50%, -50%) rotate(0deg); }}
            }}
        </style>
        
        <script>
            // Make train move back and forth
            let trainSim = document.getElementById('train-sim');
            let position = 50;
            let direction = 1;
            
            setInterval(() => {{
                position += direction * 0.5;
                if (position > 90 || position < 10) direction *= -1;
                trainSim.style.left = position + '%';
            }}, 50);
        </script>
        """
        
        components.html(sim_html, height=250)
        
    else:
        st.info("👈 Select a train from the map or list to see detailed information")

with tab4:
    # ANALYTICS VIEW
    st.subheader("📈 Advanced Analytics")
    
    # AI Predictions
    st.markdown("### 🤖 AI-Powered Predictions")
    
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    
    with col_ai1:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 10px 0; color: #00dbde;">🎯 Arrival Time Prediction</h4>
            <div style="font-size: 14px; color: #cbd5e1;">
                <p><b>Accuracy:</b> 94.7% ✅</p>
                <p><b>Next Station ETA:</b> 15-20 min</p>
                <p><b>Confidence:</b> High</p>
                <p><b>Model:</b> Enhanced DQN</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ai2:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 10px 0; color: #00dbde;">⚠️ Delay Risk Analysis</h4>
            <div style="font-size: 14px; color: #cbd5e1;">
                <p><b>Current Risk:</b> Low ✅</p>
                <p><b>Affected Trains:</b> 42</p>
                <p><b>Avg Recovery Time:</b> 18.5 min</p>
                <p><b>Hotspots:</b> Northern Zone</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ai3:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 10px 0; color: #00dbde;">⚡ Efficiency Optimization</h4>
            <div style="font-size: 14px; color: #cbd5e1;">
                <p><b>Current Score:</b> 87/100 🏆</p>
                <p><b>Fuel Saved:</b> 22%</p>
                <p><b>Time Optimized:</b> 14.5 min</p>
                <p><b>CO2 Reduced:</b> 450 kg</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Historical Data Analysis
    st.markdown("---")
    st.markdown("### 📊 Historical Performance")
    
    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    historical_data = pd.DataFrame({
        'Date': dates,
        'Punctuality': 80 + np.random.randn(30).cumsum() * 0.5,
        'Avg Speed': 75 + np.random.randn(30).cumsum() * 0.3,
        'Delay Minutes': 15 + np.random.exponential(5, 30),
        'Train Count': 100 + np.random.randint(-10, 10, 30)
    })
    
    col_hist1, col_hist2 = st.columns(2)
    
    with col_hist1:
        fig_hist1 = px.line(
            historical_data, x='Date', y=['Punctuality', 'Avg Speed'],
            title='Punctuality & Speed Trends (30 days)'
        )
        st.plotly_chart(fig_hist1, use_container_width=True)
    
    with col_hist2:
        fig_hist2 = px.bar(
            historical_data, x='Date', y='Delay Minutes',
            title='Average Delay per Day (30 days)'
        )
        st.plotly_chart(fig_hist2, use_container_width=True)
    
    # Real-time Alerts
    st.markdown("---")
    st.markdown("### 🚨 Real-time Alerts & Notifications")
    
    alerts = [
        {"time": "14:30", "train": "12673", "type": "Delay", "message": "15 min delay due to signal failure", "severity": "Medium"},
        {"time": "14:25", "train": "12431", "type": "Speed", "message": "Reduced speed zone ahead", "severity": "Low"},
        {"time": "14:20", "train": "11013", "type": "Weather", "message": "Heavy rain affecting visibility", "severity": "High"},
        {"time": "14:15", "train": "12627", "type": "Track", "message": "Track maintenance in progress", "severity": "Medium"},
        {"time": "14:10", "train": "12007", "type": "Schedule", "message": "Rescheduled departure", "severity": "Low"}
    ]
    
    for alert in alerts:
        severity_color = {
            "High": "#ef4444",
            "Medium": "#f59e0b",
            "Low": "#3b82f6"
        }.get(alert["severity"], "#94a3b8")
        
        st.markdown(f"""
        <div class="info-card" style="border-left: 4px solid {severity_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: {severity_color}; font-weight: bold;">{alert['type']}</span>
                    <span style="color: #94a3b8; margin-left: 10px;">Train {alert['train']}</span>
                </div>
                <div style="color: #94a3b8; font-size: 12px;">{alert['time']}</div>
            </div>
            <div style="margin-top: 5px; color: #cbd5e1;">{alert['message']}</div>
        </div>
        """, unsafe_allow_html=True)

with tab5:
    # AI CONTROL VIEW
    st.subheader("🤖 AI Control Center")
    
    col_control1, col_control2 = st.columns(2)
    
    with col_control1:
        st.markdown("### 🎮 Manual Control Panel")
        
        # Speed control
        current_speed = st.slider("Target Speed (km/h):", 0, 150, 80)
        st.button("Apply Speed", use_container_width=True)
        
        # Signal control
        signal_status = st.selectbox("Signal Status:", ["Green", "Yellow", "Red"])
        st.button("Update Signal", use_container_width=True)
        
        # Emergency controls
        st.markdown("### 🚨 Emergency Controls")
        col_emerg1, col_emerg2 = st.columns(2)
        with col_emerg1:
            if st.button("Emergency Stop", type="secondary", use_container_width=True):
                st.warning("Emergency stop activated!")
        with col_emerg2:
            if st.button("Slow Down", type="secondary", use_container_width=True):
                st.info("Train slowing down...")
    
    with col_control2:
        st.markdown("### ⚙️ AI Configuration")
        
        # AI mode selection
        ai_mode = st.selectbox(
            "AI Operation Mode:",
            ["Fully Autonomous", "Human-Assisted", "Safety-First", "Efficiency-Optimized"]
        )
        
        # AI parameters
        aggression = st.slider("AI Aggression:", 0.0, 1.0, 0.7, 0.1)
        safety_margin = st.slider("Safety Margin (meters):", 50, 500, 200)
        energy_weight = st.slider("Energy Efficiency Weight:", 0.0, 1.0, 0.6, 0.1)
        
        if st.button("Apply AI Settings", use_container_width=True):
            st.success("AI configuration updated!")
    
    # AI Decision Log
    st.markdown("---")
    st.markdown("### 📝 AI Decision Log")
    
    decisions = [
        {"time": "14:35:22", "action": "Accelerate", "reason": "Clear track ahead", "confidence": 0.92},
        {"time": "14:34:15", "action": "Maintain", "reason": "Approaching station", "confidence": 0.88},
        {"time": "14:33:45", "action": "Decelerate", "reason": "Weather alert", "confidence": 0.95},
        {"time": "14:32:30", "action": "Accelerate", "reason": "Schedule recovery", "confidence": 0.85},
        {"time": "14:31:10", "action": "Maintain", "reason": "Optimal speed achieved", "confidence": 0.90}
    ]
    
    for decision in decisions:
        confidence_color = "#10b981" if decision["confidence"] > 0.9 else \
                         "#fbbf24" if decision["confidence"] > 0.8 else "#f59e0b"
        
        st.markdown(f"""
        <div class="info-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #00dbde; font-weight: bold;">{decision['action']}</span>
                    <span style="color: #94a3b8; margin-left: 10px;">{decision['reason']}</span>
                </div>
                <div>
                    <span style="color: {confidence_color}; font-weight: bold;">
                        {decision['confidence']*100:.0f}%
                    </span>
                    <span style="color: #94a3b8; margin-left: 10px; font-size: 12px;">
                        {decision['time']}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
footer = """
<div style="text-align: center; padding: 30px; color: #94a3b8; font-size: 12px;">
    <p>🚆 Indian Railways Live Tracker v3.0 | Powered by Enhanced DQN AI | © 2024</p>
    <p>Real-time GPS Tracking | Moving Block Signaling | Predictive Analytics | Energy Optimization</p>
    <p style="margin-top: 10px; font-size: 10px;">
        Note: This is a simulation for demonstration purposes. Real train positions may vary.
        Data updates every 2 seconds. Total active trains: {}
    </p>
</div>
""".format(len(simulator.trains))

st.markdown(footer, unsafe_allow_html=True)

# ========== AUTO REFRESH LOGIC ==========
if st.session_state.auto_refresh:
    refresh_seconds = {
        "5 seconds": 5,
        "10 seconds": 10,
        "30 seconds": 30,
        "1 minute": 60
    }.get(refresh_rate, 10)
    
    current_time = datetime.now()
    if (current_time - st.session_state.last_update).seconds >= refresh_seconds:
        st.session_state.last_update = current_time
        st.rerun()

# ========== JAVASCRIPT FOR TRAIN SELECTION ==========
st.markdown("""
<script>
    // Listen for train selection from map
    window.addEventListener('message', function(event) {
        if (event.data.type === 'selectTrain') {
            // Trigger Streamlit to update
            const data = {trainNo: event.data.trainNo};
            Streamlit.setComponentValue(data);
        }
    });
</script>
""", unsafe_allow_html=True)

# Handle train selection from JavaScript
if st.session_state.get('component_value'):
    train_no = st.session_state.component_value.get('trainNo')
    if train_no:
        selected_train = simulator.get_train_by_number(train_no)
        if selected_train:
            st.session_state.selected_train = selected_train
        st.session_state.component_value = None
