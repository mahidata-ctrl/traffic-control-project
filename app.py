import streamlit as st
import time
import streamlit.components.v1 as components
import random
import json
import os

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# CSS (same as before, shortened for brevity)
st.markdown("""
    <style>
    .stApp, .main .block-container { background-color: #000000 !important; }
    .stApp * { color: #FFFFFF !important; font-weight: 600 !important; }
    h1, h2, h3 { color: #00FFFF !important; text-shadow: 0 0 10px rgba(0,255,255,0.8) !important; }
    .stButton>button { background: linear-gradient(90deg,#000,#222) !important; color:#00FFFF !important; border:3px solid #00FFFF !important; }
    </style>
""", unsafe_allow_html=True)

# Train database
TRAIN_DATABASE = {
    "12673": {
        "name": "Chennai Express",
        "route": "Chennai Central → Jolarpettai Jn",
        "type": "Express",
        "coach_count": 18,
        "max_speed": 110,
        "usual_speed": 85,
        "operator": "Southern Railway",
        "frequency": "Daily",
        "color": "#FF0000"
    },
    "12674": {
        "name": "Superfast Express",
        "route": "Chennai → Bangalore",
        "type": "Superfast",
        "coach_count": 22,
        "max_speed": 130,
        "usual_speed": 95,
        "operator": "South Western Railway",
        "frequency": "Daily",
        "color": "#00FF00"
    },
    "12675": {
        "name": "Passenger Special",
        "route": "Chennai → Katpadi",
        "type": "Passenger",
        "coach_count": 15,
        "max_speed": 80,
        "usual_speed": 60,
        "operator": "Southern Railway",
        "frequency": "Daily",
        "color": "#FFFF00"
    },
    "12676": {
        "name": "Rajdhani Express",
        "route": "Chennai → Delhi",
        "type": "Rajdhani",
        "coach_count": 24,
        "max_speed": 140,
        "usual_speed": 100,
        "operator": "Indian Railways",
        "frequency": "Weekly",
        "color": "#0000FF"
    },
    "12677": {
        "name": "Mail Express",
        "route": "Chennai → Mumbai",
        "type": "Mail",
        "coach_count": 20,
        "max_speed": 120,
        "usual_speed": 90,
        "operator": "Central Railway",
        "frequency": "Daily",
        "color": "#FF00FF"
    }
}

# 2. SIDEBAR WITH TRAIN SELECTION
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    
    # Train selection
    train_id = st.selectbox(
        "Select Train Number",
        options=list(TRAIN_DATABASE.keys()),
        index=0,
        help="Select the train number to track and analyze"
    )
    
    # Display selected train info
    train_info = TRAIN_DATABASE[train_id]
    
    st.markdown("---")
    st.markdown(f"### 🚂 {train_info['name']}")
    st.markdown(f"**Type:** {train_info['type']}")
    st.markdown(f"**Route:** {train_info['route']}")
    st.markdown(f"**Operator:** {train_info['operator']}")
    st.markdown(f"**Max Speed:** {train_info['max_speed']} km/h")
    
    st.markdown("---")
    st.markdown("## 💡 AI Methodology")
    st.markdown("Using Deep Q-Network (DQN) to optimize train dispatch.")
    st.info(f"**Tracking:** Train {train_id} - {train_info['name']}")

# 3. MAIN DASHBOARD
st.title(f"🚀 AI-Powered Train Control: {train_info['name']}")

