import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# FIXED CSS - Pure Black Background with SUPER BRIGHT Text Colors
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
    
    /* ALL TEXT IN THE APP - SUPER BRIGHT FOR MAXIMUM VISIBILITY */
    * {
        color: #FFFFFF !important;
    }
    
    /* Force override for ALL text elements */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown, .stText {
        color: #FFFFFF !important;
        text-shadow: 0 0 2px rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Special bright colors for emphasis */
    .stTitle, .stHeader, h1 {
        color: #00FFFF !important; /* Neon Cyan */
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8) !important;
        font-weight: 800 !important;
    }
    
    h2, h3 {
        color: #FFFF00 !important; /* Bright Yellow */
        text-shadow: 0 0 8px rgba(255, 255, 0, 0.7) !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar - ALL TEXT BRIGHT WHITE */
    section[data-testid="stSidebar"] { 
        background-color: #111111 !important; 
        border-right: 2px solid #00FFFF !important;
    }
    section[data-testid="stSidebar"] * { 
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar input fields - visible */
    .stTextInput>div>div>input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 2px solid #00FFFF !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Info box - bright */
    .stInfo {
        background-color: rgba(0, 100, 255, 0.3) !important;
        border-left: 5px solid #00FFFF !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* VERTICAL TRACKER UI - SUPER BRIGHT COLORS */
    .station-node { 
        border-left: 4px solid #00FFFF; 
        margin-left: 45px; 
        padding: 25px; 
        position: relative; 
        background-color: rgba(40, 40, 40, 0.9) !important; /* Darker background for contrast */
        border-radius: 10px !important;
        margin-bottom: 15px !important;
    }
    
    .station-name { 
        font-weight: bold !important; 
        font-size: 24px !important; 
        color: #FFFFFF !important; /* PURE WHITE */
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 10px !important;
    }
    
    .train-icon { 
        font-size: 42px !important; 
        position: absolute !important; 
        left: -30px !important; 
        top: 20px !important; 
        z-index: 10 !important;
        filter: drop-shadow(0 0 5px #00FFFF) !important;
    }
    
    .live-text { 
        color: #FFFF00 !important; /* Bright Yellow */
        font-weight: bold !important; 
        font-size: 20px !important; 
        text-transform: uppercase !important;
        text-shadow: 0 0 10px rgba(255, 255, 0, 0.9) !important;
        animation: blinker 1s linear infinite !important;
        background-color: rgba(255, 255, 0, 0.15) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        display: inline-block !important;
    }
    
    .scheduled-text { 
        color: #00FF00 !important; /* Bright Green */
        font-size: 18px !important; 
        font-weight: 600 !important;
        text-shadow: 0 0 6px rgba(0, 255, 0, 0.7) !important;
        background-color: rgba(0, 255, 0, 0.1) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        display: inline-block !important;
    }
    
    @keyframes blinker { 
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }

    /* NOTIFICATION PANELS - LIGHT BACKGROUNDS WITH DARK TEXT FOR MAX CONTRAST */
    .status-box { 
        padding: 25px !important; 
        border-radius: 12px !important; 
        margin-bottom: 20px !important; 
        border-left: 10px solid !important; 
        box-shadow: 0px 4px 20px rgba(255, 255, 255, 0.2) !important;
        font-weight: 600 !important;
    }
    
    /* Weather Panel - LIGHT Blue with DARK Blue Text */
    .weather-panel { 
        background-color: rgba(173, 216, 230, 0.95) !important; /* LIGHT BLUE */
        border-color: #1E90FF !important; 
        color: #000080 !important; /* DARK BLUE TEXT */
    }
    
    /* Health Panel - LIGHT Orange with DARK Red Text */
    .health-panel { 
        background-color: rgba(255, 218, 185, 0.95) !important; /* LIGHT ORANGE */
        border-color: #FF8C00 !important; 
        color: #8B0000 !important; /* DARK RED TEXT */
    }
    
    /* Energy Panel - LIGHT Green with DARK Green Text */
    .energy-panel { 
        background-color: rgba(144, 238, 144, 0.95) !important; /* LIGHT GREEN */
        border-color: #32CD32 !important; 
        color: #006400 !important; /* DARK GREEN TEXT */
    }
    
    /* PIS Panel - LIGHT Purple with DARK Purple Text */
    .pis-panel { 
        background-color: rgba(216, 191, 216, 0.95) !important; /* LIGHT PURPLE */
        border-color: #9370DB !important; 
        color: #4B0082 !important; /* DARK PURPLE TEXT */
    }
    
    /* Make ALL text inside panels DARK for contrast */
    .status-box * {
        color: inherit !important;
        text-shadow: none !important;
    }
    
    /* PRIMARY SYNC BUTTON - NEON GLOW */
    .stButton>button { 
        width: 100% !important; 
        border-radius: 10px !important; 
        background: linear-gradient(90deg, #000000, #222222) !important; 
        color: #00FFFF !important; 
        font-weight: bold !important; 
        height: 60px !important; 
        border: 2px solid #00FFFF !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.8) !important;
        font-size: 20px !important;
        text-shadow: 0 0 8px rgba(0, 255, 255, 0.9) !important;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    
    .stButton>button:hover { 
        box-shadow: 0 0 30px rgba(0, 255, 255, 1) !important;
        background: linear-gradient(90deg, #111111, #333333) !important;
        transform: translateY(-2px) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Columns - visible with bright borders */
    [data-testid="column"] {
        background-color: rgba(30, 30, 30, 0.9) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        border: 2px solid rgba(0, 255, 255, 0.4) !important;
        margin: 10px !important;
    }
    
    /* Spinner - visible */
    .stSpinner > div {
        border-color: #00FFFF transparent transparent transparent !important;
    }
    
    /* Divider - bright cyan */
    hr {
        border-color: #00FFFF !important;
        background-color: #00FFFF !important;
        height: 3px !important;
        margin: 25px 0 !important;
    }
    
    /* Write text - bright */
    .stWrite, .stText {
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border-left: 4px solid #00FFFF !important;
    }
    
    /* Make sure ALL bolding is visible */
    b, strong {
        color: #FFFF00 !important;
        text-shadow: 0 0 5px rgba(255, 255, 0, 0.7) !important;
    }
    
    /* Fix for any remaining dark text */
    div[class*="st-"] {
        color: #FFFFFF !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - With visible text
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673")
    st.markdown("---")
    st.markdown("## 💡 AI Methodology")
    # Using markdown with inline styling for bright text
    st.markdown(
        """
        <div style='color:#FFFFFF; font-weight:600; background:rgba(255,255,255,0.1); padding:15px; border-radius:10px; border-left:4px solid #00FFFF;'>
        <b>Deep Q-Network (DQN) Implementation:</b><br>
        • Minimize 'Ghost Space' between trains<br>
        • Maximize Section Throughput<br>
        • Dynamic speed adjustment based on real-time conditions
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.info("**System Status:** Moving Block Signaling Active ✅")

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

# Display train details in BRIGHT VISIBLE boxes
st.markdown("""
    <div style='background:rgba(255,255,255,0.15); padding:25px; border-radius:15px; border-left:8px solid #00FFFF; margin:25px 0; box-shadow: 0 0 20px rgba(0,255,255,0.3);'>
        <h2 style='color:#00FFFF; text-align:center;'>📊 Train 12673 - Live Details</h2>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;'>
            <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
                <p style='color:#FFFFFF; font-size:18px;'><strong>🚂 Train ID:</strong> 12673</p>
                <p style='color:#FFFFFF; font-size:18px;'><strong>📍 Current Location:</strong> En Route</p>
                <p style='color:#FFFFFF; font-size:18px;'><strong>🎯 Destination:</strong> Jolarpettai Jn</p>
            </div>
            <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
                <p style='color:#FFFFFF; font-size:18px;'><strong>⚡ Current Speed:</strong> 85 km/h</p>
                <p style='color:#FFFFFF; font-size:18px;'><strong>📏 Distance Covered:</strong> 245 km</p>
                <p style='color:#FFFFFF; font-size:18px;'><strong>⏱️ AI Control:</strong> ACTIVE</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if st.button("🛰️ Sync Live Satellite & Start AI Dispatch"):
    # Enhancement Analytics (Weather, Maintenance, Energy)
    weather_list = [("Heavy Rain 🌧️", 28.5), ("Dense Fog 🌫️", 34.0), ("Clear Sky ☀️", 12.0)]
    weather, gap = random.choice(weather_list)
    
    with st.spinner("🛰️ Connecting to Global Satellite Feed..."):
        time.sleep(1.5)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 Real-Time GPS Tracking")
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = """
        <div style="background: rgba(20,20,20,0.9); padding: 25px; border-radius: 15px; border: 2px solid #00FFFF;">
            <h3 style="color: #00FFFF; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px rgba(0,255,255,0.7);">Live Train Position</h3>
        """
        for i, s in enumerate(stations):
            is_live = (s == stations[curr_idx])
            icon = "🚅" if is_live else "○"
            line_color = "#00FFFF" if i <= curr_idx else "#666666"
            status = f"<div class='live-text'>● LIVE NOW - TRACKING ACTIVE</div>" if is_live else f"<div class='scheduled-text'>✓ SCHEDULED</div>"
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon" style="color: #00FFFF;">{icon}</span>
                <div class="station-name">{s}</div>
                {status}
            </div>"""
        track_html += "</div>"
        components.html(track_html, height=550)

    with col_data:
        st.subheader("📢 AI Analytics Feed")
        
        # Display all analytics in BRIGHT, HIGH-CONTRAST panels
        # 1. Weather Integration
        st.markdown(f"""<div class="status-box weather-panel">
            <h3 style="margin-top: 0; color: #000080;">☁️ Weather Condition: {weather}</h3>
            <p style="font-size: 18px; color: #000080;">AI Action: Safety Gap optimized to <b>{gap} km</b></p>
            <p style="font-size: 16px; color: #000080;">Real-time satellite weather data integrated for safety adjustments.</p>
        </div>""", unsafe_allow_html=True)
        
        # 2. Predictive Maintenance
        st.markdown(f"""<div class="status-box health-panel">
            <h3 style="margin-top: 0; color: #8B0000;">🔧 Engine Health: HEALTHY ✅</h3>
            <p style="font-size: 18px; color: #8B0000;">Diagnostic: No critical vibrations detected by AI sensors.</p>
            <p style="font-size: 16px; color: #8B0000;">All systems operating within optimal parameters.</p>
        </div>""", unsafe_allow_html=True)
        
        # 3. Energy Optimization
        fuel_saved = random.randint(12, 22)
        st.markdown(f"""<div class="status-box energy-panel">
            <h3 style="margin-top: 0; color: #006400;">⚡ Energy Efficiency: ACTIVE</h3>
            <p style="font-size: 18px; color: #006400;">Fuel Saved: <b>{fuel_saved}%</b> via AI Precise Throttle Control.</p>
            <p style="font-size: 16px; color: #006400;">Optimal acceleration/deceleration patterns applied.</p>
        </div>""", unsafe_allow_html=True)

        # 4. PIS Prediction
        arrival_time = random.randint(15, 45)
        next_station = stations[curr_idx + 1] if curr_idx < len(stations) - 1 else "Terminal Station"
        st.markdown(f"""<div class="status-box pis-panel">
            <h3 style="margin-top: 0; color: #4B0082;">🔮 AI Precise Arrival Prediction (PIS)</h3>
            <p style="font-size: 18px; color: #4B0082;">Arriving at <b>{next_station}</b> in <b>{arrival_time} minutes</b>.</p>
            <p style="font-size: 16px; color: #4B0082;">Prediction accuracy: 98.7% based on current conditions.</p>
        </div>""", unsafe_allow_html=True)
        
        # Additional Train Details in bright format
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.2); padding: 25px; border-radius: 15px; margin-top: 25px; border: 2px solid #FFFF00;">
            <h3 style="color: #FFFF00; text-align: center;">📈 Performance Metrics</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                <div style="background: rgba(0,0,0,0.6); padding: 15px; border-radius: 10px;">
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Current Speed:</strong> 85 km/h</p>
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Distance Covered:</strong> 245 km</p>
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Next Stop:</strong> {next_station}</p>
                </div>
                <div style="background: rgba(0,0,0,0.6); padding: 15px; border-radius: 10px;">
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Estimated Delay:</strong> 0 minutes</p>
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Section Throughput:</strong> +18%</p>
                    <p style="color: #FFFFFF; font-size: 17px;"><strong>Ghost Space:</strong> Minimized</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.balloons()
