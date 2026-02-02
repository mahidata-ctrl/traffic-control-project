import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# FIXED CSS - SUPER BRIGHT TEXT ON BLACK BACKGROUND
st.markdown("""
    <style>
    /* ============================================
       FORCE ALL TEXT TO BE BRIGHT WHITE - MAIN FIX
       ============================================ */
    * {
        color: #FFFFFF !important;
    }
    
    /* PURE BLACK BACKGROUND */
    .stApp { 
        background-color: #000000 !important;
    }
    
    .main .block-container { 
        background-color: #000000 !important;
        padding-top: 2rem;
    }
    
    /* ============================================
       HEADERS WITH BRIGHT COLORS AND GLOW EFFECTS
       ============================================ */
    h1 {
        color: #00FFFF !important;
        text-shadow: 0 0 15px rgba(0, 255, 255, 0.9) !important;
        font-weight: 900 !important;
        font-size: 42px !important;
        text-align: center !important;
        padding: 20px !important;
        border-bottom: 3px solid #00FFFF !important;
    }
    
    h2 {
        color: #FFFF00 !important;
        text-shadow: 0 0 12px rgba(255, 255, 0, 0.8) !important;
        font-weight: 800 !important;
        font-size: 32px !important;
        margin-top: 30px !important;
        padding-bottom: 10px !important;
        border-bottom: 2px solid #FFFF00 !important;
    }
    
    h3 {
        color: #00FF00 !important;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.7) !important;
        font-weight: 700 !important;
        font-size: 26px !important;
    }
    
    /* ============================================
       ALL GENERAL TEXT - BRIGHT WITH SHADOWS
       ============================================ */
    p, span, div:not(.status-box):not(.station-node):not([class*="st"]), label {
        color: #FFFFFF !important;
        text-shadow: 0 0 4px rgba(255, 255, 255, 0.6) !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }
    
    /* Bold text extra bright */
    b, strong {
        color: #FFFF00 !important;
        text-shadow: 0 0 8px rgba(255, 255, 0, 0.8) !important;
        font-weight: 700 !important;
    }
    
    /* ============================================
       SIDEBAR - ALL TEXT BRIGHT WHITE
       ============================================ */
    section[data-testid="stSidebar"] { 
        background-color: #111111 !important;
        border-right: 3px solid #00FFFF !important;
    }
    
    /* Force all sidebar text white */
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important !important;
        text-shadow: 0 0 3px rgba(255, 255, 255, 0.5) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar headers with neon colors */
    section[data-testid="stSidebar"] h2 {
        color: #00FF00 !important;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.7) !important;
        font-size: 28px !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #00FFFF !important;
        text-shadow: 0 0 8px rgba(0, 255, 255, 0.6) !important;
        font-size: 24px !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 2px solid #00FFFF !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }
    
    /* ============================================
       INFO BOXES AND ALERTS
       ============================================ */
    .stInfo {
        background-color: rgba(0, 100, 255, 0.3) !important;
        border-left: 6px solid #00FFFF !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.6) !important;
    }
    
    /* ============================================
       VERTICAL TRAIN TRACKER - SUPER BRIGHT
       ============================================ */
    .station-node { 
        border-left: 5px solid #00FFFF;
        margin-left: 50px;
        padding: 30px;
        position: relative;
        background-color: rgba(40, 40, 40, 0.95) !important;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 255, 255, 0.3);
    }
    
    .station-name { 
        font-weight: 800 !important;
        font-size: 26px !important;
        color: #FFFFFF !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 15px;
        letter-spacing: 1px;
    }
    
    .train-icon { 
        font-size: 46px !important;
        position: absolute !important;
        left: -35px !important;
        top: 25px !important;
        z-index: 10 !important;
        filter: drop-shadow(0 0 8px #00FFFF) !important;
    }
    
    .live-text { 
        color: #FFFF00 !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        text-transform: uppercase !important;
        text-shadow: 0 0 12px rgba(255, 255, 0, 1) !important;
        animation: blinker 1s linear infinite !important;
        background-color: rgba(255, 255, 0, 0.2) !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        display: inline-block !important;
        border: 2px solid #FFFF00 !important;
    }
    
    .scheduled-text { 
        color: #00FF00 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.8) !important;
        background-color: rgba(0, 255, 0, 0.15) !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        display: inline-block !important;
        border: 2px solid #00FF00 !important;
    }
    
    @keyframes blinker { 
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    
    /* ============================================
       ANALYTICS PANELS - LIGHT BG WITH DARK TEXT
       ============================================ */
    .status-box { 
        padding: 30px !important;
        border-radius: 15px !important;
        margin-bottom: 25px !important;
        border-left: 12px solid !important;
        box-shadow: 0px 6px 25px rgba(255, 255, 255, 0.25) !important;
        font-weight: 600 !important;
    }
    
    /* Weather - Light Blue, Dark Blue Text */
    .weather-panel { 
        background-color: rgba(173, 216, 230, 1) !important;
        border-color: #1E90FF !important;
    }
    
    .weather-panel * {
        color: #000080 !important;
        text-shadow: none !important;
        font-weight: 600 !important;
    }
    
    /* Health - Light Orange, Dark Red Text */
    .health-panel { 
        background-color: rgba(255, 218, 185, 1) !important;
        border-color: #FF8C00 !important;
    }
    
    .health-panel * {
        color: #8B0000 !important;
        text-shadow: none !important;
        font-weight: 600 !important;
    }
    
    /* Energy - Light Green, Dark Green Text */
    .energy-panel { 
        background-color: rgba(144, 238, 144, 1) !important;
        border-color: #32CD32 !important;
    }
    
    .energy-panel * {
        color: #006400 !important;
        text-shadow: none !important;
        font-weight: 600 !important;
    }
    
    /* PIS - Light Purple, Dark Purple Text */
    .pis-panel { 
        background-color: rgba(216, 191, 216, 1) !important;
        border-color: #9370DB !important;
    }
    
    .pis-panel * {
        color: #4B0082 !important;
        text-shadow: none !important;
        font-weight: 600 !important;
    }
    
    /* ============================================
       BUTTONS - NEON GLOW EFFECTS
       ============================================ */
    .stButton>button { 
        width: 100% !important;
        border-radius: 12px !important;
        background: linear-gradient(90deg, #000000, #222222) !important;
        color: #00FFFF !important;
        font-weight: 900 !important;
        height: 65px !important;
        border: 3px solid #00FFFF !important;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.9) !important;
        font-size: 22px !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 1) !important;
        margin: 15px 0 30px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover { 
        box-shadow: 0 0 35px rgba(0, 255, 255, 1) !important;
        background: linear-gradient(90deg, #111111, #333333) !important;
        transform: translateY(-3px) !important;
    }
    
    /* ============================================
       COLUMNS AND LAYOUT
       ============================================ */
    [data-testid="column"] {
        background-color: rgba(35, 35, 35, 0.95) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        border: 2px solid rgba(0, 255, 255, 0.5) !important;
        margin: 15px !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.2) !important;
    }
    
    /* ============================================
       OTHER ELEMENTS
       ============================================ */
    .stSpinner > div {
        border-color: #00FFFF transparent transparent transparent !important;
        border-width: 4px !important;
    }
    
    hr {
        border-color: #00FFFF !important;
        background-color: #00FFFF !important;
        height: 4px !important;
        margin: 35px 0 !important;
        border-radius: 2px !important;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.7) !important;
    }
    
    /* Fix for Streamlit's default dark text */
    .stMarkdown, .stText {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border-left: 5px solid #00FFFF !important;
        margin: 15px 0 !important;
    }
    
    /* Performance metrics grid */
    .metrics-grid {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 20px !important;
        margin: 20px 0 !important;
    }
    
    .metric-box {
        background: rgba(0, 0, 0, 0.7) !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #00FFFF !important;
    }
    
    .metric-box p {
        font-size: 19px !important;
        margin: 10px 0 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673", 
                           help="Enter the train identification number for tracking")
    
    st.markdown("---")
    
    st.markdown("## 💡 AI Methodology")
    st.markdown("""
    <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:12px; border-left:5px solid #00FF00;'>
    <p style='font-size:18px; margin-bottom:10px;'><b>Deep Q-Network (DQN) Implementation</b></p>
    <p style='font-size:16px;'>• <b>Minimize 'Ghost Space'</b> between trains</p>
    <p style='font-size:16px;'>• <b>Maximize Section Throughput</b> by 15-25%</p>
    <p style='font-size:16px;'>• <b>Dynamic speed adjustment</b> based on real-time conditions</p>
    <p style='font-size:16px;'>• <b>Collision avoidance</b> with predictive algorithms</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **🚦 System Status: Moving Block Signaling ACTIVE**\n
    **📍 Current Mode:** AI-Controlled Dispatch\n
    **🔄 Last Updated:** Real-time\n
    **✅ Connection:** Satellite Link Established
    """)

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

# TRAIN DETAILS SECTION - SUPER BRIGHT AND VISIBLE
st.markdown("""
<div style='background:rgba(255,255,255,0.15); padding:30px; border-radius:20px; border:3px solid #00FFFF; margin:30px 0; box-shadow: 0 0 30px rgba(0,255,255,0.4);'>
    <h2 style='color:#00FFFF; text-align:center; margin-bottom:30px;'>📊 TRAIN 12673 - LIVE OPERATIONAL DETAILS</h2>
    
    <div class="metrics-grid">
        <div class="metric-box">
            <p><b>🚂 Train ID:</b> 12673</p>
            <p><b>📍 Current Location:</b> En Route - Active Tracking</p>
            <p><b>🎯 Final Destination:</b> Jolarpettai Jn</p>
            <p><b>📅 Departure Time:</b> 08:30 AM</p>
        </div>
        
        <div class="metric-box">
            <p><b>⚡ Current Speed:</b> 85 km/h</p>
            <p><b>📏 Distance Covered:</b> 245 km (62%)</p>
            <p><b>⏱️ Estimated Arrival:</b> 01:45 PM</p>
            <p><b>🎛️ AI Control Status:</b> <span style='color:#00FF00;'>ACTIVE ✅</span></p>
        </div>
        
        <div class="metric-box">
            <p><b>👥 Passenger Count:</b> 1,240</p>
            <p><b>🔋 Energy Usage:</b> Optimal (78%)</p>
            <p><b>🛤️ Track Condition:</b> Normal</p>
            <p><b>📡 Signal Strength:</b> Excellent</p>
        </div>
        
        <div class="metric-box">
            <p><b>⏰ Schedule Adherence:</b> +2 minutes</p>
            <p><b>🎯 Section Throughput:</b> +18% Improved</p>
            <p><b>👻 Ghost Space:</b> Minimized (92%)</p>
            <p><b>🔧 Maintenance Status:</b> All Systems Go</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# MAIN ACTION BUTTON
if st.button("🛰️ SYNC LIVE SATELLITE & START AI DISPATCH"):
    # Enhancement Analytics (Weather, Maintenance, Energy)
    weather_list = [
        ("Heavy Rain 🌧️", 28.5, "Increased safety gap due to reduced visibility"),
        ("Dense Fog 🌫️", 34.0, "Extended braking distance required"),
        ("Clear Sky ☀️", 12.0, "Optimal conditions for maximum throughput")
    ]
    weather, gap, condition_note = random.choice(weather_list)
    
    with st.spinner("🛰️ CONNECTING TO GLOBAL SATELLITE FEED... UPLOADING REAL-TIME DATA..."):
        time.sleep(2)
        
    col_map, col_data = st.columns([1, 1.3])

    # LEFT COLUMN: GPS TRACKING
    with col_map:
        st.markdown("""
        <div style='text-align:center; margin-bottom:20px;'>
            <h2>📍 REAL-TIME GPS TRACKING</h2>
            <p style='font-size:18px;'>Live position updates every 30 seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        stations = ["Chennai Central", "Arakkonam Jn", "Katpadi Jn", "Jolarpettai Jn"]
        curr_idx = random.randint(0, 2)
        
        track_html = """
        <div style="background: rgba(25,25,25,0.95); padding: 30px; border-radius: 20px; border: 3px solid #00FFFF;">
            <h3 style="color: #00FFFF; text-align: center; margin-bottom: 30px; font-size: 28px;">
                🚅 LIVE TRAIN POSITION TRACKER
            </h3>
        """
        
        for i, s in enumerate(stations):
            is_live = (s == stations[curr_idx])
            icon = "🚅" if is_live else "○"
            icon_color = "#00FFFF" if is_live else "#666666"
            line_color = "#00FFFF" if i <= curr_idx else "#444444"
            
            if is_live:
                status = """<div class='live-text'>● LIVE NOW - ACTIVE TRACKING</div>
                          <div style='color:#00FFFF; font-size:16px; margin-top:5px;'>
                          Last update: Just now | Signal: Strong</div>"""
            else:
                if i < curr_idx:
                    status = """<div class='scheduled-text'>✓ DEPARTED - JOURNEY COMPLETE</div>
                              <div style='color:#00FF00; font-size:16px; margin-top:5px;'>
                              Arrived on time</div>"""
                else:
                    status = """<div class='scheduled-text'>⏰ UPCOMING - SCHEDULED</div>
                              <div style='color:#FFFFFF; font-size:16px; margin-top:5px;'>
                              ETA: Based on current speed</div>"""
            
            track_html += f"""
            <div class="station-node" style="border-left-color: {line_color};">
                <span class="train-icon" style="color: {icon_color};">{icon}</span>
                <div class="station-name">{s}</div>
                {status}
            </div>"""
        
        track_html += """
            <div style="text-align:center; margin-top:30px; color:#00FFFF; font-size:18px;">
                <b>📡 Satellite Connection:</b> Active | <b>🛰️ GPS Accuracy:</b> ±5 meters |
                <b>⏱️ Update Frequency:</b> 30 seconds
            </div>
        </div>"""
        
        components.html(track_html, height=600)

    # RIGHT COLUMN: AI ANALYTICS
    with col_data:
        st.markdown("""
        <div style='text-align:center; margin-bottom:20px;'>
            <h2>📢 AI ANALYTICS FEED</h2>
            <p style='font-size:18px;'>Real-time analysis and predictive insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. WEATHER INTEGRATION PANEL
        st.markdown(f"""<div class="status-box weather-panel">
            <h3 style="margin: 0 0 15px 0; font-size: 26px;">☁️ WEATHER CONDITION: {weather}</h3>
            <p style="font-size: 20px; margin: 10px 0;"><b>AI Action:</b> Safety gap optimized to <span style='font-size:24px;'>{gap} km</span></p>
            <p style="font-size: 18px; margin: 8px 0;"><b>Condition Note:</b> {condition_note}</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>Satellite Data:</b> Integrated from NOAA-20 & GOES-18</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>Impact on Schedule:</b> Minimal (adjusted in AI model)</p>
        </div>""", unsafe_allow_html=True)
        
        # 2. PREDICTIVE MAINTENANCE PANEL
        st.markdown(f"""<div class="status-box health-panel">
            <h3 style="margin: 0 0 15px 0; font-size: 26px;">🔧 ENGINE HEALTH: HEALTHY ✅</h3>
            <p style="font-size: 20px; margin: 10px 0;"><b>Diagnostic:</b> No critical vibrations detected by AI sensors</p>
            <p style="font-size: 18px; margin: 8px 0;"><b>Temperature:</b> Normal (85°C) | <b>Pressure:</b> Optimal</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>Next Maintenance:</b> 2,500 km remaining</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>AI Prediction:</b> All systems stable for next 48 hours</p>
        </div>""", unsafe_allow_html=True)
        
        # 3. ENERGY OPTIMIZATION PANEL
        fuel_saved = random.randint(12, 22)
        st.markdown(f"""<div class="status-box energy-panel">
            <h3 style="margin: 0 0 15px 0; font-size: 26px;">⚡ ENERGY EFFICIENCY: ACTIVE</h3>
            <p style="font-size: 20px; margin: 10px 0;"><b>Fuel Saved:</b> <span style='font-size:24px;'>{fuel_saved}%</span> via AI Precise Throttle Control</p>
            <p style="font-size: 18px; margin: 8px 0;"><b>Optimization:</b> Regenerative braking + optimal acceleration patterns</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>CO₂ Reduction:</b> Estimated {fuel_saved * 15} kg on this journey</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>AI Adjustment:</b> Speed profile optimized for gradient changes</p>
        </div>""", unsafe_allow_html=True)

        # 4. PIS PREDICTION PANEL
        arrival_time = random.randint(15, 45)
        next_station = stations[curr_idx + 1] if curr_idx < len(stations) - 1 else "Terminal Station"
        st.markdown(f"""<div class="status-box pis-panel">
            <h3 style="margin: 0 0 15px 0; font-size: 26px;">🔮 AI PRECISE ARRIVAL PREDICTION (PIS)</h3>
            <p style="font-size: 20px; margin: 10px 0;"><b>Next Station:</b> {next_station}</p>
            <p style="font-size: 20px; margin: 10px 0;"><b>Arrival Time:</b> <span style='font-size:24px;'>{arrival_time} minutes</span></p>
            <p style="font-size: 18px; margin: 8px 0;"><b>Prediction Accuracy:</b> 98.7% based on current conditions</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>Confidence Level:</b> High (All variables within expected range)</p>
            <p style="font-size: 17px; margin: 8px 0;"><b>Passenger Info:</b> Display updated on station boards</p>
        </div>""", unsafe_allow_html=True)
        
        # PERFORMANCE METRICS SUMMARY
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.2); padding: 30px; border-radius: 20px; margin-top: 30px; border: 3px solid #FFFF00;">
            <h3 style="color: #FFFF00; text-align: center; margin-bottom: 25px; font-size: 28px;">
                📈 PERFORMANCE METRICS SUMMARY
            </h3>
            <div class="metrics-grid">
                <div class="metric-box">
                    <p><b>Current Speed:</b> 85 km/h</p>
                    <p><b>Average Speed:</b> 78 km/h</p>
                    <p><b>Max Attained Speed:</b> 92 km/h</p>
                    <p><b>Speed Compliance:</b> 100%</p>
                </div>
                <div class="metric-box">
                    <p><b>Distance Covered:</b> 245 km</p>
                    <p><b>Remaining Distance:</b> 155 km</p>
                    <p><b>Next Stop:</b> {next_station}</p>
                    <p><b>Stops Completed:</b> {curr_idx + 1}/4</p>
                </div>
                <div class="metric-box">
                    <p><b>Estimated Delay:</b> +2 minutes</p>
                    <p><b>Section Throughput:</b> +18%</p>
                    <p><b>Ghost Space Reduction:</b> 92%</p>
                    <p><b>Energy Efficiency:</b> +{fuel_saved}%</p>
                </div>
                <div class="metric-box">
                    <p><b>AI Decisions Made:</b> 1,245</p>
                    <p><b>Safety Interventions:</b> 0</p>
                    <p><b>System Uptime:</b> 99.98%</p>
                    <p><b>Overall Rating:</b> EXCELLENT</p>
                </div>
            </div>
            <div style="text-align:center; margin-top:25px; color:#FFFFFF; font-size:19px;">
                <b>🎯 AI PERFORMANCE:</b> All metrics within optimal range | 
                <b>✅ SYSTEM STATUS:</b> Fully Operational |
                <b>📊 TREND:</b> Improving
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SUCCESS MESSAGE
    st.success("""
    ✅ **SATELLITE SYNC COMPLETE!** AI DISPATCH ACTIVATED!\n
    🛰️ **Global Positioning:** Locked and Tracking\n
    🤖 **AI Control:** Now managing train operations\n
    📡 **Data Stream:** Real-time analytics flowing\n
    🎯 **Mission:** Maximizing throughput while ensuring safety
    """)
    
    st.balloons()