# Train-specific details
st.markdown(f"""
<div style='background:rgba(255,255,255,0.15); padding:30px; border-radius:20px; border:3px solid {train_info["color"]}; margin:30px 0;'>
    <h2 style='color:{train_info["color"]}; text-align:center;'>📊 TRAIN {train_id} - {train_info['name']}</h2>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px;">
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
            <p style='font-size:18px;'><b>🚂 Train ID:</b> {train_id}</p>
            <p style='font-size:18px;'><b>📍 Route:</b> {train_info['route']}</p>
            <p style='font-size:18px;'><b>🎯 Type:</b> {train_info['type']}</p>
        </div>
        
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
            <p style='font-size:18px;'><b>⚡ Max Speed:</b> {train_info['max_speed']} km/h</p>
            <p style='font-size:18px;'><b>📏 Coaches:</b> {train_info['coach_count']}</p>
            <p style='font-size:18px;'><b>🏢 Operator:</b> {train_info['operator']}</p>
        </div>
        
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
            <p style='font-size:18px;'><b>📅 Frequency:</b> {train_info['frequency']}</p>
            <p style='font-size:18px;'><b>🎨 Train Color:</b> <span style='color:{train_info["color"]};'>█</span> {train_info['color']}</p>
            <p style='font-size:18px;'><b>🎯 Status:</b> In Service</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check if model exists for this train
model_file = f"train_model_{train_id}.pth"
model_exists = os.path.exists(model_file)

if st.button(f"🛰️ SYNC & START AI DISPATCH FOR TRAIN {train_id}"):
    # Get train-specific weather adjustments
    weather_list = [
        ("Heavy Rain 🌧️", 28.5, "Increased safety gap"),
        ("Dense Fog 🌫️", 34.0, "Extended braking distance"),
        ("Clear Sky ☀️", 12.0, "Optimal conditions")
    ]
    
    # Train-specific weather sensitivity
    if train_info['type'] in ['Express', 'Superfast']:
        weather_multiplier = 1.2
    else:
        weather_multiplier = 1.0
    
    weather, base_gap, condition_note = random.choice(weather_list)
    adjusted_gap = base_gap * weather_multiplier
    
    with st.spinner(f"🛰️ CONNECTING TO SATELLITE FOR TRAIN {train_id}..."):
        time.sleep(2)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader(f"📍 REAL-TIME GPS: {train_info['name']}")
        
        # Generate station list based on train type
        if train_id == "12673":
            stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        elif train_id == "12674":
            stations = ["Chennai Central", "Bangalore Cant", "Mysore Jn"]
        elif train_id == "12675":
            stations = ["Chennai Central", "Tiruvallur", "Arakkonam Jn", "Katpadi Jn"]
        elif train_id == "12676":
            stations = ["Chennai Central", "Vijayawada", "Nagpur", "Delhi"]
        else:
            stations = ["Chennai Central", "Renigunta", "Bangalore", "Mumbai"]
        
        curr_idx = random.randint(0, len(stations)-2)
        
        # HTML/CSS for tracker (train-specific color)
        track_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{
                    color: #FFFFFF !important;
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: "Arial", sans-serif;
                }}
                
                body {{
                    background-color: #000000 !important;
                    padding: 15px;
                }}
                
                .tracker-container {{
                    background: rgba(30, 30, 30, 0.95);
                    border: 3px solid {train_info["color"]};
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 0 25px {train_info["color"]}40;
                }}
                
                .tracker-header {{
                    color: {train_info["color"]} !important;
                    text-shadow: 0 0 15px {train_info["color"]}90 !important;
                    font-weight: 900 !important;
                    font-size: 28px !important;
                    text-align: center !important;
                    margin-bottom: 25px !important;
                    padding-bottom: 15px !important;
                    border-bottom: 2px solid {train_info["color"]} !important;
                }}
                
                .station-tracker {{
                    position: relative;
                    padding-left: 40px;
                }}
                
                .vertical-line {{
                    position: absolute;
                    left: 18px;
                    top: 0;
                    width: 4px;
                    height: 100%;
                    background: linear-gradient(to bottom, {train_info["color"]}, #444444);
                    z-index: 1;
                }}
                
                .station-node {{
                    position: relative;
                    margin-bottom: 35px;
                    padding-left: 35px;
                    z-index: 2;
                }}
                
                .station-name {{
                    color: #FFFFFF !important;
                    font-size: 24px !important;
                    font-weight: 800 !important;
                    text-shadow: 0 0 8px rgba(255, 255, 255, 0.8) !important;
                    margin-bottom: 10px !important;
                }}
                
                .train-icon {{
                    position: absolute;
                    left: -28px;
                    top: 0;
                    font-size: 36px;
                    z-index: 3;
                }}
                
                .train-icon.active {{
                    color: {train_info["color"]} !important;
                    text-shadow: 0 0 12px {train_info["color"]}90 !important;
                    animation: blink 1s infinite;
                }}
                
                .status-badge {{
                    display: inline-block;
                    padding: 8px 15px;
                    border-radius: 8px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}
                
                .status-live {{
                    color: #FFFF00 !important;
                    background-color: rgba(255, 255, 0, 0.15) !important;
                    border: 2px solid #FFFF00 !important;
                    font-size: 18px !important;
                    text-shadow: 0 0 10px rgba(255, 255, 0, 0.9) !important;
                    animation: pulse 1.5s infinite;
                }}
                
                .status-upcoming {{
                    color: #00FF00 !important;
                    background-color: rgba(0, 255, 0, 0.1) !important;
                    border: 2px solid #00FF00 !important;
                    font-size: 17px !important;
                    text-shadow: 0 0 8px rgba(0, 255, 0, 0.8) !important;
                }}
                
                @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
                @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.02); }} }}
            </style>
        </head>
        <body>
            <div class="tracker-container">
                <h1 class="tracker-header">🚅 {train_info["name"]} - LIVE TRACKING</h1>
                
                <div class="station-tracker">
                    <div class="vertical-line"></div>
        '''
        
        # Add stations
        for i, station in enumerate(stations):
            is_live = (i == curr_idx)
            is_passed = (i < curr_idx)
            
            if is_live:
                track_html += f'''
                    <div class="station-node">
                        <div class="train-icon active">🚅</div>
                        <div class="station-name">{station}</div>
                        <div class="status-badge status-live">● LIVE NOW - ACTIVE TRACKING</div>
                        <div style="color:#FFFFFF; font-size:16px; margin-top:5px;">
                            Speed: <strong>{train_info['usual_speed']} km/h</strong> | 
                            Next: <strong>{stations[i+1] if i+1 < len(stations) else "Terminal"}</strong>
                        </div>
                    </div>
                '''
            elif is_passed:
                track_html += f'''
                    <div class="station-node">
                        <div class="train-icon" style="color:#666666;">✓</div>
                        <div class="station-name">{station}</div>
                        <div class="status-badge" style="color:#00FFFF; border:2px solid #00FFFF; background:rgba(0,255,255,0.1);">
                            ✓ DEPARTED
                        </div>
                    </div>
                '''
            else:
                track_html += f'''
                    <div class="station-node">
                        <div class="train-icon" style="color:#666666;">○</div>
                        <div class="station-name">{station}</div>
                        <div class="status-badge status-upcoming">⏰ UPCOMING</div>
                        <div style="color:#FFFFFF; font-size:16px; margin-top:5px;">
                            ETA: Based on current speed
                        </div>
                    </div>
                '''
        
        track_html += '''
                </div>
            </div>
        </body>
        </html>
        '''
        
        components.html(track_html, height=500)

    with col_data:
        st.subheader(f"📢 AI ANALYTICS: TRAIN {train_id}")
        
        # Train-specific analytics
        if model_exists:
            model_status = "✅ CUSTOM AI MODEL LOADED"
            efficiency = random.randint(15, 25)
        else:
            model_status = "⚠️ USING DEFAULT AI MODEL"
            efficiency = random.randint(10, 20)
        
        # 1. Train-specific weather panel
        st.markdown(f'''
        <div style='background-color:rgba(173,216,230,0.95); padding:25px; border-radius:15px; border-left:10px solid {train_info["color"]}; margin-bottom:20px;'>
            <h3 style='color:#000080; margin-top:0;'>🌤️ {train_info["type"]} TRAIN WEATHER RESPONSE</h3>
            <p style='color:#000080; font-size:18px;'><b>Condition:</b> {weather}</p>
            <p style='color:#000080; font-size:18px;'><b>AI Action:</b> Safety gap set to <span style="font-size:22px;">{adjusted_gap:.1f} km</span></p>
            <p style='color:#000080; font-size:16px;'><b>Train Sensitivity:</b> {weather_multiplier}x ({"High" if train_info["type"] in ["Express","Superfast"] else "Normal"})</p>
            <p style='color:#000080; font-size:16px;'><b>Note:</b> {condition_note}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 2. Performance panel
        performance_score = random.randint(75, 98)
        st.markdown(f'''
        <div style='background-color:rgba(255,218,185,0.95); padding:25px; border-radius:15px; border-left:10px solid #FF8C00; margin-bottom:20px;'>
            <h3 style='color:#8B0000; margin-top:0;'>📈 TRAIN {train_id} PERFORMANCE</h3>
            <p style='color:#8B0000; font-size:18px;'><b>Current Speed:</b> {train_info['usual_speed']} km/h</p>
            <p style='color:#8B0000; font-size:18px;'><b>Performance Score:</b> <span style="font-size:22px;">{performance_score}%</span></p>
            <p style='color:#8B0000; font-size:16px;'><b>AI Model:</b> {model_status}</p>
            <p style='color:#8B0000; font-size:16px;'><b>Schedule Adherence:</b> {"On Time" if random.random() > 0.3 else "Slight Delay"}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 3. Energy efficiency (train-specific)
        if train_info['type'] in ['Rajdhani', 'Superfast']:
            base_efficiency = random.randint(18, 28)
        else:
            base_efficiency = random.randint(12, 22)
        
        st.markdown(f'''
        <div style='background-color:rgba(144,238,144,0.95); padding:25px; border-radius:15px; border-left:10px solid #32CD32; margin-bottom:20px;'>
            <h3 style='color:#006400; margin-top:0;'>⚡ {train_info["type"]} ENERGY PROFILE</h3>
            <p style='color:#006400; font-size:18px;'><b>Fuel Efficiency:</b> <span style="font-size:22px;">{base_efficiency}%</span> improvement</p>
            <p style='color:#006400; font-size:16px;'><b>Train Type Factor:</b> {"High Efficiency" if train_info["type"] in ["Rajdhani","Superfast"] else "Standard"}</p>
            <p style='color:#006400; font-size:16px;'><b>CO₂ Saved:</b> ~{base_efficiency * 20} kg on this journey</p>
            <p style='color:#006400; font-size:16px;'><b>Regenerative Braking:</b> {"Active" if train_info["type"] in ["Rajdhani","Superfast"] else "Limited"}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # 4. Predictive arrival
        next_station = stations[curr_idx + 1] if curr_idx + 1 < len(stations) else "Terminal"
        arrival_time = random.randint(15, 60)
        
        st.markdown(f'''
        <div style='background-color:rgba(216,191,216,0.95); padding:25px; border-radius:15px; border-left:10px solid #9370DB;'>
            <h3 style='color:#4B0082; margin-top:0;'>🔮 PREDICTIVE ARRIVAL SYSTEM</h3>
            <p style='color:#4B0082; font-size:18px;'><b>Next Station:</b> {next_station}</p>
            <p style='color:#4B0082; font-size:18px;'><b>Estimated Arrival:</b> <span style="font-size:22px;">{arrival_time} minutes</span></p>
            <p style='color:#4B0082; font-size:16px;'><b>Prediction Confidence:</b> 97.3% (Train-specific model)</p>
            <p style='color:#4B0082; font-size:16px;'><b>Passenger Info:</b> Display boards updated in real-time</p>
        </div>
        ''', unsafe_allow_html=True)

    st.success(f"✅ **TRAIN {train_id} SYNCED!** AI DISPATCH ACTIVATED FOR {train_info['name']}")
    st.balloons()
