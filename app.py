import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import os
import time
from datetime import datetime
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv

# -------------------- Real-Time Data Fetching --------------------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_train_status(train_number):
    """
    Fetch live status for a specific train using RapidAPI
    """
    try:
        # You'll need to sign up at https://rapidapi.com/rahilkhan224/api/indian-railway-irctc/
        api_key = st.secrets.get("RAPIDAPI_KEY", os.environ.get("RAPIDAPI_KEY", "demo_key"))
        
        if api_key == "demo_key":
            # Return mock data if no API key
            return generate_mock_live_status(train_number)
        
        url = "https://indian-railway-irctc.p.rapidapi.com/api/trains/v1/train/status"
        
        # Use today's date
        today = datetime.now().strftime("%Y%m%d")
        
        querystring = {
            "departure_date": today,
            "isH5": "true",
            "client": "web",
            "train_number": train_number
        }
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "indian-railway-irctc.p.rapidapi.com",
            "x-rapid-api": "rapid-api-database"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API returned status {response.status_code}. Using mock data.")
            return generate_mock_live_status(train_number)
            
    except Exception as e:
        st.warning(f"Error fetching live data: {e}. Using mock data.")
        return generate_mock_live_status(train_number)

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_train_schedule(train_number):
    """
    Fetch train schedule using RapidAPI
    """
    try:
        api_key = st.secrets.get("RAPIDAPI_KEY", os.environ.get("RAPIDAPI_KEY", "demo_key"))
        
        if api_key == "demo_key":
            return generate_mock_schedule(train_number)
        
        url = f"https://indian-railway-irctc.p.rapidapi.com/api/trains-search/v1/train/{train_number}"
        
        querystring = {
            "isH5": "true",
            "client": "web"
        }
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "indian-railway-irctc.p.rapidapi.com",
            "x-rapid-api": "rapid-api-database"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            return response.json()
        else:
            return generate_mock_schedule(train_number)
            
    except Exception as e:
        return generate_mock_schedule(train_number)

def generate_mock_live_status(train_number):
    """Generate mock live status for demo when API key not available"""
    return {
        "train_number": train_number,
        "current_speed": np.random.randint(45, 85),
        "position_km": np.random.uniform(0, 20),
        "delay_minutes": np.random.randint(-5, 15),
        "last_station": "Mumbai Central",
        "next_station": "Vadodara"
    }

def generate_mock_schedule(train_number):
    """Generate mock schedule for demo"""
    return {
        "train_number": train_number,
        "stations": [
            {"name": "Mumbai Central", "arrival": "06:00", "departure": "06:10"},
            {"name": "Vadodara", "arrival": "10:30", "departure": "10:35"},
            {"name": "Ratlam", "arrival": "13:45", "departure": "13:50"},
            {"name": "Kota", "arrival": "17:20", "departure": "17:25"},
            {"name": "Delgi Hazrat Nizamuddin", "arrival": "21:30", "departure": "Terminus"}
        ]
    }

# -------------------- Extended Indian Train Data --------------------
def generate_train_list():
    """Return a list of 30 realistic Indian trains with their numbers"""
    trains = [
        {"number": "12951", "name": "Mumbai Rajdhani", "base_speed": 85},
        {"number": "12301", "name": "Howrah Rajdhani", "base_speed": 80},
        {"number": "12431", "name": "Thiruvananthapuram Rajdhani", "base_speed": 80},
        {"number": "12627", "name": "Karnataka Express", "base_speed": 75},
        {"number": "12649", "name": "Sampark Kranti Express", "base_speed": 78},
        {"number": "12953", "name": "August Kranti Rajdhani", "base_speed": 82},
        {"number": "12295", "name": "Sanghamitra Express", "base_speed": 70},
        {"number": "12801", "name": "Puri Express", "base_speed": 65},
        {"number": "12426", "name": "Bhubaneswar Rajdhani", "base_speed": 72},
        {"number": "12577", "name": "Mysuru Express", "base_speed": 68},
        {"number": "12615", "name": "Kerala Express", "base_speed": 73},
        {"number": "12723", "name": "Andhra Pradesh Express", "base_speed": 79},
        {"number": "12839", "name": "Chennai Mail", "base_speed": 71},
        {"number": "12646", "name": "Ernakulam Express", "base_speed": 69},
        {"number": "11013", "name": "Coimbatore Express", "base_speed": 66},
        {"number": "12622", "name": "Tamil Nadu Express", "base_speed": 77},
        {"number": "12835", "name": "Hatia Express", "base_speed": 70},
        {"number": "12609", "name": "Bangalore Express", "base_speed": 72},
        {"number": "12002", "name": "Shatabdi Express", "base_speed": 84},
        {"number": "12245", "name": "Duronto Express", "base_speed": 79},
        {"number": "12559", "name": "Garib Rath", "base_speed": 73},
        {"number": "12741", "name": "Humsafar Express", "base_speed": 77},
        {"number": "11019", "name": "Konark Express", "base_speed": 68},
        {"number": "12427", "name": "Prayagraj Express", "base_speed": 70},
        {"number": "12658", "name": "Ganga Kaveri Express", "base_speed": 68},
        {"number": "12213", "name": "YPR Duronto", "base_speed": 75},
        {"number": "12614", "name": "Mysuru Express", "base_speed": 72},
        {"number": "12675", "name": "Kovai Express", "base_speed": 80},
        {"number": "12641", "name": "Thirukkural Express", "base_speed": 78},
        {"number": "11027", "name": "Chennai Express", "base_speed": 71}
    ]
    return trains

