import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import os

# -------------------- Generate 100+ Realistic Indian Trains --------------------
def generate_train_data():
    """
    Generate a list of 100+ realistic Indian trains with numbers and names.
    No external files needed – all data is embedded.
    """
    # Base station/city names for train names
    cities = [
        "Mumbai", "Delhi", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Ahmedabad",
        "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot",
        "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi",
        "Howrah", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur",
        "Kota", "Chandigarh", "Guwahati", "Solapur", "Hubli", "Mysore", "Tiruchirappalli",
        "Bareilly", "Aligarh", "Moradabad", "Bhubaneswar", "Coimbatore", "Kozhikode"
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
        ("Passenger", 40, 55)
    ]
    
    trains = []
    train_counter = 0
    
    # Generate 100+ trains by combining cities and types
    for i in range(120):  # Generate 120 trains (a bit more than 100)
        # Pick random city pair (or single city) for name
        city1 = np.random.choice(cities)
        city2 = np.random.choice(cities)
        while city2 == city1:
            city2 = np.random.choice(cities)
        
        # Random train type
        type_name, speed_min, speed_max = train_types[np.random.randint(len(train_types))]
        
        # Construct name
        if np.random.random() > 0.5:
            name = f"{city1} {city2} {type_name}"
        else:
            name = f"{city1} {type_name}"
        
        # Generate unique train number (Indian style: 1xxxx, 2xxxx)
        base = np.random.choice([1, 2]) * 10000
        number = base + np.random.randint(1001, 9999)
        
        # Ensure uniqueness by incrementing if duplicate (simple loop)
        while any(t['number'] == str(number) for t in trains):
            number += 1
        
        # Base speed
        base_speed = np.random.uniform(speed_min, speed_max)
        
        trains.append({
            "number": str(number),
            "name": name,
            "base_speed": round(base_speed, 1)
        })
        
        train_counter += 1
        if train_counter >= 110:  # Stop at 110 trains
            break
    
    # Assign random positions along 20 km section
    np.random.seed(42)
    positions = np.random.uniform(0, 20, size=len(trains))
    speeds = [t["base_speed"] + np.random.randint(-5, 6) for t in trains]
    for i, t in enumerate(trains):
        t["position_km"] = positions[i]
        t["speed_kmh"] = speeds[i]
    
    # Sort by position
    trains.sort(key=lambda x: x["position_km"])
    return trains

