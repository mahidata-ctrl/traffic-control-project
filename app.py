import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="AI Train Simulator", layout="wide")

# Header Section
st.title("🚉 Maximizing Section Throughput via AI-Powered Precise Control")
st.markdown(f"**Researcher:** Mahitha | **Specialization:** B.Tech AI & Data Science")
st.write("---")

# Sidebar for Innovation Control
st.sidebar.header("Control Panel")
mode = st.sidebar.radio("Signaling Logic (Innovation)", ["Traditional Fixed Block", "AI-Powered Moving Block"])
num_trains = st.sidebar.slider("Traffic Density (Number of Trains)", 2, 6, 4)

# Innovation Explanation
with st.expander("See Innovation Details"):
    st.write("""
    **Fixed Block:** Trains wait for a whole physical section to clear. Huge 'Ghost Space' is wasted.
    **AI Moving Block:** AI calculates 'Precise Braking Distance' in real-time. Trains can move closer, 
    maximizing the number of trains on the same track.
    """)

# Simulation Engine
if st.button("▶️ Launch Live Simulator"):
    # Initialize train data
    trains = [{"id": i, "pos": -i * 20, "speed": 0, "color": "🔴" if mode == "Traditional Fixed Block" else "🟢"} for i in range(num_trains)]
    
    track_placeholder = st.empty()
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    # Data for graph
    history = []

    for frame in range(100):
        current_speeds = []
        for i, t in enumerate(trains):
            # INNOVATION LOGIC
            if mode == "Traditional Fixed Block":
                # Static Safety Buffer (Needs 25 units of gap)
                if i > 0 and (trains[i-1]['pos'] - t['pos']) < 25:
                    t['speed'] = 0 
                else:
                    t['speed'] = 3
            else:
                # AI MOVING BLOCK (Precise Control - Needs only 12 units of gap)
                if i > 0 and (trains[i-1]['pos'] - t['pos']) < 12:
                    t['speed'] = 2 # Slow down precisely
                else:
                    t['speed'] = 6 # High efficiency speed

            t['pos'] += t['speed']
            if t['pos'] > 110: t['pos'] = -10 # Loop train
            current_speeds.append(t['speed'])

        # 1. Visual Track Representation
        track_viz = "🛤️"
        for p in range(0, 110, 5):
            train_at_p = next((t for t in trains if p <= t['pos'] < p + 5), None)
            if train_at_p:
                track_viz += f"{train_at_p['color']}🚅"
            else:
                track_viz += "──"
        track_viz += "🛤️"
        track_placeholder.markdown(f"### Live Track View\n`{track_viz}`")

        # 2. Metrics
        throughput = sum([1 for s in current_speeds if s > 0])
        avg_speed = np.mean(current_speeds)
        with metrics_placeholder.container():
            c1, c2 = st.columns(2)
            c1.metric("Section Throughput", f"{throughput} Active Trains")
            c2.metric("Average Speed", f"{avg_speed:.2f} m/s")

        history.append(avg_speed)
        time.sleep(0.1)

    st.success(f"Simulation Finished! {mode} system analyzed.")

st.markdown("---")
st.info("Project intended for Conference Submission: 'Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control'")
