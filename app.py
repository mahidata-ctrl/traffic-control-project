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

# -------------------- AI Environment for Training --------------------
class SingleTrainControlEnv(gym.Env):
    """
    Environment for controlling one train (ego) with a lead train ahead and a follow train behind.
    State: [ego_speed, front_distance, back_distance] normalized.
    Action: 0 = decelerate, 1 = maintain, 2 = accelerate.
    Reward: encourage safe distance (1.5-3 km) and high speed.
    """
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
        if action == 0 or action == 2:
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
        model.learn(total_timesteps=5000)
        model.save(model_path)
    return model

# -------------------- Helper: Find Front/Back Trains --------------------
def get_front_back(trains, selected_index):
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

# Plot all trains as small light dots
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
    front_norm = min((front_dist if front_dist else 10) / 10.0, 1.0)
    back_norm = min((back_dist if back_dist else 10) / 10.0, 1.0)
    obs = np.array([[speed_norm, front_norm, back_norm]], dtype=np.float32)

    action, _ = model.predict(obs, deterministic=True)
    action = action.item()

    speed_change = {0: -5, 1: 0, 2: 5}[action]
    new_speed = train['speed_kmh'] + speed_change
    new_speed = np.clip(new_speed, min_speed, max_speed)

    time_step = 1/3600
    for t in st.session_state.trains:
        t['position_km'] += t['speed_kmh'] * time_step
        t['position_km'] = min(t['position_km'], 20.0)

    st.session_state.trains[selected_idx]['speed_kmh'] = new_speed
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
        f"🚄 **Recommended Speed:** {new_speed:.0f} km/h\n"
        f"🔹 Train ahead at {front_text}\n"
        f"🔸 Train behind at {back_text}"
    )

st.markdown("---")
st.caption("AI model trained to maintain 1.5–3 km headway while maximizing speed. Notifications help drivers optimize throughput.")