# -------------------- AI Environment for Training --------------------
class SingleTrainControlEnv(gym.Env):
    """
    Environment for controlling one train (ego) with a lead train ahead and a follow train behind.
    State: [ego_speed, front_distance, back_distance] normalized.
    Action: 0 = decelerate, 1 = maintain, 2 = accelerate.
    Reward: encourage safe distance (1.5-3 km) and high speed.
    """
    def __init__(self, max_speed=100, min_speed=30, time_step=1/3600):  # 1 sec in hours
        super().__init__()
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.time_step = time_step  # hours

        # Action: 0=decel, 1=maintain, 2=accel
        self.action_space = spaces.Discrete(3)

        # Observation: [speed_norm, front_dist_norm, back_dist_norm]
        # speed: 30-100 km/h, distances: 0-10 km
        high = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=high, dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Initialize positions: lead at 15 km, ego at 10 km, follow at 5 km
        self.lead_pos = 15.0
        self.ego_pos = 10.0
        self.follow_pos = 5.0
        self.ego_speed = 60.0
        self.lead_speed = 65.0
        self.follow_speed = 55.0
        return self._get_obs(), {}

    def _get_obs(self):
        # Normalize: speed (30-100) -> (0-1), distance (0-10) -> (0-1)
        speed_norm = (self.ego_speed - self.min_speed) / (self.max_speed - self.min_speed)
        front_dist = max(0, self.lead_pos - self.ego_pos)
        back_dist = max(0, self.ego_pos - self.follow_pos)
        front_norm = min(front_dist / 10.0, 1.0)
        back_norm = min(back_dist / 10.0, 1.0)
        return np.array([speed_norm, front_norm, back_norm], dtype=np.float32)

    def step(self, action):
        # Apply action to ego speed
        if action == 0:  # decelerate
            self.ego_speed -= 5
        elif action == 2:  # accelerate
            self.ego_speed += 5
        # Keep speed within limits
        self.ego_speed = np.clip(self.ego_speed, self.min_speed, self.max_speed)

        # Simulate lead and follow speeds with some randomness
        self.lead_speed += np.random.randint(-2, 3)
        self.lead_speed = np.clip(self.lead_speed, self.min_speed, self.max_speed)
        self.follow_speed += np.random.randint(-2, 3)
        self.follow_speed = np.clip(self.follow_speed, self.min_speed, self.max_speed)

        # Update positions (distance = speed * time_step)
        self.lead_pos += self.lead_speed * self.time_step
        self.ego_pos += self.ego_speed * self.time_step
        self.follow_pos += self.follow_speed * self.time_step

        # Keep positions within 0-20 km track
        self.lead_pos = min(self.lead_pos, 20.0)
        self.ego_pos = min(self.ego_pos, 20.0)
        self.follow_pos = min(self.follow_pos, 20.0)

        # Compute reward
        front_dist = self.lead_pos - self.ego_pos
        back_dist = self.ego_pos - self.follow_pos
        reward = 0

        # Safety: very close front
        if front_dist < 0.5:
            reward -= 10
        elif front_dist < 1.5:
            reward -= 2
        elif 1.5 <= front_dist <= 3.0:
            reward += 5
        elif front_dist > 5.0:
            reward -= 1   # too far, capacity wasted

        # Rear distance also matters for safety
        if back_dist < 0.5:
            reward -= 5

        # Encourage higher speed
        reward += 0.05 * self.ego_speed

        # Small penalty for harsh actions
        if action == 0 or action == 2:
            reward -= 0.2

        done = False  # continuous, never done
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

# -------------------- Train or Load DQN Model --------------------
@st.cache_resource
def load_or_train_model():
    model_path = "dqn_train_control.zip"
    if os.path.exists(model_path):
        model = DQN.load(model_path)
    else:
        # Create environment and train a quick model
        env = DummyVecEnv([lambda: SingleTrainControlEnv()])
        model = DQN("MlpPolicy", env, verbose=0, learning_rate=0.001, buffer_size=10000,
                    learning_starts=100, batch_size=32, tau=0.1, gamma=0.99,
                    train_freq=4, gradient_steps=1)
        model.learn(total_timesteps=5000)
        model.save(model_path)
    return model

# -------------------- Helper: Find Front/Back Trains --------------------
def get_front_back(trains, selected_index):
    """Return distances (km) to next train ahead and behind."""
    front_dist = None
    back_dist = None
    if selected_index < len(trains) - 1:
        front_dist = trains[selected_index + 1]["position_km"] - trains[selected_index]["position_km"]
    if selected_index > 0:
        back_dist = trains[selected_index]["position_km"] - trains[selected_index - 1]["position_km"]
    return front_dist, back_dist

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="AI Train Control - Indian Railways", layout="wide")
st.title("🚉 Maximizing Section Throughput with AI (Indian Railways)")
st.markdown("---")

# Initialize session state for train data
if "trains" not in st.session_state:
    st.session_state.trains = generate_train_data()
    st.session_state.selected_idx = 0  # default

# Load AI model
model = load_or_train_model()

# Sidebar: Train selection
st.sidebar.header("Select Your Train")
train_options = [f"{t['number']} - {t['name']}" for t in st.session_state.trains]
selected_train = st.sidebar.selectbox("Train Number/Name", train_options)
selected_idx = train_options.index(selected_train)
st.session_state.selected_idx = selected_idx

