import streamlit as st
import time
import streamlit.components.v1 as components
import random

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Train Dispatch Pro", layout="wide")

# CSS for Streamlit parts
st.markdown("""
    <style>
    /* FORCE ALL STREAMLIT TEXT BRIGHT WHITE */
    .stApp, .main .block-container, section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    
    .stApp * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* Bright headers */
    h1, h2, h3, .stTitle, .stHeader {
        color: #00FFFF !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8) !important;
        font-weight: 800 !important;
    }
    
    h1 { font-size: 42px !important; }
    h2 { font-size: 32px !important; color: #FFFF00 !important; }
    h3 { font-size: 26px !important; color: #00FF00 !important; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { 
        border-right: 3px solid #00FFFF !important;
    }
    
    .stTextInput>div>div>input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 2px solid #00FFFF !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }
    
    /* Buttons */
    .stButton>button { 
        background: linear-gradient(90deg, #000000, #222222) !important; 
        color: #00FFFF !important; 
        border: 3px solid #00FFFF !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.9) !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 65px !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(0, 100, 255, 0.3) !important;
        border-left: 6px solid #00FFFF !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }
    
    /* Columns */
    [data-testid="column"] {
        background-color: rgba(35, 35, 35, 0.95) !important;
        border: 2px solid rgba(0, 255, 255, 0.5) !important;
        padding: 25px !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.markdown("## 🛰️ Global GPS Search")
    train_id = st.text_input("Enter Train Number / ID", value="12673")
    
    st.markdown("---")
    
    st.markdown("## 💡 AI Methodology")
    st.markdown("""
    <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:12px; border-left:5px solid #00FF00;'>
    <p style='font-size:18px; margin-bottom:10px;'><b>Deep Q-Network (DQN) Implementation</b></p>
    <p style='font-size:16px;'>• <b>Minimize 'Ghost Space'</b> between trains</p>
    <p style='font-size:16px;'>• <b>Maximize Section Throughput</b> by 15-25%</p>
    <p style='font-size:16px;'>• <b>Dynamic speed adjustment</b> based on real-time conditions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**🚦 System Status: Moving Block Signaling ACTIVE**")

# 3. MAIN DASHBOARD
st.title("🚀 AI-Powered Precise Train Control System")

# Train Details
st.markdown("""
<div style='background:rgba(255,255,255,0.15); padding:30px; border-radius:20px; border:3px solid #00FFFF; margin:30px 0;'>
    <h2 style='color:#00FFFF; text-align:center;'>📊 TRAIN 12673 - LIVE DETAILS</h2>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px;">
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
            <p style='font-size:18px;'><b>🚂 Train ID:</b> 12673</p>
            <p style='font-size:18px;'><b>📍 Current Location:</b> En Route</p>
            <p style='font-size:18px;'><b>🎯 Destination:</b> Jolarpettai Jn</p>
        </div>
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:10px;'>
            <p style='font-size:18px;'><b>⚡ Current Speed:</b> 85 km/h</p>
            <p style='font-size:18px;'><b>📏 Distance Covered:</b> 245 km</p>
            <p style='font-size:18px;'><b>⏱️ AI Control:</b> ACTIVE</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🛰️ SYNC LIVE SATELLITE & START AI DISPATCH"):
    weather_list = [
        ("Heavy Rain 🌧️", 28.5, "Increased safety gap due to reduced visibility"),
        ("Dense Fog 🌫️", 34.0, "Extended braking distance required"),
        ("Clear Sky ☀️", 12.0, "Optimal conditions for maximum throughput")
    ]
    weather, gap, condition_note = random.choice(weather_list)
    
    with st.spinner("🛰️ CONNECTING TO GLOBAL SATELLITE FEED..."):
        time.sleep(2)
        
    col_map, col_data = st.columns([1, 1.3])

    with col_map:
        st.subheader("📍 REAL-TIME GPS TRACKING")
        
        # COMPLETE HTML/CSS WITH BRIGHT TEXT
        track_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                /* ========== FORCE ALL TEXT BRIGHT WHITE ========== */
                * {
                    color: #FFFFFF !important;
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Arial', sans-serif;
                }
                
                body {
                    background-color: #000000 !important;
                    color: #FFFFFF !important;
                    padding: 15px;
                }
                
                .tracker-container {
                    background: rgba(30, 30, 30, 0.95);
                    border: 3px solid #00FFFF;
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 0 25px rgba(0, 255, 255, 0.4);
                }
                
                /* HEADER - BRIGHT CYAN */
                .tracker-header {
                    color: #00FFFF !important;
                    text-shadow: 0 0 15px rgba(0, 255, 255, 0.9) !important;
                    font-weight: 900 !important;
                    font-size: 28px !important;
                    text-align: center !important;
                    margin-bottom: 25px !important;
                    padding-bottom: 15px !important;
                    border-bottom: 2px solid #00FFFF !important;
                }
                
                /* STATION TRACKER */
                .station-tracker {
                    position: relative;
                    padding-left: 40px;
                }
                
                /* VERTICAL LINE */
                .vertical-line {
                    position: absolute;
                    left: 18px;
                    top: 0;
                    width: 4px;
                    height: 100%;
                    background: linear-gradient(to bottom, #00FFFF, #444444);
                    z-index: 1;
                }
                
                /* STATION NODE */
                .station-node {
                    position: relative;
                    margin-bottom: 35px;
                    padding-left: 35px;
                    z-index: 2;
                }
                
                /* STATION NAME - BRIGHT WHITE */
                .station-name {
                    color: #FFFFFF !important;
                    font-size: 24px !important;
                    font-weight: 800 !important;
                    text-shadow: 0 0 8px rgba(255, 255, 255, 0.8) !important;
                    margin-bottom: 10px !important;
                    letter-spacing: 0.5px;
                }
                
                /* TRAIN ICON */
                .train-icon {
                    position: absolute;
                    left: -28px;
                    top: 0;
                    font-size: 36px;
                    z-index: 3;
                }
                
                .train-icon.active {
                    color: #00FFFF !important;
                    text-shadow: 0 0 12px rgba(0, 255, 255, 0.9) !important;
                    animation: blink 1s infinite;
                }
                
                .train-icon.upcoming {
                    color: #666666 !important;
                }
                
                /* STATUS BADGES */
                .status-badge {
                    display: inline-block;
                    padding: 8px 15px;
                    border-radius: 8px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }
                
                .status-live {
                    color: #FFFF00 !important;
                    background-color: rgba(255, 255, 0, 0.15) !important;
                    border: 2px solid #FFFF00 !important;
                    font-size: 18px !important;
                    text-shadow: 0 0 10px rgba(255, 255, 0, 0.9) !important;
                    animation: pulse 1.5s infinite;
                }
                
                .status-upcoming {
                    color: #00FF00 !important;
                    background-color: rgba(0, 255, 0, 0.1) !important;
                    border: 2px solid #00FF00 !important;
                    font-size: 17px !important;
                    text-shadow: 0 0 8px rgba(0, 255, 0, 0.8) !important;
                }
                
                /* DETAILS TEXT - BRIGHT */
                .station-details {
                    color: #FFFFFF !important;
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    text-shadow: 0 0 4px rgba(255, 255, 255, 0.6) !important;
                    margin-top: 5px;
                    padding-left: 5px;
                }
                
                .station-details strong {
                    color: #00FFFF !important;
                    text-shadow: 0 0 6px rgba(0, 255, 255, 0.8) !important;
                }
                
                /* SATELLITE INFO */
                .satellite-info {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #00FFFF;
                    text-align: center;
                }
                
                .satellite-text {
                    color: #FFFFFF !important;
                    font-size: 18px !important;
                    font-weight: 700 !important;
                    text-shadow: 0 0 5px rgba(255, 255, 255, 0.7) !important;
                    margin: 8px 0;
                }
                
                .satellite-highlight {
                    color: #00FFFF !important;
                    text-shadow: 0 0 8px rgba(0, 255, 255, 0.8) !important;
                    font-weight: 800 !important;
                }
                
                /* ANIMATIONS */
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
                
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
                
                /* PROGRESS DOT */
                .progress-dot {
                    position: absolute;
                    left: 15px;
                    width: 12px;
                    height: 12px;
                    background-color: #00FFFF;
                    border-radius: 50%;
                    z-index: 4;
                    box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
                }
                
            </style>
        </head>
        <body>
            <div class="tracker-container">
                <h1 class="tracker-header">🚅 LIVE TRAIN POSITION TRACKER</h1>
                
                <div class="station-tracker">
                    <div class="vertical-line"></div>
                    
                    <!-- Progress dot -->
                    <div class="progress-dot" style="top: 25px;"></div>
                    
                    <!-- Station 1: Chennai Central (ACTIVE) -->
                    <div class="station-node">
                        <div class="train-icon active">🚅</div>
                        <div class="station-name">Chennai Central</div>
                        <div class="status-badge status-live">● LIVE NOW - ACTIVE TRACKING</div>
                        <div class="station-details">
                            Last update: <strong>Just now</strong> | Signal: <strong>Strong</strong><br>
                            Speed: <strong>85 km/h</strong> | GPS Accuracy: <strong>±5 meters</strong>
                        </div>
                    </div>
                    
                    <!-- Station 2: Arakkonam Jn (UPCOMING) -->
                    <div class="station-node">
                        <div class="train-icon upcoming">○</div>
                        <div class="station-name">Arakkonam Jn</div>
                        <div class="status-badge status-upcoming">⏰ UPCOMING - SCHEDULED</div>
                        <div class="station-details">
                            ETA: <strong>Based on current speed</strong><br>
                            Estimated Arrival: <strong>45 minutes</strong> | Distance: <strong>68 km</strong>
                        </div>
                    </div>
                    
                    <!-- Station 3: Katpadi Jn (UPCOMING) -->
                    <div class="station-node">
                        <div class="train-icon upcoming">○</div>
                        <div class="station-name">Katpadi Jn</div>
                        <div class="status-badge status-upcoming">⏰ UPCOMING - SCHEDULED</div>
                        <div class="station-details">
                            ETA: <strong>Based on current speed</strong><br>
                            Estimated Arrival: <strong>1 hour 15 minutes</strong> | Distance: <strong>112 km</strong>
                        </div>
                    </div>
                    
                    <!-- Station 4: Jolarpettai Jn (UPCOMING) -->
                    <div class="station-node">
                        <div class="train-icon upcoming">○</div>
                        <div class="station-name">Jolarpettai Jn</div>
                        <div class="status-badge status-upcoming">⏰ UPCOMING - SCHEDULED</div>
                        <div class="station-details">
                            ETA: <strong>Based on current speed</strong><br>
                            Estimated Arrival: <strong>2 hours 10 minutes</strong> | Distance: <strong>185 km</strong>
                        </div>
                    </div>
                </div>
                
                <div class="satellite-info">
                    <p class="satellite-text">
                        <span class="satellite-highlight">📡 Satellite Connection:</span> Active | 
                        <span class="satellite-highlight">🎯 GPS Accuracy:</span> ±5 meters | 
                        <span class="satellite-highlight">⏱️ Update Frequency:</span> 30 seconds
                    </p>
                    <p class="satellite-text">
                        <span class="satellite-highlight">🛰️ Satellites:</span> GPS (8), GLONASS (6), Galileo (4) | 
                        <span class="satellite-highlight">📍 Coordinates:</span> 13.0827° N, 80.2707° E | 
                        <span class="satellite-highlight">⚡ Signal:</span> Excellent
                    </p>
                </div>
            </div>
            
            <script>
                // Update time display
                function updateTime() {
                    const now = new Date();
                    const timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    const timeElements = document.querySelectorAll('.station-details strong');
                    
                    timeElements.forEach(el => {
                        if (el.textContent.includes('Just now')) {
                            el.textContent = 'Just now (' + timeStr + ')';
                        }
                    });
                }
                
                // Animate progress dot
                function animateProgress() {
                    const dot = document.querySelector('.progress-dot');
                    if (dot) {
                        const currentTop = parseInt(dot.style.top) || 25;
                        const stations = document.querySelectorAll('.station-node');
                        const activeIndex = 0; // First station is active
                        
                        if (activeIndex < stations.length) {
                            const targetTop = stations[activeIndex].offsetTop + 25;
                            dot.style.top = targetTop + 'px';
                            dot.style.transition = 'top 1s ease';
                        }
                    }
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    updateTime();
                    animateProgress();
                    
                    // Update time every 30 seconds
                    setInterval(updateTime, 30000);
                    
                    // Blink active train icon
                    setInterval(() => {
                        const activeIcon = document.querySelector('.train-icon.active');
                        if (activeIcon) {
                            activeIcon.style.opacity = activeIcon.style.opacity === '0.8' ? '1' : '0.8';
                        }
                    }, 800);
                });
            </script>
        </body>
        </html>
        """
        
        components.html(track_html, height=550)

    with col_data:
        st.subheader("📢 AI ANALYTICS FEED")
        
        # 1. WEATHER PANEL
        st.markdown(f"""
        <div style='background-color:rgba(173,216,230,0.95); padding:25px; border-radius:15px; border-left:10px solid #1E90FF; margin-bottom:20px;'>
            <h3 style='color:#000080; margin-top:0;'>☁️ WEATHER CONDITION: {weather}</h3>
            <p style='color:#000080; font-size:18px;'><b>AI Action:</b> Safety gap optimized to <span style='font-size:22px;'>{gap} km</span></p>
            <p style='color:#000080; font-size:16px;'><b>Condition Note:</b> {condition_note}</p>
            <p style='color:#000080; font-size:16px;'><b>Satellite Data:</b> Integrated from NOAA-20 & GOES-18</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. HEALTH PANEL
        st.markdown(f"""
        <div style='background-color:rgba(255,218,185,0.95); padding:25px; border-radius:15px; border-left:10px solid #FF8C00; margin-bottom:20px;'>
            <h3 style='color:#8B0000; margin-top:0;'>🔧 ENGINE HEALTH: HEALTHY ✅</h3>
            <p style='color:#8B0000; font-size:18px;'><b>Diagnostic:</b> No critical vibrations detected</p>
            <p style='color:#8B0000; font-size:16px;'><b>Temperature:</b> Normal (85°C) | <b>Pressure:</b> Optimal</p>
            <p style='color:#8B0000; font-size:16px;'><b>Next Maintenance:</b> 2,500 km remaining</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. ENERGY PANEL
        fuel_saved = random.randint(12, 22)
        st.markdown(f"""
        <div style='background-color:rgba(144,238,144,0.95); padding:25px; border-radius:15px; border-left:10px solid #32CD32; margin-bottom:20px;'>
            <h3 style='color:#006400; margin-top:0;'>⚡ ENERGY EFFICIENCY: ACTIVE</h3>
            <p style='color:#006400; font-size:18px;'><b>Fuel Saved:</b> <span style='font-size:22px;'>{fuel_saved}%</span> via AI Throttle Control</p>
            <p style='color:#006400; font-size:16px;'><b>Optimization:</b> Regenerative braking + optimal acceleration</p>
            <p style='color:#006400; font-size:16px;'><b>CO₂ Reduction:</b> Estimated {fuel_saved * 15}
        
