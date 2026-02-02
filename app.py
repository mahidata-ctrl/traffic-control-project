import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# Pure Black Background with Neon Bright Text Colors
st.markdown("""
    <style>
    /* PURE BLACK BACKGROUND THEME */
    .stApp { 
        background-color: #000000 !important; 
        color: #ffffff !important;
    }
    
    /* Main container background */
    .main .block-container { 
        background-color: #000000 !important;
        padding-top: 2rem;
    }
    
    /* Titles and Headers - NEON BRIGHT COLORS */
    h1, h2, h3, .stTitle, .stHeader {
        color: #00FFFF !important; /* Neon Cyan */
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.7) !important;
        font-weight: 800 !important;
    }
    
    /* General Text - Bright White */
    p, span, div, .stMarkdown, .stText {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar - Dark Gray with Bright Text */
    section[data-testid="stSidebar"] { 
        background-color: #111111 !important; 
        border-right: 2px solid #00FFFF !important;
    }
    section[data-testid="stSidebar"] * { 
        color: #FFFFFF !important !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar Titles - Neon Green */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #00FF00 !important; /* Neon Green */
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.5) !important;
    }
    
    /* Sidebar Input Fields */
    .stTextInput>div>div>input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 1px solid #00FFFF !important;
        font-weight: 600 !important;
    }
    
    /* Info Box */
    .stInfo {
        background-color: #1a1a1a !important;
        border-left: 5px solid #00FFFF !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* VERTICAL TRACKER UI - NEON BRIGHT COLORS */
    .station-node { 
        border-left: 4px solid #00FFFF; 
        margin-left: 45px; 
        padding: 25px; 
        position: relative; 
        background-color: rgba(0, 0, 0, 0.5) !important;
    }
    
    .station-name { 
        font-weight: bold !important; 
        font-size: 22px !important; 
        color: #FF00FF !important; /* Bright Magenta */
        text-shadow: 0 0 5px rgba(255, 0, 255, 0.5) !important;
    }
    
    .train-icon { 
        font-size: 38px !important; 
        position: absolute !important; 
        left: -25px !important; 
        top: 15px !important; 
        z-index: 10 !important;
    }
    
    .live-text { 
        color: #FFFF00 !important; /* Bright Yellow */
        font-weight: bold !important; 
        font-size: 18px !important; 
        text-transform: uppercase !important;
        text-shadow: 0 0 8px rgba(255, 255, 0, 0.7) !important;
    }
    
    .scheduled-text { 
        color: #00FF00 !important; /* Bright Green */
        font-size: 16px !important; 
        font-weight: 600 !important;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.3) !important;
    }
    
    @keyframes blinker { 
        50% { opacity: 0.5; } 
    }

    /* COLORFUL NOTIFICATION PANELS - VIBRANT BACKGROUNDS WITH BRIGHT TEXT */
    .status-box { 
        padding: 20px !important; 
        border-radius: 12px !important; 
        margin-bottom: 15px !important; 
        border-left: 10px solid !important; 
        box-shadow: 0px 4px 15px rgba(0, 255, 255, 0.3) !important;
        font-weight: 600 !important;
    }
    
    /* Weather Panel - Blue with Bright Text */
    .weather-panel { 
        background-color: rgba(30, 144, 255, 0.2) !important; 
        border-color: #00BFFF !important; 
        color: #00FFFF !important; /* Bright Cyan Text */
    }
    
    /* Health Panel - Orange with Bright Text */
    .health-panel { 
        background-color: rgba(255, 140, 0, 0.2) !important; 
        border-color: #FFA500 !important; 
        color: #FFFF00 !important; /* Bright Yellow Text */
    }
    
    /* Energy Panel - Green with Bright Text */
    .energy-panel { 
        background-color: rgba(50, 205, 50, 0.2) !important; 
        border-color: #00FF00 !important; 
        color: #00FF00 !important; /* Bright Green Text */
    }
    
    /* PIS Panel - Purple with Bright Text */
    .pis-panel { 
        background-color: rgba(138, 43, 226, 0.2) !important; 
        border-color: #9370DB !important; 
        color: #FF00FF !important; /* Bright Magenta Text */
    }
    
    /* PRIMARY SYNC BUTTON - NEON GLOW EFFECT */
    .stButton>button { 
        width: 100% !important; 
        border-radius: 10px !important; 
        background: linear-gradient(90deg, #000000, #222222) !important; 
        color: #00FFFF !important !important; 
        font-weight: bold !important; 
        height: 55px !important; 
        border: 2px solid #00FFFF !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
        font-size: 18px !important;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.7) !important;
    }
    
    .stButton>button:hover { 
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.8) !important;
        background: linear-gradient(90deg, #111111, #333333) !important;
    }
    
    /* Columns and Layout */
    [data-testid="column"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        border: 1px solid rgba(0, 255, 255, 0.2) !important;
    }
    
    /* Balloons animation color */
    .balloons-container path {
        fill: #00FFFF !important;
    }
    
    /* Spinner color */
    .stSpinner > div {
        border-color: #00FFFF transparent transparent transparent !important;
    }
    
    /* Divider lines */
    hr {
        border-color: #00FFFF !important;
        background-color: #00FFFF !important;
        height: 2px !important;
    }
    
    /* Tab and selection colors */
    .st-bd, .st-bg, .st-bh, .st-bi, .st-bj {
        border-color: #00FFFF !important;
    }
    
    /* Selection and focus */
    :focus {
        outline-color: #00FFFF !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - Matching Image 2 Logic
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673")
    st.markdown("---")
    st.markdown("## 💡 AI Methodology")
    st.write("Using Deep Q-Network (DQN) to minimize 'Ghost Space' and maximize Section Throughput.")
    st.info("System: Moving Block Signaling Active")

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    # Enhancement Analytics (Weather, Maintenance, Energy)
    weather_list = [("Heavy Rain 🌧️", 28.5), ("Dense Fog 🌫️", 34.0), ("Clear Sky ☀️", 12.0)]
    weather, gap = random.choice(weather_list)
    
    with st.spinner("Connecting to Global Satellite Feed..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Real-Time GPS Tracking")
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = "<div>"
        for s in stations:
            is_live = (s == stations[curr_idx])
            icon = "🚅" if is_live else ""
            line_color = "#00FFFF" if stations.index(s) <= curr_idx else "#444444"
            status = f"<div class='live-text'>● LIVE NOW</div>" if is_live else "<div class='scheduled-text'>Scheduled</div>"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon">{icon}</span>
                <div class="station-name">{s}</div>
                {status}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=500)

    with col_data:
        st.subheader("📢 AI Analytics Feed")
        
        # 1. Weather Integration (Blue)
        st.markdown(f"""<div class="status-box weather-panel">
            <b>☁️ Weather Condition: {weather}</b><br>
            AI Action: Safety Gap optimized to <b>{gap} km</b>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance (Orange)
        st.markdown(f"""<div class="status-box health-panel">
            <b>🔧 Engine Health: Healthy ✅</b><br>
            Diagnostic: No critical vibrations detected by AI sensors.
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization (Green)
        st.markdown(f"""<div class="status-box energy-panel">
            <b>⚡ Energy Efficiency: Active</b><br>
            Fuel Saved: <b>{random.randint(12, 22)}%</b> via AI Precise Throttle.
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction (Dark Blue)
        st.markdown(f"""<div class="status-box pis-panel">
            <b>🔮 AI Precise Arrival (PIS)</b><br>
            Arriving at {stations[curr_idx+1]} in {random.randint(15, 45)} mins.
        </div>""", unsafe_allow_html=True)

    st.balloons()
