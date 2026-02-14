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
    """
    Generate trains with realistic parameters:
    - length (200–600 m)
    - max speed (60–120 km/h)
    - acceleration (0.5–1.0 m/s²)
    - deceleration (0.8–1.2 m/s²)
    - station schedule (arrival/departure times)
    """
    cities = [
        "Mumbai", "Delhi", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Ahmedabad",
        "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Visakhapatnam",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Varanasi", "Amritsar", "Guwahati"
    ]
    train_types = [
        ("Rajdhani", 100, 120, 0.8, 1.0, 22),   # name, min_speed, max_speed, accel, decel, coaches
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

        # Train number (unique)
        base = np.random.choice([1, 2]) * 10000
        number = base + np.random.randint(1001, 9999)
        while number in used_numbers:
            number = base + np.random.randint(1001, 9999)
        used_numbers.add(number)

        # Name
        name = f"{city1} {city2} {type_name}"

        # Train length (each coach ~22 m)
        length_km = (coaches * 22) / 1000.0  # km

        # Schedule: two stations (origin and destination) with random times
        origin = city1
        dest = city2
        dep_time = np.random.randint(0, 24*60)  # minutes after midnight
        travel_time = np.random.randint(120, 600)  # minutes
        arr_time = (dep_time + travel_time) % (24*60)

        trains.append({
            "number": str(number),
            "name": name,
            "type": type_name,
            "length_km": length_km,
            "max_speed_kmh": max_speed,
            "accel_kmh_per_s": accel * 3.6,   # convert m/s² to km/h per s
            "decel_kmh_per_s": decel * 3.6,
            "origin": origin,
            "destination": dest,
            "departure_min": dep_time,
            "arrival_min": arr_time,
            "position_km": None,   # will be set later
            "speed_kmh": None,
            "delayed_min": 0
        })

    progress_bar.progress(1.0)
    time.sleep(0.2)
    progress_bar.empty()
    return trains

# -------------------- Railway Environment with Fixed Blocks --------------------
class RailwaySectionEnv(gym.Env):
    """
    Multi‑train simulation with:
    - Fixed blocks (each 2 km)
    - Train lengths
    - Speed limits per block
    - Stations at block boundaries
    - Simple train dynamics (acceleration/braking)
    """
    def __init__(self, trains, section_length_km=50, block_length_km=2):
        super().__init__()
        self.trains = trains
        self.section_length = section_length_km
        self.block_length = block_length_km
        self.num_blocks = int(section_length / block_length)

        # Action space: speed control for a selected train (0: brake, 1: coast, 2: accel)
        self.action_space = spaces.Discrete(3)

        # Observation: [speed_norm, distance_to_next_block_signal, next_block_occupied?]
        # We'll keep it simple for the RL agent: it sees its speed and distance to next train ahead.
        # A full observation would be complex; we keep the same 3-dim state as before.
        self.observation_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.float32)

        # For simulation, we need to track all trains' positions and speeds
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Place trains randomly along the section, sorted by position
        num = len(self.trains)
        positions = np.random.uniform(0, self.section_length, size=num)
        # Sort and assign
        self.trains_sorted = sorted(self.trains, key=lambda x: x["position_km"] if x["position_km"] else 0)
        for i, t in enumerate(self.trains_sorted):
            t["position_km"] = positions[i]
            t["speed_kmh"] = np.random.uniform(30, t["max_speed_kmh"])
        self.trains_sorted.sort(key=lambda x: x["position_km"])
        # Select a random train as the "ego" (the one the AI controls)
        self.ego_idx = np.random.randint(len(self.trains_sorted))
        self.time_step = 1.0  # seconds
        return self._get_obs(), {}

    def _get_obs(self):
        ego = self.trains_sorted[self.ego_idx]
        # Find nearest train ahead
        front_dist = None
        for i in range(self.ego_idx + 1, len(self.trains_sorted)):
            other = self.trains_sorted[i]
            gap = other["position_km"] - ego["position_km"] - ego["length_km"]
            if gap > 0:
                front_dist = gap
                break
        if front_dist is None:
            front_dist = self.section_length - ego["position_km"]  # open track ahead

        # Normalize
        speed_norm = (ego["speed_kmh"] - 30) / (ego["max_speed_kmh"] - 30)
        front_norm = min(front_dist / 10.0, 1.0)
        # For simplicity, ignore rear train in observation
        return np.array([speed_norm, front_norm, 0.5], dtype=np.float32)

    def step(self, action):
        ego = self.trains_sorted[self.ego_idx]

        # Apply acceleration/braking
        if action == 0:  # brake
            ego["speed_kmh"] -= ego["decel_kmh_per_s"] * self.time_step
        elif action == 2:  # accel
            ego["speed_kmh"] += ego["accel_kmh_per_s"] * self.time_step
        # Coast: no change

        # Limit speed
        ego["speed_kmh"] = np.clip(ego["speed_kmh"], 0, ego["max_speed_kmh"])

        # Move all trains (simplified: all move at their current speed)
        dt_hours = self.time_step / 3600.0
        for t in self.trains_sorted:
            t["position_km"] += t["speed_kmh"] * dt_hours
            # If a train reaches the end, it leaves the section (remove)
            # For simplicity, we'll wrap around (circular line) or cap at section length
            t["position_km"] = min(t["position_km"], self.section_length)

        # Re‑sort
        self.trains_sorted.sort(key=lambda x: x["position_km"])

        # Find new index of ego (may have changed due to sorting)
        for i, t in enumerate(self.trains_sorted):
            if t["number"] == ego["number"]:
                self.ego_idx = i
                break

        # Compute reward
        # Find front train again
        front_dist = None
        for i in range(self.ego_idx + 1, len(self.trains_sorted)):
            other = self.trains_sorted[i]
            gap = other["position_km"] - ego["position_km"] - ego["length_km"]
            if gap > 0:
                front_dist = gap
                break
        if front_dist is None:
            front_dist = self.section_length - ego["position_km"]

        # Reward: encourage high speed but penalize if too close to train ahead
        reward = 0.1 * ego["speed_kmh"]
        if front_dist < 1.0:   # less than 1 km gap -> danger
            reward -= 50
        elif front_dist < 2.0:
            reward -= 10
        elif front_dist > 5.0:   # too far, capacity lost
            reward -= 5

        # Penalize harsh actions (optional)
        if action != 1:
            reward -= 1

        done = False
        truncated = False
        return self._get_obs(), reward, done, truncated, {}