# -------------------- Realistic Train Environment --------------------
class RealisticTrainEnv(gym.Env):
    """
    Realistic single-train control with acceleration limits and train length.
    """
    def __init__(self, max_speed_kmh=100, min_speed_kmh=30, train_length_km=0.2, dt=1.0):
        super().__init__()
        self.max_speed_kmh = max_speed_kmh
        self.min_speed_kmh = min_speed_kmh
        self.train_length_km = train_length_km
        self.dt = dt / 3600.0

        self.accel_rate = 1.8
        self.brake_rate = -3.6

        self.action_space = spaces.Discrete(3)
        high = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=high, dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.lead_pos = 15.0
        self.ego_pos = 10.0
        self.follow_pos = 5.0
        self.lead_speed = 65.0
        self.ego_speed = 60.0
        self.follow_speed = 55.0
        return self._get_obs(), {}

    def _get_obs(self):
        speed_norm = (self.ego_speed - self.min_speed_kmh) / (self.max_speed_kmh - self.min_speed_kmh)
        front_dist = max(0, self.lead_pos - self.ego_pos - self.train_length_km)
        back_dist = max(0, self.ego_pos - self.follow_pos - self.train_length_km)
        front_norm = min(front_dist / 10.0, 1.0)
        back_norm = min(back_dist / 10.0, 1.0)
        return np.array([speed_norm, front_norm, back_norm], dtype=np.float32)

    def step(self, action):
        if action == 0:
            self.ego_speed += self.brake_rate * self.dt * 3600
        elif action == 2:
            self.ego_speed += self.accel_rate * self.dt * 3600
        
        self.ego_speed = np.clip(self.ego_speed, self.min_speed_kmh, self.max_speed_kmh)

        # Lead and follow trains with random actions
        for train_speed in ['lead', 'follow']:
            rand_action = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
            if train_speed == 'lead':
                if rand_action == -1:
                    self.lead_speed += self.brake_rate * self.dt * 3600
                elif rand_action == 1:
                    self.lead_speed += self.accel_rate * self.dt * 3600
                self.lead_speed = np.clip(self.lead_speed, self.min_speed_kmh, self.max_speed_kmh)
            else:
                if rand_action == -1:
                    self.follow_speed += self.brake_rate * self.dt * 3600
                elif rand_action == 1:
                    self.follow_speed += self.accel_rate * self.dt * 3600
                self.follow_speed = np.clip(self.follow_speed, self.min_speed_kmh, self.max_speed_kmh)

        self.lead_pos += self.lead_speed * self.dt
        self.ego_pos += self.ego_speed * self.dt
        self.follow_pos += self.follow_speed * self.dt

        self.lead_pos = np.clip(self.lead_pos, 0, 20)
        self.ego_pos = np.clip(self.ego_pos, 0, 20)
        self.follow_pos = np.clip(self.follow_pos, 0, 20)

        front_dist = self.lead_pos - self.ego_pos - self.train_length_km
        back_dist = self.ego_pos - self.follow_pos - self.train_length_km

        reward = 0

        if front_dist < 0.5:
            reward -= 10
        elif front_dist < 1.0:
            reward -= 5
        elif 1.0 <= front_dist <= 2.5:
            reward += 5
        elif front_dist > 5.0:
            reward -= 2

        if back_dist < 0.5:
            reward -= 5

        speed_factor = (self.ego_speed - self.min_speed_kmh) / (self.max_speed_kmh - self.min_speed_kmh)
        reward += 2 * speed_factor

        if action != 1:
            reward -= 0.5

        done = False
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

