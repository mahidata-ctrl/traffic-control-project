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

# -------------------- Realistic Train Data Generator --------------------
def generate_realistic_trains(num_trains=50):
    cities = [
        "Mumbai", "Delhi", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Ahmedabad",
        "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Varanasi", "Amritsar", "Guwahati"
    ]
    train_types = [
        ("Rajdhani", 100, 120, 0.8, 1.0, 22),
        ("Shatabdi", 110, 130, 0.9, 1.1, 20),
        ("Duronto", 100, 120, 0.7, 0.9, 18),
        ("Garib Rath", 80, 100, 0.6, 0.8, 16),
        ("Express", 60, 90, 0.5, 0.7, 20),
        ("Mail", 50, 80, 0.4, 0.6, 22),
        ("Passenger", 40, 60, 0.3, 0.5, 15)
    ]

    trains = []
    used_numbers = set()
    progress_bar = st.progress(0, text=f"Generating {num_trains} realistic trains...")

    for i in range(num_trains):
        if i % 10 == 0:
            progress_bar.progress(i / num_trains)

        city1 = np.random.choice(cities)
        city2 = np.random.choice(cities)
        while city2 == city1:
            city2 = np.random.choice(cities)

        typ = train_types[np.random.randint(len(train_types))]
        type_name, min_speed, max_speed, accel, decel, coaches = typ

        base = np.random.choice([1, 2]) * 10000
        number = base + np.random.randint(1001, 9999)
        while number in used_numbers:
            number = base + np.random.randint(1001, 9999)
        used_numbers.add(number)

        name = f"{city1} {city2} {type_name}"
        length_km = (coaches * 22) / 1000.0
        origin = city1
        dest = city2
        dep_time = np.random.randint(0, 24*60)
        travel_time = np.random.randint(120, 600)
        arr_time = (dep_time + travel_time) % (24*60)

        trains.append({
            "number": str(number),
            "name": name,
            "type": type_name,
            "length_km": length_km,
            "max_speed_kmh": max_speed,
            "accel_kmh_per_s": accel * 3.6,
            "decel_kmh_per_s": decel * 3.6,
            "origin": origin,
            "destination": dest,
            "departure_min": dep_time,
            "arrival_min": arr_time,
            "position_km": None,
            "speed_kmh": None,
            "delayed_min": 0
        })

    progress_bar.progress(1.0)
    time.sleep(0.2)
    progress_bar.empty()
    return trains

# -------------------- Railway Environment with Fixed Blocks --------------------
class RailwaySectionEnv(gym.Env):
    def __init__(self, trains, section_length_km=50, block_length_km=2):
        super().__init__()
        self.trains = trains
        self.section_length = section_length_km
        self.block_length = block_length_km
        self.num_blocks = int(self.section_length / self.block_length)

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.float32)

        self.time_step = 1.0  # seconds
        self.ego_idx = 0
        self.trains_sorted = []
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        num = len(self.trains)
        positions = np.random.uniform(0, self.section_length, size=num)
        for i, t in enumerate(self.trains):
            t["position_km"] = positions[i]
            t["speed_kmh"] = np.random.uniform(30, t["max_speed_kmh"])
            t["delayed_min"] = 0

        self.trains_sorted = sorted(self.trains, key=lambda x: x["position_km"])
        self.ego_idx = np.random.randint(len(self.trains_sorted))
        return self._get_obs(), {}

    def _get_obs(self):
        ego = self.trains_sorted[self.ego_idx]
        front_dist = None
        for i in range(self.ego_idx + 1, len(self.trains_sorted)):
            other = self.trains_sorted[i]
            gap = other["position_km"] - ego["position_km"] - ego["length_km"]
            if gap > 0:
                front_dist = gap
                break
        if front_dist is None:
            front_dist = self.section_length - ego["position_km"]

        speed_norm = (ego["speed_kmh"] - 30) / (ego["max_speed_kmh"] - 30)
        front_norm = min(front_dist / 10.0, 1.0)
        return np.array([speed_norm, front_norm, 0.5], dtype=np.float32)

    def step(self, action):
        ego = self.trains_sorted[self.ego_idx]

        if action == 0:
            ego["speed_kmh"] -= ego["decel_kmh_per_s"] * self.time_step
        elif action == 2:
            ego["speed_kmh"] += ego["accel_kmh_per_s"] * self.time_step

        ego["speed_kmh"] = np.clip(ego["speed_kmh"], 0, ego["max_speed_kmh"])

        dt_hours = self.time_step / 3600.0
        for t in self.trains_sorted:
            t["position_km"] += t["speed_kmh"] * dt_hours
            t["position_km"] = min(t["position_km"], self.section_length)

        self.trains_sorted.sort(key=lambda x: x["position_km"])
        for i, t in enumerate(self.trains_sorted):
            if t["number"] == ego["number"]:
                self.ego_idx = i
                break

        front_dist = None
        for i in range(self.ego_idx + 1, len(self.trains_sorted)):
            other = self.trains_sorted[i]
            gap = other["position_km"] - ego["position_km"] - ego["length_km"]
            if gap > 0:
                front_dist = gap
                break
        if front_dist is None:
            front_dist = self.section_length - ego["position_km"]

        reward = 0.1 * ego["speed_kmh"]
        if front_dist < 1.0:
            reward -= 50
        elif front_dist < 2.0:
            reward -= 10
        elif front_dist > 5.0:
            reward -= 5

        if action != 1:
            reward -= 1

        done = False
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