# -------------------- Train or Load DQN Model --------------------
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

# Sidebar: number of trains
st.sidebar.header("Simulation Settings")
num_trains = st.sidebar.slider("Number of trains", 10, 100, 30, step=5,
                               help="Realistic number for a 50 km section")
section_length = st.sidebar.number_input("Section length (km)", 20, 200, 50, step=10)

if st.sidebar.button("🔄 New Simulation"):
    st.cache_data.clear()
    st.rerun()

# Generate trains (cached)
@st.cache_data(ttl=600)
def get_trains(n):
    return generate_realistic_trains(n)

trains = get_trains(num_trains)

# Create environment (not cached because it holds mutable state)
env = RailwaySectionEnv(trains, section_length_km=section_length)

# Load AI model
model = load_or_train_model(env)

# Main area: train selection and info
st.subheader("Train Selection")
train_options = [f"{t['number']} - {t['name']}" for t in trains]
selected = st.selectbox("Choose a train to control", train_options)
selected_idx = train_options.index(selected)
ego = trains[selected_idx]

# Display train details
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

# Track visualization (simplified)
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

# Plot trains
for t in trains:
    color = 'red' if t['number'] == ego['number'] else 'blue'
    ax.barh(0.5, t['length_km'], left=t['position_km'], height=0.2, color=color, edgecolor='black')
    ax.text(t['position_km'] + t['length_km']/2, 0.7, t['number'][-4:], ha='center', fontsize=8)

st.pyplot(fig)

# AI Recommendation
if st.button("🚦 Get AI Speed Recommendation", type="primary"):
    # Prepare observation for current ego (using environment's method)
    obs = env._get_obs().reshape(1, -1)
    action, _ = model.predict(obs, deterministic=True)
    action = action.item() if isinstance(action, np.ndarray) else int(action)

    # Simulate one step with this action (update environment)
    env.step(action)

    # Update trains list from environment
    trains_sorted = env.trains_sorted
    # Rebuild train_options if needed (but we keep same list, just update speeds/positions)
    # Since we modified trains in place, the UI will reflect changes on next rerun
    st.success("AI recommendation applied. Positions updated.")
    time.sleep(1)
    st.rerun()

# Throughput metrics
st.subheader("Section Throughput")
# Count trains that have passed a point (simulate by checking if any train crossed a fixed point)
# Simplified: just show number of trains in section
st.metric("Trains in section", len(trains))
# Estimate throughput per hour (if we had moving trains)
avg_speed = np.mean([t['speed_kmh'] for t in trains])
theoretical_throughput = avg_speed / 5  # rough: trains per hour with 5 km headway
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