# -------------------- Train or Load DQN Model --------------------
@st.cache_resource
def load_or_train_model():
    model_path = "dqn_realistic.zip"
    if os.path.exists(model_path):
        model = DQN.load(model_path)
    else:
        env = DummyVecEnv([lambda: RealisticTrainEnv()])
        model = DQN("MlpPolicy", env, verbose=0, learning_rate=0.001, buffer_size=10000,
                    learning_starts=100, batch_size=32, tau=0.1, gamma=0.99,
                    train_freq=4, gradient_steps=1)
        with st.spinner("Training AI model for realistic dynamics..."):
            model.learn(total_timesteps=8000)
            model.save(model_path)
    return model

# -------------------- Helper Functions --------------------
def get_front_back(trains, selected_idx):
    """Calculate distances between trains"""
    front_dist = None
    back_dist = None
    if selected_idx < len(trains) - 1:
        front_dist = trains[selected_idx + 1]["position_km"] - trains[selected_idx]["position_km"] - 0.2
    if selected_idx > 0:
        back_dist = trains[selected_idx]["position_km"] - trains[selected_idx - 1]["position_km"] - 0.2
    return front_dist, back_dist

def update_train_positions(trains, time_step=1/3600):
    """Update positions based on current speeds"""
    for t in trains:
        t['position_km'] += t['speed_kmh'] * time_step
        t['position_km'] = np.clip(t['position_km'], 0, 20)
    trains.sort(key=lambda x: x['position_km'])
    return trains

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="Real-Time AI Train Control", layout="wide")
st.title("🚄 Real-Time AI Train Control System (Indian Railways)")
st.markdown("---")

# Sidebar for API configuration
with st.sidebar.expander("🔧 API Configuration"):
    api_key = st.text_input("RapidAPI Key", type="password", 
                           help="Get your free key from https://rapidapi.com/rahilkhan224/api/indian-railway-irctc/")
    if api_key:
        os.environ["RAPIDAPI_KEY"] = api_key
        st.success("API key set!")

# Initialize train list
if "train_list" not in st.session_state:
    st.session_state.train_list = generate_train_list()

# Train selection
st.sidebar.header("Select Your Train")
train_options = [f"{t['number']} - {t['name']}" for t in st.session_state.train_list]
selected_train_display = st.sidebar.selectbox("Train Number/Name", train_options)
selected_train_number = selected_train_display.split(" - ")[0]

# Fetch real-time data for selected train
with st.spinner("Fetching real-time train data..."):
    live_data = fetch_live_train_status(selected_train_number)
    schedule_data = fetch_train_schedule(selected_train_number)

# Create a list of trains with their current positions
if "trains" not in st.session_state or st.session_state.get("last_train") != selected_train_number:
    # Initialize with real data plus random other trains
    np.random.seed(int(selected_train_number) % 1000)
    
    trains = []
    # Add the selected train with real data
    trains.append({
        "number": selected_train_number,
        "name": selected_train_display.split(" - ")[1],
        "position_km": live_data.get("position_km", np.random.uniform(5, 15)),
        "speed_kmh": live_data.get("current_speed", np.random.uniform(45, 85))
    })
    
    # Add 9 other random trains
    other_trains = [t for t in st.session_state.train_list if t['number'] != selected_train_number]
    selected_others = np.random.choice(len(other_trains), min(9, len(other_trains)), replace=False)
    
    for idx in selected_others:
        t = other_trains[idx]
        trains.append({
            "number": t['number'],
            "name": t['name'],
            "position_km": np.random.uniform(0, 20),
            "speed_kmh": t['base_speed'] + np.random.randint(-5, 6)
        })
    
    trains.sort(key=lambda x: x['position_km'])
    st.session_state.trains = trains
    st.session_state.last_train = selected_train_number

# Find selected train index
selected_idx = None
for i, t in enumerate(st.session_state.trains):
    if t['number'] == selected_train_number:
        selected_idx = i
        break

if selected_idx is None:
    st.error("Selected train not found in current simulation")
    st.stop()

