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
import torch
from train import TrainAgent, DQNetwork
from rail_env import TrainTrafficEnv

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="🚆 AI Train Traffic Control System",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    
    /* Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #38bdf8;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8, #1e40af);
        transform: scale(1.05);
    }
    
    /* GPS Tracking Container */
    .gps-container {
        background: rgba(15, 23, 42, 0.9);
        border-radius: 15px;
        padding: 20px;
        border: 2px solid #334155;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Live Indicator */
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #ef4444;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Progress Bar */
    .progress-container {
        height: 8px;
        background-color: #334155;
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Train Icon Animation */
    .train-moving {
        animation: moveTrain 2s linear infinite;
    }
    @keyframes moveTrain {
        0% { transform: translateX(0); }
        100% { transform: translateX(20px); }
    }
</style>
""", unsafe_allow_html=True)

# 2. SIDEBAR CONFIGURATION
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972544.png", width=80)
    st.title("🚆 Control Panel")
    
    st.markdown("---")
    
    # Train Selection
    st.subheader("🛰️ GPS Configuration")
    train_id = st.selectbox(
        "Select Train",
        ["12673 - Cheran SF Exp", "12671 - Nilgiri Exp", "12675 - Kovai Exp", "22651 - Rajdhani Exp"]
    )
    
    # Route Selection
    route = st.selectbox(
        "Select Route",
        ["Chennai → Salem", "Chennai → Coimbatore", "Chennai → Bangalore", "Custom Route"]
    )
    
    # AI Mode Selection
    ai_mode = st.radio(
        "🤖 AI Operation Mode",
        ["Fully Autonomous", "Human-Assisted", "Training Mode", "Safety-First"]
    )
    
    # Simulation Speed
    sim_speed = st.slider("Simulation Speed", 1, 10, 3)
    
    # Weather Conditions
    weather = st.select_slider(
        "Weather Conditions",
        options=["Clear ☀️", "Light Rain 🌦️", "Heavy Rain 🌧️", "Fog 🌫️", "Storm ⛈️"],
        value="Clear ☀️"
    )
    
    # Track Condition
    track_condition = st.select_slider(
        "Track Condition",
        options=["Excellent 🟢", "Good 🟡", "Fair 🟠", "Poor 🔴", "Maintenance 🔧"],
        value="Excellent 🟢"
    )
    
    st.markdown("---")
    
    # AI Status
    st.subheader("🧠 AI Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Learning Rate", "0.001")
    with col2:
        st.metric("Exploration", "12%")
    
    # System Info
    st.markdown("---")
    st.subheader("📊 System Info")
    st.info("""
    **AI Model**: Deep Q-Network (DQN)
    **Training Episodes**: 500
    **Safety Protocol**: Moving Block Signaling
    **Update Frequency**: 100ms
    """)

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")
st.markdown("---")

# Initialize session state for simulation
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'current_station' not in st.session_state:
    st.session_state.current_station = 0
if 'train_data' not in st.session_state:
    st.session_state.train_data = []

# 4. REAL-TIME METRICS
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Current Speed", "85 km/h", "↑ 5.2%")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Distance to Next", "2.8 km", "Safe ✅")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Energy Saved", "18.7%", "↑ 3.1%")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("On-Time Performance", "96.3%", "↑ 1.8%")
    st.markdown('</div>', unsafe_allow_html=True)

# 5. GPS TRACKING VISUALIZATION
st.markdown("---")
st.subheader("📍 Live GPS Tracking & Route Visualization")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🌍 Map View", "📈 Track View", "🚆 3D View", "📊 Analytics"])

with tab1:
    # Interactive Folium Map
    col_map, col_info = st.columns([2, 1])
    
    with col_map:
        # Create map centered on India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='CartoDB dark_matter')
        
        # Define route coordinates (Chennai to Salem)
        route_coords = [
            [13.0827, 80.2707],  # Chennai
            [13.0846, 79.6725],  # Arakkonam
            [12.9702, 79.1590],  # Katpadi
            [12.5667, 78.5667],  # Jolarpettai
            [11.6643, 78.1460]   # Salem
        ]
        
        # Add route line
        folium.PolyLine(
            route_coords,
            weight=4,
            color='#3b82f6',
            opacity=0.8,
            tooltip='Train Route'
        ).add_to(m)
        
        # Add stations
        station_names = ['Chennai Central', 'Arakkonam Jn', 'Katpadi Jn', 'Jolarpettai Jn', 'Salem Jn']
        for idx, (coord, name) in enumerate(zip(route_coords, station_names)):
            folium.Marker(
                coord,
                popup=f"""
                <div style='font-family: Arial; padding: 10px;'>
                    <h4 style='color: #3b82f6; margin: 0;'>{name}</h4>
                    <p style='margin: 5px 0;'><b>Status:</b> {'Arrived ✅' if idx <= st.session_state.current_station else 'Pending ⏳'}</p>
                    <p style='margin: 5px 0;'><b>Platform:</b> PF {idx+1}</p>
                </div>
                """,
                tooltip=name,
                icon=folium.Icon(
                    color='green' if idx <= st.session_state.current_station else 'gray',
                    icon='train',
                    prefix='fa'
                )
            ).add_to(m)
        
        # Add moving train marker
        if st.session_state.current_station < len(route_coords) - 1:
            # Interpolate position between stations
            progress = st.session_state.get('progress', 0)
            start_coord = route_coords[st.session_state.current_station]
            end_coord = route_coords[st.session_state.current_station + 1]
            
            lat = start_coord[0] + (end_coord[0] - start_coord[0]) * progress
            lng = start_coord[1] + (end_coord[1] - start_coord[1]) * progress
            
            folium.Marker(
                [lat, lng],
                popup=f"""
                <div style='font-family: Arial; padding: 10px;'>
                    <h4 style='color: #ef4444; margin: 0;'>🚅 {train_id}</h4>
                    <p style='margin: 5px 0;'><b>Speed:</b> 85 km/h</p>
                    <p style='margin: 5px 0;'><b>Next Station:</b> {station_names[st.session_state.current_station + 1]}</p>
                    <p style='margin: 5px 0;'><b>ETA:</b> {random.randint(10, 30)} min</p>
                </div>
                """,
                tooltip=f"Train: {train_id}",
                icon=folium.DivIcon(
                    html=f"""
                    <div style='
                        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 20px;
                        border: 3px solid white;
                        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
                        animation: pulse 1.5s infinite;
                    '>
                        🚅
                    </div>
                    """
                )
            ).add_to(m)
        
        # Display map
        folium_static(m, width=800, height=500)
    
    with col_info:
        st.markdown('<div class="gps-container">', unsafe_allow_html=True)
        st.subheader("📡 GPS Information")
        
        # GPS Status
        st.markdown(f"""
        <div style='margin-bottom: 20px;'>
            <span class='live-indicator'></span>
            <span style='font-weight: bold; color: #ef4444;'>LIVE TRACKING ACTIVE</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Current Position
        st.metric("Latitude", "12.3456° N")
        st.metric("Longitude", "78.9012° E")
        st.metric("Altitude", "245 m")
        
        # GPS Accuracy
        st.progress(0.92)
        st.caption("GPS Accuracy: 92%")
        
        # Satellite Info
        st.markdown("### 🛰️ Satellites in View")
        col_sat1, col_sat2 = st.columns(2)
        with col_sat1:
            st.metric("GPS", "8", "+2")
        with col_sat2:
            st.metric("GLONASS", "6", "+1")
        
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # Enhanced Vertical Track View
    st.markdown('<div class="gps-container">', unsafe_allow_html=True)
    
    railway_data = [
        {"name": "Chennai Central", "arr": "--:--", "dep": "22:10", "pf": "PF 10", "dist": "0 km", "delay": "0 min"},
        {"name": "Arakkonam Jn", "arr": "23:08", "dep": "23:10", "pf": "PF 3", "dist": "69 km", "delay": "2 min"},
        {"name": "Katpadi Jn", "arr": "23:58", "dep": "00:01", "pf": "PF 1", "dist": "130 km", "delay": "1 min"},
        {"name": "Jolarpettai Jn", "arr": "01:23", "dep": "01:25", "pf": "PF 2", "dist": "214 km", "delay": "0 min"},
        {"name": "Salem Jn", "arr": "02:57", "dep": "03:00", "pf": "PF 4", "dist": "334 km", "delay": "0 min"}
    ]
    
    # Create vertical track visualization
    track_html = """
    <div style='position: relative; padding-left: 60px; margin: 20px 0; min-height: 600px;'>
        <!-- Main vertical track line -->
        <div style='
            position: absolute;
            left: 70px;
            top: 0;
            bottom: 0;
            width: 6px;
            background: linear-gradient(to bottom, #334155, #64748b);
            border-radius: 3px;
            z-index: 1;
        '></div>
        
        <!-- Progress line -->
        <div id='progress-line' style='
            position: absolute;
            left: 70px;
            top: 0;
            width: 6px;
            background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
            border-radius: 3px;
            z-index: 2;
            transition: height 1s ease;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
        '></div>
        
        <!-- Moving train -->
        <div id='train-marker' style='
            position: absolute;
            left: 55px;
            font-size: 40px;
            z-index: 10;
            transition: top 1s ease;
            filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.8));
        '>🚅</div>
    """
    
    for i, station in enumerate(railway_data):
        is_active = (i <= st.session_state.current_station)
        is_current = (i == st.session_state.current_station)
        
        # Calculate position
        top_pos = i * 120
        
        track_html += f"""
        <div style='position: relative; margin-bottom: 120px;'>
            <!-- Station dot -->
            <div style='
                position: absolute;
                left: 62px;
                top: {top_pos + 20}px;
                width: 24px;
                height: 24px;
                background-color: {'#10b981' if is_active else '#64748b'};
                border-radius: 50%;
                border: 4px solid #0f172a;
                z-index: 3;
                box-shadow: 0 0 15px {'rgba(16, 185, 129, 0.5)' if is_active else 'none'};
                transition: all 0.5s ease;
            '></div>
            
            <!-- Station info card -->
            <div style='
                margin-left: 100px;
                background: {'rgba(59, 130, 246, 0.1)' if is_current else 'rgba(255, 255, 255, 0.05)'};
                padding: 15px;
                border-radius: 10px;
                border-left: 5px solid {'#ef4444' if is_current else ('#10b981' if is_active else '#64748b')};
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            '>
                <div style='
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                '>
                    <h3 style='
                        margin: 0;
                        color: {'#ef4444' if is_current else ('#ffffff' if is_active else '#94a3b8')};
                        font-weight: 700;
                    '>
                        {station['name']}
                        {'<span style="color: #ef4444; font-size: 14px; margin-left: 10px;">● LIVE</span>' if is_current else ''}
                    </h3>
                    <span style='
                        background: {'#ef4444' if is_current else ('#10b981' if is_active else '#64748b')};
                        color: white;
                        padding: 4px 12px;
                        border-radius: 20px;
                        font-size: 12px;
                        font-weight: 600;
                    '>
                        {station['pf']}
                    </span>
                </div>
                
                <div style='
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                    color: {'#cbd5e1' if is_active else '#64748b'};
                '>
                    <div>
                        <div style='font-size: 11px; color: #94a3b8;'>ARRIVAL</div>
                        <div style='font-size: 16px; font-weight: 600;'>{station['arr']}</div>
                    </div>
                    <div>
                        <div style='font-size: 11px; color: #94a3b8;'>DEPARTURE</div>
                        <div style='font-size: 16px; font-weight: 600;'>{station['dep']}</div>
                    </div>
                    <div>
                        <div style='font-size: 11px; color: #94a3b8;'>DISTANCE</div>
                        <div style='font-size: 16px; font-weight: 600;'>{station['dist']}</div>
                    </div>
                </div>
                
                {'<div style="margin-top: 10px; font-size: 13px; color: #f59e0b;">Delay: ' + station['delay'] + '</div>' if station['delay'] != "0 min" else ''}
            </div>
        </div>
        """
    
    track_html += "</div>"
    
    # Add JavaScript for animation
    track_html += """
    <script>
        function updateTrainPosition(currentStation) {
            const progressLine = document.getElementById('progress-line');
            const trainMarker = document.getElementById('train-marker');
            
            // Calculate positions (120px per station)
            const progressHeight = currentStation * 120 + 40;
            const trainTop = currentStation * 120 + 10;
            
            progressLine.style.height = progressHeight + 'px';
            trainMarker.style.top = trainTop + 'px';
        }
        
        // Initialize with current station
        updateTrainPosition(""" + str(st.session_state.current_station) + """);
    </script>
    """
    
    components.html(track_html, height=700)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    # 3D Visualization using Plotly
    st.subheader("🚆 3D Route Visualization")
    
    # Create 3D route data
    x = np.linspace(0, 334, 100)
    y = np.sin(x/50) * 20
    z = np.cos(x/100) * 50
    
    fig = go.Figure(data=[
        go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(width=8, color='#3b82f6'),
            name='Track'
        ),
        go.Scatter3d(
            x=[x[st.session_state.current_station * 20]],
            y=[y[st.session_state.current_station * 20]],
            z=[z[st.session_state.current_station * 20]],
            mode='markers',
            marker=dict(size=15, color='#ef4444'),
            name='Train'
        )
    ])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Distance (km)',
            yaxis_title='Lateral Position',
            zaxis_title='Elevation',
            bgcolor='rgba(0,0,0,0)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    # Analytics Dashboard
    col_anal1, col_anal2 = st.columns(2)
    
    with col_anal1:
        st.subheader("📈 Performance Metrics")
        
        # Create sample data
        metrics_data = pd.DataFrame({
            'Time': pd.date_range('2024-01-01', periods=24, freq='H'),
            'Speed': np.random.normal(80, 10, 24),
            'Energy': np.random.normal(85, 5, 24),
            'Safety': np.random.normal(95, 2, 24)
        })
        
        st.line_chart(metrics_data.set_index('Time'))
    
    with col_anal2:
        st.subheader("🎯 AI Decision Log")
        
        # Sample AI decisions
        decisions = pd.DataFrame({
            'Time': ['22:15', '22:30', '22:45', '23:00'],
            'Action': ['Accelerate', 'Maintain', 'Decelerate', 'Maintain'],
            'Reason': ['Clear track ahead', 'Approaching station', 'Weather alert', 'Optimal speed'],
            'Reward': [+2.5, +1.0, -0.5, +1.5]
        })
        
        st.dataframe(decisions, use_container_width=True)

# 6. AI ANALYTICS PANEL
st.markdown("---")
st.subheader("🤖 AI Analytics Feed")

col_ai1, col_ai2, col_ai3 = st.columns(3)

with col_ai1:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    '>
        <h4 style='color: white; margin-top: 0;'>🌤️ Weather Intelligence</h4>
        <p style='color: #dbeafe; font-size: 14px;'>
            <b>Current:</b> """ + weather + """<br>
            <b>AI Action:</b> Safety gap adjusted to 28.5 km<br>
            <b>Speed Limit:</b> 90 km/h (-10% for safety)
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #ea580c, #f97316);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.3);
    '>
        <h4 style='color: white; margin-top: 0;'>🔧 Predictive Maintenance</h4>
        <p style='color: #ffedd5; font-size: 14px;'>
            <b>Engine Health:</b> 98% ✅<br>
            <b>Next Service:</b> 1,250 km remaining<br>
            <b>Components:</b> All systems optimal
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ai3:
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #047857, #10b981);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
    '>
        <h4 style='color: white; margin-top: 0;'>⚡ Energy Optimization</h4>
        <p style='color: #d1fae5; font-size: 14px;'>
            <b>Fuel Saved:</b> 22% via AI Throttle<br>
            <b>Regen Braking:</b> Active ✅<br>
            <b>CO2 Reduced:</b> 450 kg/trip
        </p>
    </div>
    """, unsafe_allow_html=True)

# 7. SIMULATION CONTROLS
st.markdown("---")
st.subheader("🎮 Simulation Controls")

col_control1, col_control2, col_control3, col_control4 = st.columns(4)

with col_control1:
    if st.button("🚀 Start AI Simulation", type="primary", use_container_width=True):
        st.session_state.simulation_running = True
        st.success("AI Simulation Started!")

with col_control2:
    if st.button("⏸️ Pause Simulation", use_container_width=True):
        st.session_state.simulation_running = False
        st.warning("Simulation Paused")

with col_control3:
    if st.button("🔁 Reset Simulation", use_container_width=True):
        st.session_state.current_station = 0
        st.session_state.simulation_running = False
        st.info("Simulation Reset")

with col_control4:
    if st.button("📥 Export Data", use_container_width=True):
        st.success("Data exported successfully!")

# 8. REAL-TIME SIMULATION
if st.session_state.simulation_running:
    st.markdown("---")
    st.subheader("🔄 Live Simulation Progress")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulation loop
    for i in range(5):  # Simulate 5 stations
        if not st.session_state.simulation_running:
            break
            
        # Update station
        st.session_state.current_station = i
        progress = (i + 1) / 5
        
        # Update progress
        progress_bar.progress(progress)
        status_text.text(f"🚉 Arriving at {railway_data[i]['name']}...")
        
        # Add train data point
        st.session_state.train_data.append({
            'timestamp': datetime.now(),
            'station': railway_data[i]['name'],
            'speed': random.randint(75, 95),
            'energy': random.randint(80, 95)
        })
        
        # Wait for next step
        time.sleep(2 / sim_speed)
    
    if st.session_state.current_station >= 4:
        st.balloons()
        st.success("🎉 Simulation Complete: Optimal Section Throughput Achieved!")
        st.session_state.simulation_running = False

# 9. FOOTER
st.markdown("---")
footer = """
<div style='
    text-align: center;
    padding: 20px;
    color: #94a3b8;
    font-size: 12px;
'>
    <p>🚆 AI Train Traffic Control System v2.0 | Powered by Deep Q-Learning | © 2024</p>
    <p>Real-time GPS Tracking | Moving Block Signaling | Predictive Analytics</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
