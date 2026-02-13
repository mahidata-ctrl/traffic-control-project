import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
import os

# -------------------- Extended Indian Train Data --------------------
def generate_train_data():
    """Return a list of 30 realistic Indian trains with random positions/speeds."""
    train_names = [
        "Mumbai Rajdhani", "Howrah Rajdhani", "Delhi Rajdhani", "Chennai Rajdhani",
        "Bengaluru Rajdhani", "Thiruvananthapuram Rajdhani", "Ahmedabad Rajdhani",
        "Sealdah Rajdhani", "Ranchi Rajdhani", "Bhubaneswar Rajdhani",
        "Karnataka Express", "Kerala Express", "Andhra Pradesh Express",
        "Tamil Nadu Express", "Goa Express", "Punjab Mail", "Grand Trunk Express",
        "Coromandel Express", "Konark Express", "Shatabdi Express",
        "Duronto Express", "Garib Rath", "Humsafar Express",
        "Lokmanya Tilak Terminus Express", "Prayagraj Express", "Ganga Kaveri Express",
        "Sanghamitra Express", "Mysuru Express", "Coimbatore Express", "Madurai Express"
    ]
    numbers = [11001, 12301, 12627, 12951, 12431, 12295, 12801, 12649, 12953,
               12426, 12577, 12615, 12723, 12839, 12646, 11013, 12622, 12835,
               12609, 12002, 12245, 12559, 12741, 11019, 12427, 12658, 12213,
               12614, 12675, 12641]
    base_speeds = [80, 75, 85, 80, 70, 65, 78, 82, 77, 72,
                   68, 73, 79, 81, 69, 66, 74, 76, 71, 67,
                   84, 79, 73, 77, 70, 68, 75, 72, 80, 78]
    trains = []
    for i in range(30):
        trains.append({
            "number": str(numbers[i]),
            "name": train_names[i],
            "base_speed": base_speeds[i]
        })
    np.random.seed(42)
    positions = np.random.uniform(0, 20, size=len(trains))
    speeds = [t["base_speed"] + np.random.randint(-5, 6) for t in trains]
    for i, t in enumerate(trains):
        t["position_km"] = positions[i]
        t["speed_kmh"] = speeds[i]
    trains.sort(key=lambda x: x["position_km"])
    return trains

