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

# -------------------- Generate 1000+ Realistic Indian Trains --------------------
def generate_train_data(num_trains=1050):
    """
    Generate a list of realistic Indian trains with numbers and names.
    No external files needed – all data is embedded.
    """
    # Extended list of Indian cities/stations (100+ cities)
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
    
    # Train types and their typical speed ranges
    train_types = [
        ("Rajdhani Express", 85, 95),
        ("Shatabdi Express", 90, 100),
        ("Duronto Express", 85, 95),
        ("Garib Rath", 70, 80),
        ("Humsafar Express", 75, 85),
        ("Superfast Express", 70, 85),
        ("Express", 60, 75),
        ("Mail", 55, 70),
        ("Passenger", 40, 55),
        ("Jan Shatabdi", 65, 75),
        ("Intercity Express", 60, 70),
        ("Antyodaya Express", 70, 80),
        ("Tejas Express", 90, 100),
        ("Uday Express", 80, 90),
        ("Mahamana Express", 75, 85),
        ("Kavi Guru Express", 70, 80),
        ("Vivek Express", 65, 75),
        ("Yuva Express", 75, 85)
    ]
    
    trains = []
    used_numbers = set()
    
    # Use a progress bar for generation
    progress_bar = st.progress(0, text="Generating 1000+ trains...")
    
    for i in range(num_trains):
        # Update progress every 100 trains
        if i % 100 == 0:
            progress_bar.progress(i / num_trains)
        
        # Pick random city pair (or single city) for name
        city1 = np.random.choice(cities)
        city2 = np.random.choice(cities)
        while city2 == city1:
            city2 = np.random.choice(cities)
        
        # Random train type
        type_idx = np.random.randint(len(train_types))
        type_name, speed_min, speed_max = train_types[type_idx]
        
        # Construct name
        name_style = np.random.random()
        if name_style < 0.4:
            name = f"{city1} {city2} {type_name}"
        elif name_style < 0.7:
            name = f"{city1} {type_name}"
        else:
            name = f"{city1} - {city2} {type_name}"
        
        # Generate unique train number (Indian style: 1xxxx, 2xxxx)
        base = np.random.choice([1, 2]) * 10000
        number = base + np.random.randint(1001, 9999)
        
        # Ensure uniqueness
        while number in used_numbers:
            number = base + np.random.randint(1001, 9999)
        used_numbers.add(number)
        
        # Base speed
        base_speed = np.random.uniform(speed_min, speed_max)
        
        trains.append({
            "number": str(number),
            "name": name,
            "base_speed": round(base_speed, 1)
        })
    
    progress_bar.progress(1.0)
    time.sleep(0.5)
    progress_bar.empty()
    
    # Assign random positions along 20 km section
    np.random.seed(42)
    positions = np.random.uniform(0, 20, size=len(trains))
    speeds = [t["base_speed"] + np.random.randint(-5, 6) for t in trains]
    for i, t in enumerate(trains):
        t["position_km"] = positions[i]
        t["speed_kmh"] = max(30, min(100, speeds[i]))  # clamp to 30-100
    
    # Sort by position
    trains.sort(key=lambda x: x["position_km"])
    return trains

# -------------------- AI Environment for Training --------------------
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

        self.lead_pos = min(self.lead_pos, 20.0)
        self.ego_pos = min(self.ego_pos, 20.0)
        self.follow_pos = min(self.follow_pos, 20.0)

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

# -------------------- Train or Load DQN Model --------------------
@st.cache_resource
def load_or_train_model():
    model_path = "dqn_train_control.zip"
    if os.path.exists(model_path):
        model = DQN.load(model_path)
    else:
        env = DummyVecEnv([lambda: SingleTrainControlEnv()])
        model = DQN("MlpPolicy", env, verbose=0, learning_rate=0.001, buffer_size=10000,
                    learning_starts=100, batch_size=32, tau=0.1, gamma=0.99,
                    train_freq=4, gradient_steps=1)
        with st.spinner("Training AI model (first run only)..."):
            model.learn(total_timesteps=5000)
            model.save(model_path)
    return model

# -------------------- Helper: Find Front/Back Trains --------------------
def get_front_back(trains, selected_index):
    """Return distances (km) to next train ahead and behind, ensuring non-negative."""
    front_dist = None
    back_dist = None
    if selected_index < len(trains) - 1:
        front_dist = trains[selected_index + 1]["position_km"] - trains[selected_index]["position_km"]
        front_dist = max(0, front_dist)  # ensure non-negative
    if selected_index > 0:
        back_dist = trains[selected_index]["position_km"] - trains[selected_index - 1]["position_km"]
        back_dist = max(0, back_dist)
    return front_dist, back_dist

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="AI Train Control - Indian Railways", layout="wide")
st.title("🚉 Maximizing Section Throughput with AI (Indian Railways)")
st.markdown("---")

