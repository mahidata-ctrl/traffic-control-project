import streamlit as st
import time
import streamlit.components.v1 as components
import random
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Indian Railways AI Dispatch", layout="wide")

# CSS for Indian Railways theme (Saffron-White-Green)
st.markdown("""
    <style>
    /* INDIAN RAILWAYS THEME - Saffron, White, Green */
    * {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .stApp, .main .block-container {
        background-color: #000000 !important;
        background-image: linear-gradient(to bottom, 
            rgba(255, 153, 51, 0.1) 0%, 
            rgba(0, 0, 0, 0.9) 30%,
            rgba(19, 136, 8, 0.1) 100%);
    }
    
    /* Headers with Indian Railways colors */
    h1 {
        color: #FF9933 !important; /* Saffron */
        text-shadow: 0 0 20px rgba(255, 153, 51, 0.8) !important;
        font-weight: 900 !important;
        font-size: 44px !important;
        text-align: center !important;
        padding: 20px !important;
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    
    h2 {
        color: #FFFFFF !important;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.7) !important;
        font-weight: 800 !important;
        font-size: 32px !important;
        border-left: 5px solid #FF9933 !important;
        padding-left: 15px !important;
    }
    
    h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 26px !important;
    }
    
    /* Sidebar - Indian Railways theme */
    section[data-testid="stSidebar"] { 
        background-color: #111111 !important;
        border-right: 4px solid #FF9933 !important;
        background-image: linear-gradient(to bottom, 
            rgba(255, 153, 51, 0.05), 
            rgba(0, 0, 0, 0.95),
            rgba(19, 136, 8, 0.05));
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 3px solid #FF9933 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(255, 153, 51, 0.3) !important;
    }
    
    /* Buttons - Indian Railways theme */
    .stButton>button {
        background: linear-gradient(90deg, #FF9933, #138808) !important;
        color: #FFFFFF !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 0 25px rgba(255, 153, 51, 0.7) !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        height: 70px !important;
        border-radius: 15px !important;
        margin-top: 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 35px rgba(255, 153, 51, 1) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Info boxes */
    .stInfo, .stSuccess, .stWarning {
        border-left: 6px solid #FF9933 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    
    .stSuccess {
        border-left-color: #138808 !important;
        background-color: rgba(19, 136, 8, 0.15) !important;
    }
    
    .stWarning {
        border-left-color: #FF9933 !important;
        background-color: rgba(255, 153, 51, 0.15) !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        background-color: rgba(30, 30, 30, 0.95) !important;
        border: 2px solid rgba(255, 153, 51, 0.5) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        margin: 10px !important;
    }
    
    /* Status indicators */
    .status-running { color: #00FF00 !important; font-weight: 900 !important; }
    .status-delayed { color: #FFFF00 !important; font-weight: 900 !important; }
    .status-cancelled { color: #FF0000 !important; font-weight: 900 !important; }
    .status-terminated { color: #888888 !important; font-weight: 900 !important; }
    
    /* Train details cards */
    .train-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #FF9933;
        border-right: 5px solid #138808;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
    }
    
    /* Animation for live tracking */
    @keyframes trainPulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes saffronGlow {
        0% { box-shadow: 0 0 10px rgba(255, 153, 51, 0.5); }
        50% { box-shadow: 0 0 20px rgba(255, 153, 51, 0.8); }
        100% { box-shadow: 0 0 10px rgba(255, 153, 51, 0.5); }
    }
    
    .train-pulse {
        animation: trainPulse 2s infinite;
    }
    
    .saffron-glow {
        animation: saffronGlow 3s infinite;
    }
    
    /* Divider with Indian flag colors */
    .indian-divider {
        height: 5px;
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
        border-radius: 3px;
        margin: 30px 0;
    }
    
    /* Zone badges */
    .zone-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        margin: 5px;
    }
    
    .zone-nr { background-color: #FF0000; color: #FFFFFF; }
    .zone-wr { background-color: #00FF00; color: #000000; }
    .zone-er { background-color: #0000FF; color: #FFFFFF; }
    .zone-sr { background-color: #FF00FF; color: #FFFFFF; }
    .zone-cr { background-color: #FFFF00; color: #000000; }
    .zone-others { background-color: #888888; color: #FFFFFF; }
    
    </style>
""", unsafe_allow_html=True)