# -------------------- Realistic Train Environment --------------------
class RealisticTrainEnv(gym.Env):
    """
    Realistic single-train control with acceleration limits and train length.
    The ego train is controlled by the agent; lead and follow trains are simulated with random actions.
    """
    def __init__(self, max_speed_kmh=100, min_speed_kmh=30, train_length_km=0.2, dt=1.0):
        super().__init__()
        self.max_speed_kmh = max_speed_kmh
        self.min_speed_kmh = min_speed_kmh
        self.train_length_km = train_length_km  # 200 m
        self.dt = dt / 3600.0  # convert seconds to hours for position updates

        # Acceleration/deceleration rates (km/h per second)
        self.accel_rate = 1.8   # 0.5 m/s² ≈ 1.8 km/h per second
        self.brake_rate = -3.6   # -1.0 m/s² ≈ -3.6 km/h per second

        self.action_space = spaces.Discrete(3)  # 0: brake, 1: coast, 2: accel
        # Observation: [norm_speed, norm_front_dist, norm_back_dist]
        high = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=high, dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Positions (km) – lead, ego, follow
        self.lead_pos = 15.0
        self.ego_pos = 10.0
        self.follow_pos = 5.0
        # Speeds (km/h)
        self.lead_speed = 65.0
        self.ego_speed = 60.0
        self.follow_speed = 55.0
        return self._get_obs(), {}

    def _get_obs(self):
        speed_norm = (self.ego_speed - self.min_speed_kmh) / (self.max_speed_kmh - self.min_speed_kmh)
        # Distance from front of ego to rear of lead train (or vice versa)
        front_dist = self.lead_pos - self.ego_pos - self.train_length_km
        back_dist = self.ego_pos - self.follow_pos - self.train_length_km
        # Clip negative distances (shouldn't happen, but safety)
        front_dist = max(0, front_dist)
        back_dist = max(0, back_dist)
        # Normalize distance (max expected ~10 km)
        front_norm = min(front_dist / 10.0, 1.0)
        back_norm = min(back_dist / 10.0, 1.0)
        return np.array([speed_norm, front_norm, back_norm], dtype=np.float32)

    def step(self, action):
        # --- Ego train speed update based on action ---
        if action == 0:  # brake
            self.ego_speed += self.brake_rate * self.dt * 3600  # convert rate to per dt
        elif action == 2:  # accel
            self.ego_speed += self.accel_rate * self.dt * 3600
        # else action 1: coast – no change
        self.ego_speed = np.clip(self.ego_speed, self.min_speed_kmh, self.max_speed_kmh)

        # --- Lead and follow trains: simple random acceleration ---
        # Lead train randomly accelerates/brakes
        lead_action = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
        if lead_action == -1:
            self.lead_speed += self.brake_rate * self.dt * 3600
        elif lead_action == 1:
            self.lead_speed += self.accel_rate * self.dt * 3600
        self.lead_speed = np.clip(self.lead_speed, self.min_speed_kmh, self.max_speed_kmh)

        # Follow train similarly
        follow_action = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
        if follow_action == -1:
            self.follow_speed += self.brake_rate * self.dt * 3600
        elif follow_action == 1:
            self.follow_speed += self.accel_rate * self.dt * 3600
        self.follow_speed = np.clip(self.follow_speed, self.min_speed_kmh, self.max_speed_kmh)

        # --- Update positions ---
        self.lead_pos += self.lead_speed * self.dt
        self.ego_pos += self.ego_speed * self.dt
        self.follow_pos += self.follow_speed * self.dt

        # Keep within track bounds (0-20 km)
        self.lead_pos = np.clip(self.lead_pos, 0, 20)
        self.ego_pos = np.clip(self.ego_pos, 0, 20)
        self.follow_pos = np.clip(self.follow_pos, 0, 20)

        # --- Compute reward ---
        front_dist = self.lead_pos - self.ego_pos - self.train_length_km
        back_dist = self.ego_pos - self.follow_pos - self.train_length_km

        reward = 0

        # Safety: very close front (including train length)
        if front_dist < 0.5:
            reward -= 10
        elif front_dist < 1.0:
            reward -= 5
        elif 1.0 <= front_dist <= 2.5:
            reward += 5   # ideal headway
        elif front_dist > 5.0:
            reward -= 2   # too far, capacity lost

        # Rear safety
        if back_dist < 0.5:
            reward -= 5

        # Encourage higher speed (normalized)
        speed_factor = (self.ego_speed - self.min_speed_kmh) / (self.max_speed_kmh - self.min_speed_kmh)
        reward += 2 * speed_factor

        # Small penalty for harsh actions to promote smooth driving
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
        # Create environment and train a quick model
        env = DummyVecEnv([lambda: RealisticTrainEnv()])
        model = DQN("MlpPolicy", env, verbose=0, learning_rate=0.001, buffer_size=10000,
                    learning_starts=100, batch_size=32, tau=0.1, gamma=0.99,
                    train_freq=4, gradient_steps=1)
        model.learn(total_timesteps=8000)  # a bit more for complex dynamics
        model.save(model_path)
    return model

# -------------------- Helper: Find Front/Back Trains --------------------
def get_front_back(trains, selected_index):
    front_dist = None
    back_dist = None
    if selected_index < len(trains) - 1:
        # Distance between front of selected and rear of next train
        front_dist = trains[selected_index + 1]["position_km"] - trains[selected_index]["position_km"] - 0.2
    if selected_index > 0:
        back_dist = trains[selected_index]["position_km"] - trains[selected_index - 1]["position_km"] - 0.2
    return front_dist, back_dist

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="AI Train Control - Realistic", layout="wide")
st.title("🚉 Realistic AI Train Control (Indian Railways)")
st.markdown("---")