train = st.session_state.trains[selected_idx]
front_dist, back_dist = get_front_back(st.session_state.trains, selected_idx)

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Speed", f"{train['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Train Ahead", f"{front_dist:.2f} km" if front_dist else "No train")
with col3:
    st.metric("Train Behind", f"{back_dist:.2f} km" if back_dist else "No train")
with col4:
    delay = live_data.get("delay_minutes", 0)
    st.metric("Delay", f"{delay} min", delta=f"{delay} min" if delay != 0 else "On time")

# Live status details
with st.expander("📊 Live Train Details"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Train Number:** {live_data.get('train_number', selected_train_number)}")
        st.write(f"**Last Station:** {live_data.get('last_station', 'Mumbai Central')}")
    with col2:
        st.write(f"**Next Station:** {live_data.get('next_station', 'Vadodara')}")
        st.write(f"**Delay:** {live_data.get('delay_minutes', 0)} minutes")

# Track visualization
st.subheader("🚆 Track View (0 to 20 km)")
fig, ax = plt.subplots(figsize=(12, 2))

# Draw track
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2)

# Plot all trains
positions = [t['position_km'] for t in st.session_state.trains]
ax.scatter(positions, [0]*len(positions), c='lightblue', s=40, alpha=0.7, zorder=1)

# Highlight selected train
ax.scatter(train['position_km'], 0, c='red', s=150, zorder=3, edgecolors='darkred', linewidth=2)
ax.text(train['position_km'], 0.06, f"{train['number']}\n{train['speed_kmh']:.0f} km/h", 
        ha='center', fontsize=9, fontweight='bold')

# Annotate neighbors
if front_dist is not None and selected_idx < len(st.session_state.trains)-1:
    front_train = st.session_state.trains[selected_idx+1]
    ax.scatter(front_train['position_km'], 0, c='orange', s=100, zorder=2)
    ax.text(front_train['position_km'], -0.08, front_train['number'], 
            ha='center', fontsize=8, color='orange')

if back_dist is not None and selected_idx > 0:
    back_train = st.session_state.trains[selected_idx-1]
    ax.scatter(back_train['position_km'], 0, c='orange', s=100, zorder=2)
    ax.text(back_train['position_km'], -0.08, back_train['number'], 
            ha='center', fontsize=8, color='orange')

ax.set_xlim(0, 20)
ax.set_ylim(-0.15, 0.15)
ax.set_yticks([])
ax.set_xlabel("Position (km)")
ax.set_title("Train Positions - Red: Selected, Orange: Adjacent Trains")

st.pyplot(fig)

# Load AI model
model = load_or_train_model()

# AI Recommendation Button
if st.button("🚦 Get AI Speed Recommendation", type="primary"):
    min_speed, max_speed = 30, 100
    speed_norm = (train['speed_kmh'] - min_speed) / (max_speed - min_speed)
    front_norm = min((front_dist if front_dist else 10) / 10.0, 1.0)
    back_norm = min((back_dist if back_dist else 10) / 10.0, 1.0)
    obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

    action, _ = model.predict(obs, deterministic=True)
    action = action.item()

    # Apply action
    if action == 0:
        train['speed_kmh'] -= 3.6
        action_text = "⚠️ BRAKE"
    elif action == 2:
        train['speed_kmh'] += 1.8
        action_text = "⚡ ACCELERATE"
    else:
        action_text = "➡️ COAST"

    train['speed_kmh'] = np.clip(train['speed_kmh'], min_speed, max_speed)

    # Update positions
    st.session_state.trains = update_train_positions(st.session_state.trains)
    
    # Re-find index after sorting
    for i, t in enumerate(st.session_state.trains):
        if t['number'] == train['number']:
            st.session_state.selected_idx = i
            break

    new_front, new_back = get_front_back(st.session_state.trains, st.session_state.selected_idx)
    
    front_text = f"{new_front:.2f} km" if new_front is not None else "No train"
    back_text = f"{new_back:.2f} km" if new_back is not None else "No train"

    # Display notification
    st.success("### 📢 Driver Advisory")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            f"**Train {train['number']} - {train['name']}**\n\n"
            f"🚄 **Current Speed:** {train['speed_kmh']:.0f} km/h\n"
            f"🔹 **Train Ahead:** {front_text}\n"
            f"🔸 **Train Behind:** {back_text}"
        )
    with col2:
        st.warning(
            f"**Action Recommended:** {action_text}\n\n"
            f"**Delay Status:** {delay} minutes\n"
            f"**Next Station:** {live_data.get('next_station', 'Unknown')}"
        )

    st.caption("⚠️ This is an advisory system. Driver must exercise judgment for safety.")
    st.rerun()

# Auto-refresh option
if st.sidebar.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.info(
    "**How to get a Real API Key:**\n"
    "1. Visit https://rapidapi.com/rahilkhan224/api/indian-railway-irctc/\n"
    "2. Sign up for free\n"
    "3. Subscribe to Basic plan (free tier available)\n"
    "4. Copy your API key and paste above"
)

st.markdown("---")
st.caption(
    "**Note:** Without API key, the app runs on simulated data. "
    "With API key, it fetches real-time train information from Indian Railways."
)