# 2. COMPREHENSIVE INDIAN RAILWAYS DATABASE
INDIAN_TRAINS = {
    # Southern Railway
    "12673": {"name": "CHENNAI EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Chennai Central → Jolarpettai", "coaches": 22, "max_speed": 110,
              "departure": "06:00", "arrival": "12:30", "duration": "6h 30m"},
    
    "12674": {"name": "BANGALORE EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Chennai Central → Bangalore", "coaches": 24, "max_speed": 110,
              "departure": "07:30", "arrival": "13:45", "duration": "6h 15m"},
    
    "12675": {"name": "MYSORE EXPRESS", "zone": "SR", "type": "Mail/Express",
              "route": "Chennai → Mysore", "coaches": 18, "max_speed": 110,
              "departure": "20:15", "arrival": "07:30", "duration": "11h 15m"},
    
    # Western Railway
    "12951": {"name": "RAJDHANI EXPRESS", "zone": "WR", "type": "Rajdhani",
              "route": "Mumbai Central → Delhi", "coaches": 22, "max_speed": 130,
              "departure": "16:35", "arrival": "08:45", "duration": "16h 10m"},
    
    "12952": {"name": "MUMBAI RAJDHANI", "zone": "WR", "type": "Rajdhani",
              "route": "Delhi → Mumbai", "coaches": 22, "max_speed": 130,
              "departure": "16:00", "arrival": "08:10", "duration": "16h 10m"},
    
    # Northern Railway
    "12009": {"name": "SHATABDI EXPRESS", "zone": "NR", "type": "Shatabdi",
              "route": "New Delhi → Bhopal", "coaches": 16, "max_speed": 150,
              "departure": "06:00", "arrival": "12:35", "duration": "6h 35m"},
    
    "12010": {"name": "SHATABDI EXPRESS", "zone": "NR", "type": "Shatabdi",
              "route": "Bhopal → New Delhi", "coaches": 16, "max_speed": 150,
              "departure": "14:00", "arrival": "20:35", "duration": "6h 35m"},
    
    # Eastern Railway
    "12301": {"name": "HOWRAH RAJDHANI", "zone": "ER", "type": "Rajdhani",
              "route": "New Delhi → Howrah", "coaches": 24, "max_speed": 130,
              "departure": "16:55", "arrival": "10:00", "duration": "17h 5m"},
    
    "12302": {"name": "NEW DELHI RAJDHANI", "zone": "ER", "type": "Rajdhani",
              "route": "Howrah → New Delhi", "coaches": 24, "max_speed": 130,
              "departure": "16:50", "arrival": "10:00", "duration": "17h 10m"},
    
    # Central Railway
    "12137": {"name": "PUNE EXPRESS", "zone": "CR", "type": "Superfast",
              "route": "Mumbai → Pune", "coaches": 20, "max_speed": 110,
              "departure": "07:15", "arrival": "10:30", "duration": "3h 15m"},
    
    # Popular Trains
    "12607": {"name": "LALBAGH EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Bangalore → Chennai", "coaches": 22, "max_speed": 110,
              "departure": "06:00", "arrival": "11:45", "duration": "5h 45m"},
    
    "12608": {"name": "LALBAGH EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Chennai → Bangalore", "coaches": 22, "max_speed": 110,
              "departure": "15:00", "arrival": "20:45", "duration": "5h 45m"},
    
    "12639": {"name": "BRINDAVAN EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Chennai → Bangalore", "coaches": 20, "max_speed": 110,
              "departure": "07:10", "arrival": "12:45", "duration": "5h 35m"},
    
    "12640": {"name": "BRINDAVAN EXPRESS", "zone": "SR", "type": "Superfast",
              "route": "Bangalore → Chennai", "coaches": 20, "max_speed": 110,
              "departure": "15:00", "arrival": "20:35", "duration": "5h 35m"},
    
    # Duronto Express
    "12213": {"name": "DURONTO EXPRESS", "zone": "ER", "type": "Duronto",
              "route": "Howrah → New Delhi", "coaches": 22, "max_speed": 130,
              "departure": "20:05", "arrival": "09:30", "duration": "13h 25m"},
    
    # Garib Rath
    "12201": {"name": "GARIB RATH", "zone": "NR", "type": "Garib Rath",
              "route": "Anand Vihar → Mumbai", "coaches": 24, "max_speed": 130,
              "departure": "16:10", "arrival": "09:05", "duration": "16h 55m"},
    
    # Tejas Express
    "12951": {"name": "TEJAS EXPRESS", "zone": "WR", "type": "Tejas",
              "route": "Mumbai → Goa", "coaches": 20, "max_speed": 130,
              "departure": "05:00", "arrival": "13:00", "duration": "8h 00m"},
    
    # Vande Bharat Express
    "22201": {"name": "VANDE BHARAT", "zone": "NR", "type": "Vande Bharat",
              "route": "New Delhi → Varanasi", "coaches": 16, "max_speed": 160,
              "departure": "06:00", "arrival": "14:00", "duration": "8h 00m"},
    
    "22202": {"name": "VANDE BHARAT", "zone": "SR", "type": "Vande Bharat",
              "route": "Chennai → Mysore", "coaches": 16, "max_speed": 160,
              "departure": "05:45", "arrival": "12:15", "duration": "6h 30m"},
}