# Display current train info
train = st.session_state.trains[selected_idx]
front_dist, back_dist = get_front_back(st.session_state.trains, selected_idx)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Speed", f"{train['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Train Ahead Distance", f"{front_dist:.2f} km" if front_dist else "No train")
with col3:
    st.metric("Train Behind Distance", f"{back_dist:.2f} km" if back_dist else "No train")

# Clean Track Visualization
st.subheader("Track View (0 to 20 km)")
fig, ax = plt.subplots(figsize=(12, 2))

# Draw track line
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2)

# Plot all trains as small light dots
positions = [t['position_km'] for t in st.session_state.trains]
ax.scatter(positions, [0]*len(positions), c='lightblue', s=30, alpha=0.6, zorder=1)

# Highlight selected train in red
ax.scatter(train['position_km'], 0, c='red', s=100, zorder=2, edgecolors='darkred', linewidth=2)
ax.text(train['position_km'], 0.05, train['number'], ha='center', fontsize=9, fontweight='bold')

# Annotate front train if exists
if front_dist is not None and selected_idx < len(st.session_state.trains)-1:
    front_train = st.session_state.trains[selected_idx+1]
    ax.scatter(front_train['position_km'], 0, c='orange', s=70, zorder=2)
    ax.text(front_train['position_km'], -0.08, front_train['number'], ha='center', fontsize=8, color='orange')

# Annotate back train if exists
if back_dist is not None and selected_idx > 0:
    back_train = st.session_state.trains[selected_idx-1]
    ax.scatter(back_train['position_km'], 0, c='orange', s=70, zorder=2)
    ax.text(back_train['position_km'], -0.08, back_train['number'], ha='center', fontsize=8, color='orange')

ax.set_xlim(0, 20)
ax.set_ylim(-0.2, 0.2)
ax.set_yticks([])
ax.set_xlabel("Position (km)")
ax.set_title("Train Positions (Selected in Red, Neighbors in Orange)")

st.pyplot(fig)

# AI Recommendation Button
if st.button("🚦 Get AI Speed Recommendation"):
    # Prepare state for model
    min_speed, max_speed = 30, 100
    speed_norm = (train['speed_kmh'] - min_speed) / (max_speed - min_speed)
    front_norm = min((front_dist if front_dist else 10) / 10.0, 1.0)
    back_norm = min((back_dist if back_dist else 10) / 10.0, 1.0)
    obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

    # Predict action
    action, _ = model.predict(obs, deterministic=True)
    action = action.item()  # safe extraction

    # Map action to speed change (same as environment)
    speed_change = {0: -5, 1: 0, 2: 5}[action]
    new_speed = train['speed_kmh'] + speed_change
    new_speed = np.clip(new_speed, min_speed, max_speed)

    # Simulate one time step (1 second) to update positions
    time_step = 1/3600  # hours
    for t in st.session_state.trains:
        t['position_km'] += t['speed_kmh'] * time_step
        t['position_km'] = min(t['position_km'], 20.0)

    # Update selected train's speed
    st.session_state.trains[selected_idx]['speed_kmh'] = new_speed

    # Re-sort trains by position
    st.session_state.trains.sort(key=lambda x: x['position_km'])
    # Find new index of selected train (by number)
    for i, t in enumerate(st.session_state.trains):
        if t['number'] == train['number']:
            st.session_state.selected_idx = i
            break

    # Get updated distances
    new_front, new_back = get_front_back(st.session_state.trains, st.session_state.selected_idx)

    # Handle None values for front/back distances
    front_text = f"{new_front:.2f} km" if new_front is not None else "No train"
    back_text = f"{new_back:.2f} km" if new_back is not None else "No train"

    # Display notification
    st.success("### 📢 Driver Advisory")
    st.info(
        f"**Train {train['number']} - {train['name']}**\n\n"
        f"🚄 **Recommended Speed:** {new_speed:.0f} km/h\n"
        f"🔹 Train ahead at {front_text}\n"
        f"🔸 Train behind at {back_text}"
    )

st.markdown("---")
st.caption("AI model trained to maintain 1.5–3 km headway while maximizing speed. Notifications help drivers optimize throughput.")