# -------------------- Load or Train Model --------------------
@st.cache_resource
def load_or_train_model(env):
    model_path = "dqn_railway.zip"
    if os.path.exists(model_path):
        return DQN.load(model_path)
    else:
        vec_env = DummyVecEnv([lambda: env])
        model = DQN("MlpPolicy", vec_env, verbose=0, learning_rate=0.001,
                    buffer_size=10000, learning_starts=100, batch_size=32,
                    tau=0.1, gamma=0.99, train_freq=4, gradient_steps=1)
        with st.spinner("Training AI model for realistic railway..."):
            model.learn(total_timesteps=10000)
            model.save(model_path)
        return model

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="Practical AI Train Control", layout="wide")
st.title("🚆 Practical AI-Powered Railway Traffic Control")
st.markdown("---")

st.sidebar.header("Simulation Settings")
num_trains = st.sidebar.slider("Number of trains", 10, 100, 30, step=5)
section_length = st.sidebar.number_input("Section length (km)", 20, 200, 50, step=10)

if st.sidebar.button("🔄 New Simulation"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=600)
def get_trains(n):
    return generate_realistic_trains(n)

trains = get_trains(num_trains)

# Create environment with error handling
try:
    env = RailwaySectionEnv(trains, section_length_km=section_length)
except Exception as e:
    st.error(f"Failed to create environment: {e}")
    st.stop()

# Load AI model
model = load_or_train_model(env)

st.subheader("Train Selection")
train_options = [f"{t['number']} - {t['name']}" for t in trains]
selected = st.selectbox("Choose a train to control", train_options)
selected_idx = train_options.index(selected)
ego = trains[selected_idx]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Speed", f"{ego['speed_kmh']:.1f} km/h")
with col2:
    st.metric("Max Speed", f"{ego['max_speed_kmh']} km/h")
with col3:
    st.metric("Length", f"{ego['length_km']*1000:.0f} m")
with col4:
    st.metric("Delay", f"{ego['delayed_min']:.0f} min")

# Find front train
front_train = None
front_dist = None
for i in range(selected_idx + 1, len(trains)):
    other = trains[i]
    gap = other["position_km"] - ego["position_km"] - ego["length_km"]
    if gap > 0:
        front_train = other
        front_dist = gap
        break

if front_train:
    st.info(f"🚂 Train ahead: {front_train['number']} at {front_dist:.2f} km")
else:
    st.info("🚂 No train ahead (end of section)")

st.subheader("Track View")
fig, ax = plt.subplots(figsize=(12, 2))
ax.set_xlim(0, section_length)
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_xlabel("Position (km)")

# Draw blocks
block_length = 2
for i in range(0, int(section_length), block_length):
    ax.axvspan(i, i+block_length, alpha=0.1, color='gray' if i%4==0 else 'lightgray')

for t in trains:
    color = 'red' if t['number'] == ego['number'] else 'blue'
    ax.barh(0.5, t['length_km'], left=t['position_km'], height=0.2, color=color, edgecolor='black')
    ax.text(t['position_km'] + t['length_km']/2, 0.7, t['number'][-4:], ha='center', fontsize=8)

st.pyplot(fig)

if st.button("🚦 Get AI Speed Recommendation", type="primary"):
    obs = env._get_obs().reshape(1, -1)
    action, _ = model.predict(obs, deterministic=True)
    action = action.item() if isinstance(action, np.ndarray) else int(action)

    env.step(action)
    st.success("AI recommendation applied. Positions updated.")
    time.sleep(1)
    st.rerun()

st.subheader("Section Throughput")
st.metric("Trains in section", len(trains))
avg_speed = np.mean([t['speed_kmh'] for t in trains])
theoretical_throughput = avg_speed / 5
st.metric("Estimated throughput (trains/h)", f"{theoretical_throughput:.1f}")

st.markdown("---")
st.caption("""
**Practical enhancements:**
- Train lengths (200–600 m)
- Fixed‑block signaling (blocks of 2 km)
- Acceleration/braking limits
- Station schedules (simulated delays)
- Throughput estimation
""")
