import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import os
import time

# -------------------- Generate Realistic Indian Trains --------------------
def generate_train_data(num_trains=500):
    """Generate a list of Indian trains (names, numbers, base speeds)."""
    cities = [
        "Mumbai", "Delhi", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Ahmedabad",
        "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot",
        "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi",
        "Howrah", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur",
        "Kota", "Chandigarh", "Guwahati", "Solapur", "Hubli", "Mysore", "Tiruchirappalli",
        "Bareilly", "Aligarh", "Moradabad", "Bhubaneswar", "Coimbatore", "Kozhikode",
        "Thiruvananthapuram", "Mangalore", "Tirupati", "Warangal", "Guntur", "Belgaum",
        "Udaipur", "Ajmer", "Jammu", "Dehradun", "Shimla", "Panaji", "Pondicherry",
        "Kochi", "Salem", "Tuticorin", "Nellore", "Kurnool", "Kakinada", "Rajahmundry",
        "Bhavnagar", "Jamnagar", "Gandhinagar", "Siliguri", "Asansol", "Durgapur",
        "Bokaro", "Rourkela", "Sambalpur", "Jhansi", "Mathura", "Alwar",
        "Bikaner", "Jaisalmer", "Mount Abu", "Nanded", "Latur", "Osmanabad", "Kolhapur",
        "Sangli", "Ratnagiri", "Panvel", "Thane", "Kalyan", "Virar", "Vapi", "Valsad",
        "Surat", "Bharuch", "Anand", "Nadiad", "Godhra", "Dahod", "Mandsaur", "Neemuch",
        "Chittorgarh", "Bhilwara", "Tonk", "Sikar", "Jhunjhunu", "Hanumangarh", "Ganganagar",
        "Firozpur", "Pathankot", "Hoshiarpur", "Kapurthala", "Jalandhar", "Phagwara",
        "Khanna", "Sirhind", "Rajpura", "Patiala", "Sangrur", "Barnala",
        "Bathinda", "Moga", "Fazilka", "Abohar", "Malout", "Giddarbaha", "Muktsar",
        "Faridkot", "Ferozepur", "Zira", "Makhu", "Talwandi Bhai", "Mullanpur",
        "Doraha", "Sahnewal", "Halwara", "Raikot", "Jagraon", "Nakodar", "Phillaur",
        "Nurmahal", "Gorakhpur", "Gonda", "Balrampur", "Shravasti", "Bahraich",
        "Lakhimpur", "Kheri", "Sitapur", "Hardoi", "Unnao", "Raebareli", "Pratapgarh",
        "Sultanpur", "Faizabad", "Ambedkar Nagar", "Azamgarh", "Mau", "Ballia",
        "Ghazipur", "Chandauli", "Mirzapur", "Sonbhadra", "Sant Kabir Nagar",
        "Maharajganj", "Kushinagar", "Deoria", "Padrauna", "Kasia", "Basti",
        "Siddharthnagar", "Sant Ravidas Nagar", "Bhadohi", "Jaunpur", "Barabanki",
        "Ayodhya", "Amethi", "Rae Bareli", "Fatehpur", "Kaushambi"
    ]
    
    train_types = [
        ("Rajdhani Express", 85, 95), ("Shatabdi Express", 90, 100),
        ("Duronto Express", 85, 95), ("Garib Rath", 70, 80),
        ("Humsafar Express", 75, 85), ("Superfast Express", 70, 85),
        ("Express", 60, 75), ("Mail", 55, 70), ("Passenger", 40, 55),
        ("Jan Shatabdi", 65, 75), ("Intercity Express", 60, 70),
        ("Antyodaya Express", 70, 80), ("Tejas Express", 90, 100),
        ("Uday Express", 80, 90), ("Mahamana Express", 75, 85),
        ("Kavi Guru Express", 70, 80), ("Vivek Express", 65, 75),
        ("Yuva Express", 75, 85)
    ]
    
    trains = []
    used_numbers = set()
    progress_bar = st.progress(0, text=f"Generating {num_trains} trains...")
    
    for i in range(num_trains):
        if i % 50 == 0:
            progress_bar.progress(i / num_trains)
        
        city1 = np.random.choice(cities)
        city2 = np.random.choice(cities)
        while city2 == city1:
            city2 = np.random.choice(cities)
        
        type_name, speed_min, speed_max = train_types[np.random.randint(len(train_types))]
        
        r = np.random.random()
        if r < 0.4:
            name = f"{city1} {city2} {type_name}"
        elif r < 0.7:
            name = f"{city1} {type_name}"
        else:
            name = f"{city1} - {city2} {type_name}"
        
        base = np.random.choice([1, 2]) * 10000
        number = base + np.random.randint(1001, 9999)
        while number in used_numbers:
            number = base + np.random.randint(1001, 9999)
        used_numbers.add(number)
        
        base_speed = np.random.uniform(speed_min, speed_max)
        trains.append({
            "number": str(number),
            "name": name,
            "base_speed": round(base_speed, 1)
        })
    
    progress_bar.progress(1.0)
    time.sleep(0.2)
    progress_bar.empty()
    
    # Assign random positions and speeds
    np.random.seed(42)
    positions = np.random.uniform(0, 20, size=len(trains))
    speeds = [t["base_speed"] + np.random.randint(-5, 6) for t in trains]
    for i, t in enumerate(trains):
        t["position_km"] = positions[i]
        t["speed_kmh"] = np.clip(speeds[i], 30, 100)
    
    trains.sort(key=lambda x: x["position_km"])
    return trains