# Initialize session state for train data
if "trains" not in st.session_state:
    st.session_state.trains = generate_train_data(1050)  # generate 1050 trains
    st.session_state.selected_idx = 0

# Load AI model
model = load_or_train_model()

# Sidebar: Train selection
st.sidebar.header("Select Your Train")

# For large number of trains, use a searchable selectbox
train_options = [f"{t['number']} - {t['name']}" for t in st.session_state.trains]
selected_train = st.sidebar.selectbox(
    "Train Number/Name",
    train_options,
    index=st.session_state.selected_idx,
    placeholder="Type to search..."
)
selected_idx = train_options.index(selected_train)
st.session_state.selected_idx = selected_idx

# Display current train info
train = st.session_state.trains[selected_idx]
front_dist, back_dist = get_front_back(st.session_state.trains, selected_idx)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Speed", f"{train['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Train Ahead Distance", f"{front_dist:.2f} km" if front_dist is not None else "No train")
with col3:
    st.metric("Train Behind Distance", f"{back_dist:.2f} km" if back_dist is not None else "No train")

# Track Visualization (clean, only neighbors labeled)
st.subheader("Track View (0 to 20 km)")
fig, ax = plt.subplots(figsize=(12, 2))

# Draw track line
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2)

# Plot all trains as small light dots (low alpha to avoid clutter)
positions = [t['position_km'] for t in st.session_state.trains]
ax.scatter(positions, [0]*len(positions), c='lightblue', s=20, alpha=0.3, zorder=1)

# Highlight selected train in red
ax.scatter(train['position_km'], 0, c='red', s=120, zorder=3, edgecolors='darkred', linewidth=2)
ax.text(train['position_km'], 0.05, train['number'], ha='center', fontsize=9, fontweight='bold')

# Annotate front train if exists
if front_dist is not None and selected_idx < len(st.session_state.trains)-1:
    front_train = st.session_state.trains[selected_idx+1]
    ax.scatter(front_train['position_km'], 0, c='orange', s=80, zorder=2)
    ax.text(front_train['position_km'], -0.08, front_train['number'], ha='center', fontsize=8, color='orange')

# Annotate back train if exists
if back_dist is not None and selected_idx > 0:
    back_train = st.session_state.trains[selected_idx-1]
    ax.scatter(back_train['position_km'], 0, c='orange', s=80, zorder=2)
    ax.text(back_train['position_km'], -0.08, back_train['number'], ha='center', fontsize=8, color='orange')

ax.set_xlim(0, 20)
ax.set_ylim(-0.2, 0.2)
ax.set_yticks([])
ax.set_xlabel("Position (km)")
ax.set_title(f"Train Positions ({len(st.session_state.trains)} trains on track)")

st.pyplot(fig)

# AI Recommendation Button
if st.button("🚦 Get AI Speed Recommendation"):
    try:
        # Prepare observation
        min_speed, max_speed = 30, 100
        speed_norm = (train['speed_kmh'] - min_speed) / (max_speed - min_speed)
        # Use safe defaults if distances are None
        front_val = front_dist if front_dist is not None else 10.0
        back_val = back_dist if back_dist is not None else 10.0
        front_norm = min(front_val / 10.0, 1.0)
        back_norm = min(back_val / 10.0, 1.0)
        obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

        # Predict action
        action, _ = model.predict(obs, deterministic=True)
        # Ensure action is a scalar integer
        if isinstance(action, np.ndarray):
            action = action.item()

        # Map action to speed change
        speed_change = {0: -5, 1: 0, 2: 5}[action]
        new_speed = train['speed_kmh'] + speed_change
        new_speed = np.clip(new_speed, min_speed, max_speed)

        # Simulate one time step (1 second)
        time_step = 1/3600  # hours
        for t in st.session_state.trains:
            t['position_km'] += t['speed_kmh'] * time_step
            t['position_km'] = np.clip(t['position_km'], 0, 20)

        # Update selected train's speed
        st.session_state.trains[selected_idx]['speed_kmh'] = new_speed

        # Re-sort trains by position
        st.session_state.trains.sort(key=lambda x: x['position_km'])
        # Find new index of selected train
        new_idx = None
        for i, t in enumerate(st.session_state.trains):
            if t['number'] == train['number']:
                new_idx = i
                break
        if new_idx is not None:
            st.session_state.selected_idx = new_idx

        # Get updated distances
        new_front, new_back = get_front_back(st.session_state.trains, st.session_state.selected_idx)

        # Format output safely
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

        # Optional: Show action taken
        action_names = {0: "BRAKE", 1: "COAST", 2: "ACCELERATE"}
        st.caption(f"AI action: {action_names[action]}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please try again or reload the app.")

st.markdown("---")
st.caption(f"✅ AI model trained to maintain 1.5–3 km headway. Currently {len(st.session_state.trains)} trains on the track.")
