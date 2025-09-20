import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os

# --- Helper Functions for Data Storage ---
DATA_FILE = "sleep_logs.json"
STATE_FILE = "app_state.json"

def load_data():
    """Loads sleep logs from a JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Saves sleep logs to a JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_state():
    """Loads app state from a JSON file."""
    if not os.path.exists(STATE_FILE):
        return {"is_sleeping": False, "hug_count": 0, "sleep_start_time": None}
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
        # Convert sleep_start_time back to datetime object
        if state["sleep_start_time"]:
            state["sleep_start_time"] = datetime.fromisoformat(state["sleep_start_time"])
        return state

def save_state(state):
    """Saves app state to a JSON file."""
    # Convert sleep_start_time to ISO format string for JSON serialization
    if state["sleep_start_time"]:
        state["sleep_start_time"] = state["sleep_start_time"].isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

# --- App Initialization and State Management ---
app_state = load_state()

# --- App Layout ---
st.set_page_config(
    page_title="Bear-ly Awake",
    page_icon="🐻",
    layout="centered",
)

# --- Header Section ---
st.title("Bear-ly Awake 🐻")
st.markdown("Your Intelligent Sleep Companion!")

st.markdown("---")
# --- Bear Container with Buttons ---
with st.container(border=False):
    col_img, col_buttons = st.columns([0.5, 2])
    
    with col_img:
        st.image("assets/bear image.jpg")
    
    with col_buttons:
        st.write("") # Spacer
        col_sleep = st.columns(2)
        if not app_state["is_sleeping"]:
            if st.button("🌙 Start Sleep", use_container_width=True):
                app_state["is_sleeping"] = True
                app_state["sleep_start_time"] = datetime.now()
                save_state(app_state)
        else:
            if st.button("💤 End Sleep", use_container_width=True, type="primary"):
                app_state["is_sleeping"] = False
                sleep_duration = (datetime.now() - app_state["sleep_start_time"]).total_seconds() / 3600
                restlessness = 2 # Placeholder for a real restlessness score
                
                # Logic to add the log
                new_log = {
                    "date": datetime.now().isoformat(),
                    "duration": round(sleep_duration, 2),
                    "restlessness": restlessness,
                    "data_points": 7, # Simulated data points
                    "phases": ["light", "deep", "rem", "awake"] # Simulated phases
                }
                logs = load_data()
                logs.append(new_log)
                save_data(logs)
                
                app_state["sleep_start_time"] = None
                save_state(app_state)

# --- Key Metrics Section ---
st.markdown("---")
st.header("Dashboard")

logs = load_data()
avg_sleep = 0
if logs:
    avg_sleep = sum(log['duration'] for log in logs) / len(logs)

with st.container(border=False):
    st.write("Avg Sleep")
    st.title(f"😴 {round(avg_sleep, 1)}h")

# --- Live Sensors (Simulated) ---
st.markdown("---")
with st.container(border=False):
    st.subheader("Live Sensors")
    if app_state["is_sleeping"]:
        st.success("MONITORING")
        st.markdown("Heart Rate: **68 BPM**")
        st.markdown("Temperature: **98.4°F**")
        st.markdown("Movement: **3/10**")
        st.markdown("Sleep Phase: **AWAKE**")
        st.markdown("Noise: NONE")
    else:
        st.warning("Not monitoring.")
        st.markdown("Heart Rate: --")
        st.markdown("Temperature: --")
        st.markdown("Movement: --")
        st.markdown("Sleep Phase: --")
        st.markdown("Noise: --")

# --- AI Assistant ---
st.markdown("---")
with st.container(border=False):
    st.subheader("AI Sleep Assistant")
    if st.button("Generate Personalized Routine", use_container_width=True):
        st.markdown("""
        ### Personalized Routine
        Based on your last few nights of sleep, we recommend the following:
        - **Maintain a consistent bedtime:** Try to go to sleep around 10:30 PM.
        - **Minimize screen time:** Avoid your phone for at least 30 minutes before bed.
        - **Take a warm bath:** A warm bath can help you relax and fall asleep faster.
        """)

# --- Sleep History & Analytics ---
st.markdown("---")
st.header("Sleep History & Analytics")

if not logs:
    st.write("No sleep logs yet. Start tracking your sleep to see your history here!")
else:
    for log in reversed(logs):
        date_str = datetime.fromisoformat(log["date"]).strftime("%m/%d/%Y")
        
        with st.expander(f"**{date_str}** - {log['duration']} hours"):
            st.write(f"**Data Points:** {log['data_points']} points")
            st.write(f"**Restlessness:** {log['restlessness']}/5")
            st.write(f"**Sleep Phases:** {', '.join(log['phases'])}")

# --- Reset/Clear All Button ---
st.markdown("---")

if st.button("🧹 Reset All (Clear Data)", type="secondary"):
    # Remove data files if they exist
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    st.success("All data has been cleared. Please refresh the page.")
    st.stop()