# -------------------- AI Environment --------------------
class SingleTrainControlEnv(gym.Env):
    def __init__(self, max_speed=100, min_speed=30, time_step=1/3600):
        super().__init__()
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.time_step = time_step
        self.action_space = spaces.Discrete(3)
        high = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=high, dtype=np.float32)
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.lead_pos = 15.0
        self.ego_pos = 10.0
        self.follow_pos = 5.0
        self.ego_speed = 60.0
        self.lead_speed = 65.0
        self.follow_speed = 55.0
        return self._get_obs(), {}

    def _get_obs(self):
        speed_norm = (self.ego_speed - self.min_speed) / (self.max_speed - self.min_speed)
        front_dist = max(0, self.lead_pos - self.ego_pos)
        back_dist = max(0, self.ego_pos - self.follow_pos)
        front_norm = min(front_dist / 10.0, 1.0)
        back_norm = min(back_dist / 10.0, 1.0)
        return np.array([speed_norm, front_norm, back_norm], dtype=np.float32)

    def step(self, action):
        if action == 0:
            self.ego_speed -= 5
        elif action == 2:
            self.ego_speed += 5
        self.ego_speed = np.clip(self.ego_speed, self.min_speed, self.max_speed)

        self.lead_speed += np.random.randint(-2, 3)
        self.lead_speed = np.clip(self.lead_speed, self.min_speed, self.max_speed)
        self.follow_speed += np.random.randint(-2, 3)
        self.follow_speed = np.clip(self.follow_speed, self.min_speed, self.max_speed)

        self.lead_pos += self.lead_speed * self.time_step
        self.ego_pos += self.ego_speed * self.time_step
        self.follow_pos += self.follow_speed * self.time_step
        self.lead_pos = np.clip(self.lead_pos, 0, 20)
        self.ego_pos = np.clip(self.ego_pos, 0, 20)
        self.follow_pos = np.clip(self.follow_pos, 0, 20)

        front_dist = self.lead_pos - self.ego_pos
        back_dist = self.ego_pos - self.follow_pos
        reward = 0

        if front_dist < 0.5:
            reward -= 10
        elif front_dist < 1.5:
            reward -= 2
        elif 1.5 <= front_dist <= 3.0:
            reward += 5
        elif front_dist > 5.0:
            reward -= 1

        if back_dist < 0.5:
            reward -= 5

        reward += 0.05 * self.ego_speed
        if action != 1:
            reward -= 0.2

        done = False
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

# -------------------- Load or Train Model --------------------
@st.cache_resource
def load_or_train_model():
    model_path = "dqn_train_control.zip"
    if os.path.exists(model_path):
        return DQN.load(model_path)
    else:
        env = DummyVecEnv([lambda: SingleTrainControlEnv()])
        model = DQN("MlpPolicy", env, verbose=0, learning_rate=0.001, buffer_size=10000,
                    learning_starts=100, batch_size=32, tau=0.1, gamma=0.99,
                    train_freq=4, gradient_steps=1)
        with st.spinner("Training AI model for the first time..."):
            model.learn(total_timesteps=5000)
            model.save(model_path)
        return model

# -------------------- Helper --------------------
def get_front_back(trains, idx):
    front = None
    back = None
    if idx < len(trains) - 1:
        front = trains[idx + 1]["position_km"] - trains[idx]["position_km"]
        front = max(0, front)
    if idx > 0:
        back = trains[idx]["position_km"] - trains[idx - 1]["position_km"]
        back = max(0, back)
    return front, back

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="AI Train Control", layout="wide")
st.title("🚉 AI-Powered Train Traffic Control (Indian Railways)")
st.markdown("---")

# Sidebar controls
st.sidebar.header("Settings")
num_trains = st.sidebar.slider("Number of trains in simulation", 100, 2000, 500, step=50,
                               help="More trains = more fun, but remember it's just a demo!")
if st.sidebar.button("🔄 Regenerate Trains"):
    st.cache_data.clear()
    st.rerun()

# Load or generate train data
@st.cache_data(ttl=600)
def get_trains(n):
    return generate_train_data(n)

if "trains" not in st.session_state:
    st.session_state.trains = get_trains(num_trains)
    st.session_state.selected_idx = 0

# Update if slider changed
if len(st.session_state.trains) != num_trains:
    st.session_state.trains = get_trains(num_trains)
    st.session_state.selected_idx = 0