if "trains" not in st.session_state:
    st.session_state.trains = generate_train_data()
    st.session_state.selected_idx = 0

model = load_or_train_model()

st.sidebar.header("Select Your Train")
train_options = [f"{t['number']} - {t['name']}" for t in st.session_state.trains]
selected_train = st.sidebar.selectbox("Train Number/Name", train_options)
selected_idx = train_options.index(selected_train)
st.session_state.selected_idx = selected_idx

train = st.session_state.trains[selected_idx]
front_dist, back_dist = get_front_back(st.session_state.trains, selected_idx)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Speed", f"{train['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Train Ahead Distance", f"{front_dist:.2f} km" if front_dist else "No train")
with col3:
    st.metric("Train Behind Distance", f"{back_dist:.2f} km" if back_dist else "No train")

# -------------------- Clean Track Visualization --------------------
st.subheader("Track View (0 to 20 km)")
fig, ax = plt.subplots(figsize=(10, 2))

# Draw track line
ax.axhline(y=0, color='gray', linestyle='-', linewidth=2)

# Plot all trains as small light dots (positions are front of train)
positions = [t['position_km'] for t in st.session_state.trains]
ax.scatter(positions, [0]*len(positions), c='lightblue', s=30, alpha=0.6, zorder=1)

# Highlight selected train in red
ax.scatter(train['position_km'], 0, c='red', s=100, zorder=2, edgecolors='darkred', linewidth=2)
ax.text(train['position_km'], 0.05, train['number'], ha='center', fontsize=10, fontweight='bold')

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

# -------------------- AI Recommendation Button --------------------
if st.button("🚦 Get AI Speed Recommendation"):
    min_speed, max_speed = 30, 100
    speed_norm = (train['speed_kmh'] - min_speed) / (max_speed - min_speed)
    # Use front/back distances (already include train length)
    front_norm = min((front_dist if front_dist else 10) / 10.0, 1.0)
    back_norm = min((back_dist if back_dist else 10) / 10.0, 1.0)
    obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

    action, _ = model.predict(obs, deterministic=True)
    action = action.item()

    # Apply action to the selected train in the mock data
    # For demo, we simulate one step with realistic dynamics
    # Convert action to speed change (simplified for demo)
    if action == 0:  # brake
        train['speed_kmh'] -= 3.6  # reduce by 3.6 km/h (1 m/s² for 1 sec)
    elif action == 2:  # accel
        train['speed_kmh'] += 1.8  # increase by 1.8 km/h
    # else coast: no change

    train['speed_kmh'] = np.clip(train['speed_kmh'], min_speed, max_speed)

    # Update all train positions (simple linear movement)
    time_step = 1/3600  # 1 second in hours
    for t in st.session_state.trains:
        t['position_km'] += t['speed_kmh'] * time_step
        t['position_km'] = np.clip(t['position_km'], 0, 20)

    # Re-sort and find new index
    st.session_state.trains.sort(key=lambda x: x['position_km'])
    for i, t in enumerate(st.session_state.trains):
        if t['number'] == train['number']:
            st.session_state.selected_idx = i
            break

    new_front, new_back = get_front_back(st.session_state.trains, st.session_state.selected_idx)

    front_text = f"{new_front:.2f} km" if new_front is not None else "No train"
    back_text = f"{new_back:.2f} km" if new_back is not None else "No train"

    st.success("### 📢 Driver Advisory")
    st.info(
        f"**Train {train['number']} - {train['name']}**\n\n"
        f"🚄 **Recommended Speed:** {train['speed_kmh']:.0f} km/h\n"
        f"🔹 Train ahead at {front_text}\n"
        f"🔸 Train behind at {back_text}\n\n"
        f"*(Action: {'Brake' if action==0 else 'Coast' if action==1 else 'Accelerate'})*"
    )

st.markdown("---")
st.caption("Realistic dynamics: acceleration 1.8 km/h/s, braking 3.6 km/h/s, train length 200m.")