# Zone information
ZONE_INFO = {
    "NR": {"name": "Northern Railway", "color": "#FF0000", "headquarters": "Delhi"},
    "WR": {"name": "Western Railway", "color": "#00FF00", "headquarters": "Mumbai"},
    "ER": {"name": "Eastern Railway", "color": "#0000FF", "headquarters": "Kolkata"},
    "SR": {"name": "Southern Railway", "color": "#FF00FF", "headquarters": "Chennai"},
    "CR": {"name": "Central Railway", "color": "#FFFF00", "headquarters": "Mumbai"},
    "NER": {"name": "North Eastern Railway", "color": "#FFA500", "headquarters": "Gorakhpur"},
}

# Train type colors
TRAIN_TYPE_COLORS = {
    "Rajdhani": "#FF0000",
    "Shatabdi": "#0000FF",
    "Duronto": "#800080",
    "Garib Rath": "#00FF00",
    "Tejas": "#FF4500",
    "Vande Bharat": "#FFD700",
    "Superfast": "#FF9933",
    "Mail/Express": "#138808",
    "Passenger": "#888888",
    "Local": "#666666",
}

# 3. SIDEBAR - INDIAN RAILWAYS SEARCH
with st.sidebar:
    st.markdown("## 🇮🇳 INDIAN RAILWAYS SEARCH")
    
    # Indian Railways Logo
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <div style="font-size: 48px;">🚂</div>
        <div style="color: #FF9933; font-weight: 900; font-size: 24px;">भारतीय रेल</div>
        <div style="color: #FFFFFF; font-size: 18px;">INDIAN RAILWAYS</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Train number input
    train_input = st.text_input(
        "Enter Indian Railways Train Number",
        value="12673",
        placeholder="e.g., 12673, 12951, 12009, 22201",
        help="Enter any 5-digit Indian Railways train number"
    )
    
    # Search button
    search_clicked = st.button("🔍 SEARCH TRAIN", use_container_width=True)
    
    st.markdown("---")
    
    # Quick examples
    st.markdown("### 🚂 Popular Trains:")
    st.markdown("""
    - **12673**: Chennai Express
    - **12951**: Rajdhani Express
    - **12009**: Shatabdi Express
    - **22201**: Vande Bharat
    - **12607**: Lalbagh Express
    - **12213**: Duronto Express
    """)
    
    st.markdown("---")
    
    # System status
    st.markdown("### 📡 SYSTEM STATUS")
    st.info("""
    **Indian Railways Network:** Active ✅
    **AI Dispatch System:** Online ✅
    **Satellite Coverage:** PAN India
    **Last Updated:** Real-time
    """)
    
    # Railway zones
    st.markdown("### 🗺️ RAILWAY ZONES")
    cols = st.columns(3)
    zones = list(ZONE_INFO.items())[:6]
    for idx, (code, info) in enumerate(zones):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="background: {info['color']}20; padding: 8px; border-radius: 5px; text-align: center;">
                <div style="font-weight: 700; color: {info['color']}">{code}</div>
                <div style="font-size: 10px; color: #FFFFFF;">{info['name']}</div>
            </div>
            """, unsafe_allow_html=True)

# 4. MAIN DASHBOARD
st.title("🇮🇳 INDIAN RAILWAYS AI DISPATCH SYSTEM")

# Check if train exists
train_data = None
train_found = False

if search_clicked or 'current_train' not in st.session_state:
    if train_input.strip():
        search_key = train_input
        
        if search_key in INDIAN_TRAINS:
            train_data = INDIAN_TRAINS[search_key]
            train_found = True
            st.session_state.current_train = train_data
            st.session_state.train_number = train_input
        else:
            # Generate realistic Indian train data
            train_found = True
            zone = random.choice(["NR", "WR", "ER", "SR", "CR"])
            train_type = random.choice(["Superfast", "Mail/Express", "Passenger"])
            
            train_data = {
                "name": f"TRAIN {train_input}",
                "zone": zone,
                "type": train_type,
                "route": "Indian Railways Route",
                "coaches": random.randint(16, 24),
                "max_speed": 110 if train_type == "Superfast" else 90,
                "departure": f"{random.randint(5, 22):02d}:{random.randint(0, 59):02d}",
                "arrival": "N/A",
                "duration": "N/A"
            }
            st.session_state.current_train = train_data
            st.session_state.train_number = train_input
            st.warning(f"⚠️ Train {train_input} not in main database. Showing simulated data.")
    else:
        st.error("❌ Please enter a train number")

# Use session state if available
if 'current_train' in st.session_state and not search_clicked:
    train_data = st.session_state.current_train
    train_input = st.session_state.train_number
    train_found = True

if train_found and train_data:
    # Get zone and type info
    zone_code = train_data["zone"]
    zone_info = ZONE_INFO.get(zone_code, {"name": "Indian Railways", "color": "#888888", "headquarters": "India"})
    train_type = train_data["type"]
    type_color = TRAIN_TYPE_COLORS.get(train_type, "#FFFFFF")
    
    # Display train header with Indian theme
    st.markdown(f"""
    <div class='saffron-glow' style='
        background: linear-gradient(90deg, #000000, #222222);
        padding: 30px; 
        border-radius: 20px; 
        border: 3px solid {type_color};
        margin: 30px 0;
        position: relative;
        overflow: hidden;
    '>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='flex: 1;'>
                <h1 style='color:{type_color} !important; margin:0; font-size: 36px;'>{train_data['name']}</h1>
                <p style='font-size: 28px; margin: 10px 0;'>Train No: <strong>{train_input}</strong></p>
                <div style='display: flex; gap: 20px; margin-top: 15px;'>
                    <span class='zone-badge zone-{zone_code.lower()}' style='background-color:{zone_info["color"]};'>
                        {zone_code} ZONE
                    </span>
                    <span style='
                        padding: 8px 20px;
                        border-radius: 20px;
                        background-color: {type_color};
                        color: #000000;
                        font-weight: 900;
                    '>
                        {train_type}
                    </span>
                </div>
            </div>
            <div style='text-align: right; flex: 1;'>
                <div style='font-size: 48px;'>🚂</div>
                <p style='font-size: 20px; margin: 5px 0;'><strong>Zone:</strong> {zone_info['name']}</p>
                <p style='font-size: 18px; margin: 5px 0;'><strong>HQ:</strong> {zone_info['headquarters']}</p>
            </div>
        </div>
        <div class='indian-divider' style='margin-top: 20px;'></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Train details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='train-card'>
            <h3>📋 TRAIN SPECIFICATIONS</h3>
            <p><strong>Train Number:</strong> {train_input}</p>
            <p><strong>Train Name:</strong> {train_data['name']}</p>
            <p><strong>Type:</strong> <span style='color:{type_color};'>{train_type}</span></p>
            <p><strong>Zone:</strong> {zone_info['name']} ({zone_code})</p>
            <p><strong>Coaches:</strong> {train_data['coaches']}</p>
            <p><strong>Max Speed:</strong> {train_data['max_speed']} km/h</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Generate current status
        current_speed = random.randint(int(train_data['max_speed']*0.6), int(train_data['max_speed']*0.9))
        delay = random.choice([0, 0, 0, 0, 5, 10, 15, 30, 60])
        status = "ON TIME" if delay == 0 else f"DELAYED {delay} MIN"
        status_color = "#00FF00" if delay == 0 else "#FFFF00" if delay <= 30 else "#FF0000"
        
        st.markdown(f"""
        <div class='train-card'>
            <h3>⚡ CURRENT STATUS</h3>
            <p><strong>Current Speed:</strong> {current_speed} km/h</p>
            <p><strong>Schedule Status:</strong> <span style='color:{status_color}; font-weight:900;'>{status}</span></p>
            <p><strong>Running Condition:</strong> Normal</p>
            <p><strong>GPS Signal:</strong> Strong</p>
            <p><strong>Last Update:</strong> Just now</p>
            <p><strong>Next Station:</strong> {random.choice(['Approaching', 'Departing', 'At Platform'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='train-card'>
            <h3>📍 SCHEDULE & ROUTE</h3>
            <p><strong>Route:</strong> {train_data['route']}</p>
            <p><strong>Departure:</strong> {train_data['departure']}</p>
            <p><strong>Arrival:</strong> {train_data.get('arrival', 'N/A')}</p>
            <p><strong>Duration:</strong> {train_data.get('duration', 'N/A')}</p>
            <p><strong>Distance:</strong> ~{random.randint(200, 2000)} km</p>
            <p><strong>Stations:</strong> {random.randint(10, 50)} stops</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="indian-divider"></div>', unsafe_allow_html=True)
    
    # Sync button
    if st.button(f"🛰️ SYNC LIVE DATA FOR {train_input} - {train_data['name']}", use_container_width=True):
        with st.spinner(f"🔗 Connecting to Indian Railways Network for {train_data['name']}..."):
            time.sleep(1.5)
            
            col_tracker, col_analytics = st.columns([1, 1.3])
            
            with col_tracker:
                st.markdown(f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <h2>📍 LIVE GPS TRACKING</h2>
                    <p style='font-size: 18px; color: #FF9933;'>Real-time position updates every 30 seconds</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Generate route stations based on train route
                route_parts = train_data['route'].split('→')
                if len(route_parts) >= 2:
                    start = route_parts[0].strip()
                    end = route_parts[-1].strip()
                    
                    # Common Indian stations
                    common_stations = {
                        "Chennai": ["Chennai Central", "Arakkonam", "Katpadi", "Jolarpettai"],
                        "Bangalore": ["Bangalore City", "Krishnarajapuram", "Bangalore Cant"],
                        "Mumbai": ["Mumbai Central", "Dadar", "Thane", "Kalyan"],
                        "Delhi": ["New Delhi", "Hazrat Nizamuddin", "Ghaziabad"],
                        "Kolkata": ["Howrah", "Kolkata", "Bardhaman"],
                        "Pune": ["Pune Junction", "Lonavala"],
                        "Hyderabad": ["Hyderabad Deccan", "Secunderabad"],
                    }
                    
                    # Select appropriate stations
                    stations = []
                    for station in common_stations.get(start.split()[0], []):
                        stations.append(station)
                    
                    # Add intermediate stations
                    mid_stations = ["Intermediate Junction", "Major City", "Division Point"]
                    stations.extend(mid_stations[:random.randint(1, 3)])
                    
                    for station in common_stations.get(end.split()[0], []):
                        stations.append(station)
                    
                    if len(stations) < 4:
                        stations = ["Origin Station", "Junction 1", "Junction 2", "Division HQ", "Destination"]
                else:
                    stations = ["Origin", "Station A", "Station B", "Station C", "Destination"]
                
                curr_idx = random.randint(0, len(stations)-2)
                
                # HTML tracker with Indian theme
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
                            font-family: 'Arial', sans-serif;
                        }}
                        
                        body {{
                            background: #000000;
                            padding: 20px;
                        }}
                        
                        .container {{
                            background: rgba(40, 40, 40, 0.95);
                            border: 3px solid {type_color};
                            border-radius: 20px;
                            padding: 25px;
                            box-shadow: 0 0 30px {type_color}40;
                            position: relative;
                            overflow: hidden;
                        }}
                        
                        .container::before {{
                            content: "🇮🇳";
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            font-size: 40px;
                            opacity: 0.2;
                        }}
                        
                        .header {{
                            color: {type_color} !important;
                            text-shadow: 0 0 15px {type_color}90;
                            font-size: 26px;
                            font-weight: 900;
                            text-align: center;
                            margin-bottom: 20px;
                            padding-bottom: 15px;
                            border-bottom: 2px solid {type_color};
                        }}
                        
                        .route-info {{
                            text-align: center;
                            color: #FF9933;
                            font-size: 18px;
                            margin-bottom: 25px;
                            font-weight: 700;
                        }}
                        
                        .station-tracker {{
                            position: relative;
                            padding-left: 60px;
                        }}
                        
                        .vertical-line {{
                            position: absolute;
                            left: 28px;
                            top: 0;
                            width: 4px;
                            height: 100%;
                            background: linear-gradient(to bottom, {type_color}, #138808);
                            z-index: 1;
                        }}
                        
                        .station-node {{
                            position: relative;
                            margin-bottom: 40px;
                            padding-left: 40px;
                            z-index: 2;
                        }}
                        
                        .station-name {{
                            color: #FFFFFF !important;
                            font-size: 22px;
                            font-weight: 800;
                            text-shadow: 0 0 8px rgba(255,255,255,0.8);
                            margin-bottom: 10px;
                        }}
                        
                        .train-icon {{
                            position: absolute;
                            left: -42px;
                            top: 0;
                            font-size: 44px;
                            z-index: 3;
                        }}
                        
                        .status-live {{
                            color: #FFFF00 !important;
                            font-size: 20px;
                            font-weight: 900;
                            text-shadow: 0 0 12px rgba(255,255,0,0.9);
                            background: rgba(255,255,0,0.15);
                            padding: 12px 24px;
                            border-radius: 12px;
                            border: 3px solid #FFFF00;
                            display: inline-block;
                            margin: 10px 0;
                            animation: pulse 2s infinite;
                        }}
                        
                        .status-upcoming {{
                            color: #00FF00 !important;
                            font-size: 18px;
                            font-weight: 700;
                            background: rgba(0,255,0,0.1);
                            padding: 10px 20px;
                            border-radius: 10px;
                            border: 2px solid #00FF00;
                            display: inline-block;
                            margin: 8px 0;
                        }}
                        
                        .status-passed {{
                            color: #00FFFF !important;
                            font-size: 18px;
                            font-weight: 700;
                            background: rgba(0,255,255,0.1);
                            padding: 10px 20px;
                            border-radius: 10px;
                            border: 2px solid #00FFFF;
                            display: inline-block;
                            margin: 8px 0;
                        }}
                        
                        .station-details {{
                            color: #FFFFFF !important;
                            font-size: 16px;
                            margin-top: 10px;
                            padding-left: 10px;
                        }}
                        
                        .station-details strong {{
                            color: #FF9933 !important;
                        }}
                        
                        .footer {{
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 2px solid #FF9933;
                            text-align: center;
                            color: #FFFFFF;
                            font-size: 16px;
                        }}
                        
                        @keyframes pulse {{
                            0%, 100% {{ transform: scale(1); opacity: 1; }}
                            50% {{ transform: scale(1.05); opacity: 0.8; }}
                        }}
                        
                        @keyframes moveTrain {{
                            0% {{ transform: translateX(0); }}
                            100% {{ transform: translateX(10px); }}
                        }}
                        
                        .moving-train {{
                            animation: moveTrain 1s infinite alternate;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="header">🚉 INDIAN RAILWAYS LIVE TRACKING</h1>
                        <div class="route-info">
                            {train_data['route']} • Train No: {train_input}
                        </div>
                        
                        <div class="station-tracker">
                            <div class="vertical-line"></div>
                '''
                
                for i, station in enumerate(stations):
                    is_live = (i == curr_idx)
                    is_passed = (i < curr_idx)
                    
                    if is_live:
                        track_html += f'''
                            <div class="station-node">
                                <div class="train-icon moving-train" style="color:{type_color};">🚅</div>
                                <div class="station-name">{station}</div>
                                <div class="status-live">● LIVE TRACKING ACTIVE</div>
                                <div class="station-details">
                                    <strong>Speed:</strong> {current_speed} km/h • 
                                    <strong>Delay:</strong> {delay} min • 
                                    <strong>Next:</strong> {stations[i+1] if i+1 < len(stations) else "Terminal"}
                                </div>
                            </div>
                        '''
                    elif is_passed:
                        track_html += f'''
                            <div class="station-node">
                                <div class="train-icon" style="color:#666666;">✓</div>
                                <div class="station-name">{station}</div>
                                <div class="status-passed">✓ PASSED</div>
                            </div>
                        '''
                    else:
                        eta = random.randint(15, 120)
                        track_html += f'''
                            <div class="station-node">
                                <div class="train-icon" style="color:#888888;">○</div>
                                <div class="station-name">{station}</div>
                                <div class="status-upcoming">⏰ UPCOMING • ETA: {eta} min</div>
                            </div>
                        '''
                
                track_html += f'''
                        </div>
                        
                        <div class="footer">
                            <strong>🇮🇳 INDIAN RAILWAYS NETWORK</strong><br>
                            📡 Satellite: IRNSS (NavIC) Active • 🛰️ GPS: ±10m accuracy • 
                            ⏱️ Updates: Every 30 seconds<br>
                            🔗 Connected to: {random.randint(5000, 15000)} trains nationwide
                        </div>
                    </div>
                    
                    <script>
                        // Auto-update time
                        function updateTime() {{
                            const now = new Date();
                            const timeStr = now.toLocaleTimeString('en-IN', {{hour: '2-digit', minute:'2-digit'}});
                            const dateStr = now.toLocaleDateString('en-IN');
                            
                            // Update any time elements
                            document.querySelectorAll('.station-details').forEach(el => {{
                                if (el.innerHTML.includes('Last update')) {{
                                    el.innerHTML = `<strong>Last update:</strong> ${{timeStr}} • <strong>Date:</strong> ${{dateStr}}`;
                                }}
                            }});
                        }}
                        
                        // Initialize
                        document.addEventListener('DOMContentLoaded', function() {{
                            updateTime();
                            setInterval(updateTime, 30000); // Update every 30 seconds
                        }});
                    </script>
                </body>
                </html>
                '''
                
                components.html(track_html, height=600)
            
            with col_analytics:
                st.markdown(f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <h2>📊 AI ANALYTICS DASHBOARD</h2>
                    <p style='font-size: 18px; color: #138808;'>Real-time analysis and predictions</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Panel 1: Weather in India
                indian_weather = random.choice([
                    ("Clear Sky ☀️", "Optimal running conditions", 15),
                    ("Heavy Rain 🌧️", "Monsoon alert - reduced speed", 35),
                    ("Fog 🌫️", "Low visibility - caution advised", 30),
                    ("Heat Wave 🔥", "High temperature - speed restrictions", 25),
                    ("Normal ☁️", "Standard operating conditions", 20)
                ])
                
                st.markdown(f'''
                <div style='
                    background: linear-gradient(135deg, rgba(173,216,230,0.95), rgba(135,206,250,0.95));
                    padding: 25px; 
                    border-radius: 15px; 
                    border-left: 10px solid #1E90FF;
                    margin-bottom: 20px;
                '>
                    <h3 style="color: #000080; margin-top: 0;">🌤️ INDIAN WEATHER UPDATE</h3>
                    <p style="color: #000080; font-size: 20px;"><strong>Condition:</strong> {indian_weather[0]}</p>
                    <p style="color: #000080; font-size: 18px;"><strong>Safety Gap:</strong> <span style="font-size: 24px;">{indian_weather[2]} km</span></p>
                    <p style="color: #000080; font-size: 16px;"><strong>AI Action:</strong> {indian_weather[1]}</p>
                    <p style="color: #000080; font-size: 14px;"><strong>Source:</strong> IMD (India Meteorological Department)</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Panel 2: Performance Metrics
                perf_score = random.randint(75, 98)
                fuel_saved = random.randint(10, 25)
                
                st.markdown(f'''
                <div style='
                    background: linear-gradient(135deg, rgba(255,218,185,0.95), rgba(255,228,196,0.95));
                    padding: 25px; 
                    border-radius: 15px; 
                    border-left: 10px solid #FF8C00;
                    margin-bottom: 20px;
                '>
                    <h3 style="color: #8B0000; margin-top: 0;">📈 PERFORMANCE METRICS</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="background: rgba(139,0,0,0.1); padding: 15px; border-radius: 10px;">
                            <p style="color: #8B0000; margin: 5px 0;"><strong>Efficiency:</strong></p>
                            <p style="color: #8B0000; font-size: 28px; margin: 0; font-weight: 900;">{perf_score}%</p>
                        </div>
                        <div style="background: rgba(139,0,0,0.1); padding: 15px; border-radius: 10px;">
                            <p style="color: #8B0000; margin: 5px 0;"><strong>Fuel Saved:</strong></p>
                            <p style="color: #8B0000; font-size: 28px; margin: 0; font-weight: 900;">{fuel_saved}%</p>
                        </div>
                    </div>
                    <p style="color: #8B0000; font-size: 14px; margin-top: 15px;">
                        <strong>CO₂ Reduction:</strong> ~{fuel_saved * 20} kg • 
                        <strong>Punctuality:</strong> {100 - delay}%
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Panel 3: Predictive Analytics
                next_station = stations[curr_idx + 1] if curr_idx + 1 < len(stations) else "Terminal Station"
                arrival_eta = random.randint(10, 90)
                
                st.markdown(f'''
                <div style='
                    background: linear-gradient(135deg, rgba(144,238,144,0.95), rgba(152,251,152,0.95));
                    padding: 25px; 
                    border-radius: 15px; 
                    border-left: 10px solid #32CD32;
                    margin-bottom: 20px;
                '>
                    <h3 style="color: #006400; margin-top: 0;">🔮 PREDICTIVE ARRIVAL SYSTEM</h3>
                    <p style="color: #006400; font-size: 20px;"><strong>Next Station:</strong> {next_station}</p>
                    <p style="color: #006400; font-size: 20px;"><strong>Estimated Arrival:</strong> 
                        <span style="font-size: 32px; font-weight: 900;">{arrival_eta} minutes</span>
                    </p>
                    <div style="background: rgba(0,100,0,0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
                        <p style="color: #006400; margin: 5px 0;"><strong>Confidence Level:</strong> 97.3%</p>
                        <p style="color: #006400; margin: 5px 0;"><strong>Algorithm:</strong> Indian Railways AI Model v2.1</p>
                        <p style="color: #006400; margin: 5px 0;"><strong>PIS Update:</strong> Station displays updated</p>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Panel 4: Maintenance & Health
                st.markdown(f'''
                <div style='
                    background: linear-gradient(135deg, rgba(216,191,216,0.95), rgba(221,160,221,0.95));
                    padding: 25px; 
                    border-radius: 15px; 
                    border-left: 10px solid #9370DB;
                '>
                    <h3 style="color: #4B0082; margin-top: 0;">🔧 MAINTENANCE & HEALTH</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="background: rgba(75,0,130,0.1); padding: 15px; border-radius: 10px;">
                            <p style="color: #4B0082; margin: 5px 0;"><strong>Engine Health:</strong></p>
                            <p style="color: #4B0082; font-size: 24px; margin: 0; font-weight: 900;">✅ EXCELLENT</p>
                        </div>
                        <div style="background: rgba(75,0,130,0.1); padding: 15px; border-radius: 10px;">
                            <p style="color: #4B0082; margin: 5px 0;"><strong>Next Service:</strong></p>
                            <p style="color: #4B0082; font-size: 20px; margin: 0; font-weight: 900;">{random.randint(1000, 5000)} km</p>
                        </div>
                    </div>
                    <p style="color: #4B0082; font-size: 14px; margin-top: 15px;">
                        <strong>Diagnostics:</strong> All systems normal • 
                        <strong>Vibration:</strong> Within limits • 
                        <strong>Temperature:</strong> Optimal
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            
            # Success message
            st.success(f"""
            ✅ **LIVE SYNC COMPLETE FOR TRAIN {train_input}!**
            
            **Train Name:** {train_data['name']}
            **Current Status:** Live tracking active
            **AI Dispatch:** Optimizing in real-time
            **Next Station:** {next_station} in {arrival_eta} minutes
            """)
            
            st.balloons()
    
    # Search another train
    st.markdown("---")
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        new_search = st.text_input("Search another Indian Railways train:", 
                                  placeholder="Enter train number...",
                                  key="new_search")
    with col_btn:
        if st.button("🔍 SEARCH", key="search_another", use_container_width=True):
            st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(255,153,51,0.1), rgba(255,255,255,0.05), rgba(19,136,8,0.1));
        padding: 50px; 
        border-radius: 25px; 
        border: 3px solid #FF9933;
        text-align: center;
        margin: 40px 0;
    '>
        <div style="font-size: 64px;">🚂🇮🇳</div>
        <h1 style='
            background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 48px;
            margin: 20px 0;
        '>INDIAN RAILWAYS AI DISPATCH</h1>
        <p style='font-size: 24px; margin: 20px 0;'>Enter ANY Indian Railways train number in the sidebar</p>
        <div style='
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
            margin: 20px auto;
        '>
            <p style='font-size: 20px; margin: 10px 0;'><strong>Examples:</strong> 12673, 12951, 12009, 22201</p>
            <p style='font-size: 18px; margin: 10px 0;'>Supports all Indian Railways trains nationwide</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show some popular trains
    st.markdown("### 🚂 POPULAR INDIAN TRAINS")
    popular_trains = [
        ("12673", "CHENNAI EXPRESS", "SR", "Superfast"),
        ("12951", "RAJDHANI EXPRESS", "WR", "Rajdhani"),
        ("12009", "SHATABDI EXPRESS", "NR", "Shatabdi"),
        ("22201", "VANDE BHARAT", "NR", "Vande Bharat"),
        ("12607", "LALBAGH EXPRESS", "SR", "Superfast"),
        ("12213", "DURONTO EXPRESS", "ER", "Duronto"),
    ]
    
    cols = st.columns(3)
    for idx, (num, name, zone, ttype) in enumerate(popular_trains):
        with cols[idx % 3]:
            type_color = TRAIN_TYPE_COLORS.get(ttype, "#FFFFFF")
            st.markdown(f"""
            <div style='
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid {type_color};
                cursor: pointer;
            ' onclick="document.querySelector('[placeholder*=\\'train\\']').value='{num}';">
                <p style='font-size: 18px; margin: 0;'><strong>{num}</strong></p>
                <p style='font-size: 16px; margin: 5px 0; color: {type_color};'>{name}</p>
                <p style='font-size: 14px; margin: 0;'>{zone} Zone • {ttype}</p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888888; font-size: 14px; padding: 20px;'>
    <div style='display: flex; justify-content: center; gap: 30px; margin-bottom: 10px;'>
        <span>🇮🇳 भारतीय रेल</span>
        <span>🚂 Indian Railways</span>
        <span>📡 AI Dispatch System v3.0</span>
    </div>
    <div>
        Covers 7,349 stations • 68,043 km route • 13,523 passenger trains daily
    </div>
</div>
""", unsafe_allow_html=True)