# Load AI model
model = load_or_train_model()

# Train selection
st.sidebar.header("Select Your Train")
train_options = [f"{t['number']} - {t['name']}" for t in st.session_state.trains]
selected = st.sidebar.selectbox("Train Number/Name", train_options,
                                index=st.session_state.selected_idx,
                                placeholder="Type to search...")
selected_idx = train_options.index(selected)
st.session_state.selected_idx = selected_idx

train = st.session_state.trains[selected_idx]
front_dist, back_dist = get_front_back(st.session_state.trains, selected_idx)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Speed", f"{train['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Train Ahead", f"{front_dist:.2f} km" if front_dist is not None else "No train")
with col3:
    st.metric("Train Behind", f"{back_dist:.2f} km" if back_dist is not None else "No train")

# Track visualization
st.subheader("Track View (0–20 km)")
fig, ax = plt.subplots(figsize=(12, 2))
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2)
positions = [t['position_km'] for t in st.session_state.trains]
ax.scatter(positions, [0]*len(positions), c='lightblue', s=20, alpha=0.3, zorder=1)
ax.scatter(train['position_km'], 0, c='red', s=120, zorder=3, edgecolors='darkred', linewidth=2)
ax.text(train['position_km'], 0.05, train['number'], ha='center', fontsize=9, fontweight='bold')
if front_dist is not None and selected_idx < len(st.session_state.trains)-1:
    ft = st.session_state.trains[selected_idx+1]
    ax.scatter(ft['position_km'], 0, c='orange', s=80, zorder=2)
    ax.text(ft['position_km'], -0.08, ft['number'], ha='center', fontsize=8, color='orange')
if back_dist is not None and selected_idx > 0:
    bt = st.session_state.trains[selected_idx-1]
    ax.scatter(bt['position_km'], 0, c='orange', s=80, zorder=2)
    ax.text(bt['position_km'], -0.08, bt['number'], ha='center', fontsize=8, color='orange')
ax.set_xlim(0, 20)
ax.set_ylim(-0.2, 0.2)
ax.set_yticks([])
ax.set_xlabel("Position (km)")
ax.set_title(f"{len(st.session_state.trains)} trains on track (selected red, neighbours orange)")
st.pyplot(fig)

# AI Recommendation Button
if st.button("🚦 Get AI Speed Recommendation", type="primary"):
    try:
        # Prepare observation
        min_speed, max_speed = 30, 100
        speed_norm = (train['speed_kmh'] - min_speed) / (max_speed - min_speed)
        # Default to 10 km if no train ahead/behind
        f_val = front_dist if front_dist is not None else 10.0
        b_val = back_dist if back_dist is not None else 10.0
        front_norm = np.clip(f_val / 10.0, 0, 1)
        back_norm = np.clip(b_val / 10.0, 0, 1)
        obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

        # Predict action – safely handle any return type
        action, _ = model.predict(obs, deterministic=True)
        if isinstance(action, np.ndarray):
            action = action.item() if action.size == 1 else int(action[0])
        else:
            action = int(action)

        # Map action
        speed_change = {0: -5, 1: 0, 2: 5}[action]
        new_speed = train['speed_kmh'] + speed_change
        new_speed = np.clip(new_speed, min_speed, max_speed)

        # Simulate one second
        dt = 1 / 3600  # hours
        for t in st.session_state.trains:
            t['position_km'] += t['speed_kmh'] * dt
            t['position_km'] = np.clip(t['position_km'], 0, 20)

        # Update selected train speed
        st.session_state.trains[selected_idx]['speed_kmh'] = new_speed

        # Re‑sort and find new index
        st.session_state.trains.sort(key=lambda x: x['position_km'])
        new_idx = next((i for i, t in enumerate(st.session_state.trains) if t['number'] == train['number']), selected_idx)
        st.session_state.selected_idx = new_idx

        # Get updated distances
        new_front, new_back = get_front_back(st.session_state.trains, new_idx)

        # Format output
        front_text = f"{new_front:.2f} km" if new_front is not None else "No train"
        back_text = f"{new_back:.2f} km" if new_back is not None else "No train"

        # Display advisory
        st.success("### 📢 Driver Advisory")
        st.info(
            f"**Train {train['number']} - {train['name']}**\n\n"
            f"🚄 **Recommended Speed:** {new_speed:.0f} km/h\n"
            f"🔹 Train ahead at {front_text}\n"
            f"🔸 Train behind at {back_text}"
        )
        action_names = {0: "BRAKE", 1: "COAST", 2: "ACCELERATE"}
        st.caption(f"AI action: {action_names[action]}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please try again. If the problem persists, reduce the number of trains or restart the app.")

st.markdown("---")
st.caption(f"✅ Simulation running with {len(st.session_state.trains)} trains. "
           "The AI recommends speeds to maintain safe but close following distances, "
           "maximizing track throughput.")
