import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import base64
from collections import Counter
import matplotlib.pyplot as plt
import json
from google import genai

# Load the CSS file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def set_bg_from_local(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpeg;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

local_css("appCSS.css")
set_bg_from_local("assets/background.png")

# --- Helper Functions for Data Storage ---
#everything JSON is below here
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
        return {"is_sleeping": False, "sleep_start_time": None}
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

# --- Process Live JSON Data ---
def get_json_data(file):
    try:
        with open(file, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File {json} does not exist.")
        return None
    except Exception as e:
        print(f"Error reading {json}: {e}")
        return None
    
sleep_data = get_json_data('sleep_logs.json')

def process_json_data(data):
    counts = len(data)

    # a ideal temp for sleeping is 36.5 degrees
    temp_data = [record["temperature"] for record in data]
    avg_temp = sum(temp_data) / counts
    min_temp = min(temp_data)
    max_temp = max(temp_data)

    # noisy if score above 0.1
    noise_level_score = (sum([1 for record in data if record["sound"] >= 560]) / counts)

    # % of each sleep phase: light, deep, rem, awake
    sleep_phase = [50, 30, 15, 5]

    # % of times moved over entire sleep duration
    movement_percentage = (sum([1 for record in data if record["shock"]]) / counts) * 100

    # Create a string summary
    summary_text = (
        f"Sleep Data Summary:\n"
        f"Total duration of tracked sleep: {counts * 12} minutes (based on 5-minute intervals).\n"
        f"Noise score (anything over 0.1 is a noisy environment): {noise_level_score}.\n"
        f"Sleep phase percentage in the orde of [light, deep, rem, awake]: {sleep_phase}\n"
        f"Temperature during sleep:\n"
        f" - Average: {avg_temp:.2f}°C\n"
        f" - Minimum: {min_temp}°C\n"
        f" - Maximum: {max_temp}°C\n"
        f"Percentage of movement during the night: {movement_percentage:.2f} (lower is better for sleep quality, and more than 0.2 is bad)."
    )
    return summary_text

if sleep_data:
    sleep_summary = process_json_data(sleep_data)
    if sleep_summary == None:
        #print("Nothing in Summary")
        sleep_summary = "No summary available."
    else:
        #print(sleep_summary)
        pass
#start of app
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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("assets/bear image.jpg", width=300)
        st.write("")  # Spacer
        if not app_state["is_sleeping"]:
            if st.button("🌙 Start Sleep", key="start_sleep", use_container_width=True):
                app_state["is_sleeping"] = True
                app_state["sleep_start_time"] = datetime.now()
                save_state(app_state)
        else:
            if st.button("💤 End Sleep", key="end_sleep", use_container_width=True, type="primary"):
                app_state["is_sleeping"] = False
                sleep_duration = (datetime.now() - app_state["sleep_start_time"]).total_seconds() / 3600
                restlessness = 2  # Placeholder for a real restlessness score
                new_log = {
                    "date": datetime.now().isoformat(),
                    "duration": round(sleep_duration, 2),
                    "restlessness": restlessness,
                    "phases": ["light", "deep", "rem", "awake"], # Placeholder
                    "noise": 1, # Placeholder
                    "temperature": 22, # Placeholder
                    "movement": 3, # Placeholder
                    "shock": False, # Placeholder
                    "sound": 300, # Placeholder
                }
                logs = load_data()
                logs.append(new_log)
                save_data(logs)
                app_state["sleep_start_time"] = None
                save_state(app_state)

# --- Key Metrics Section ---
st.markdown("---")
st.header("Dashboard")

def compute_sleep_quality(duration, restlessness):
    # Duration score: 8 hours is ideal (full 70 points), less or more reduces score
    duration_score = max(0, 70 - abs(8 - duration) * 10)
    # Restlessness score: 1 is best (30 points), 5 is worst (0 points)
    restlessness_score = max(0, 30 - (restlessness - 1) * 7.5)
    return round(duration_score + restlessness_score, 1)

def compute_energy_score(duration, restlessness):
    # Example: 8 hours & restlessness 1 = 100, less sleep or more restlessness reduces score
    duration_component = min(duration / 8, 1) * 70  # up to 70 points for duration
    restlessness_component = max(0, (6 - restlessness) / 5) * 30  # up to 30 points for calmness
    return round(duration_component + restlessness_component, 1)

logs = load_data()
avg_sleep = 0
avg_quality = 0
avg_energy = 0
if logs:
    avg_sleep = sum(log['duration'] for log in logs) / len(logs)
    quality_scores = [
        compute_sleep_quality(log['duration'], log.get('restlessness', 2))
        for log in logs
    ]
    avg_quality = sum(quality_scores) / len(quality_scores)
    energy_scores = [
        compute_energy_score(log['duration'], log.get('restlessness', 2))
        for log in logs
    ]
    avg_energy = sum(energy_scores) / len(energy_scores)

# Aggregate sleep phases for pie chart
phase_counts = Counter()
for log in logs:
    for phase in log.get("phases", []):
        phase_counts[phase] += 1

with st.container(border=False):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write("Average Sleep")
        st.title(f"😴 {round(avg_sleep, 1)}h")
    with col2:
        st.write("Sleep Phase Breakdown")
        if phase_counts:
            fig, ax = plt.subplots()
            ax.pie(
                list(phase_counts.values()),
                labels=list(phase_counts.keys()),
                autopct='%1.1f%%',
                startangle=90,
                counterclock=False
            )
            ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.write("No phase data")
    with col3:
        st.write("Energy Score")
        if avg_energy > 0:
            fig2, ax2 = plt.subplots()
            ax2.pie(
                [avg_energy, 100 - avg_energy],
                labels=[f"Energy ({round(avg_energy,1)})", ""],
                colors=["#FFD700", "#E0E0E0"],
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.4)
            )
            ax2.axis('equal')
            st.pyplot(fig2)
        else:
            st.write("No data")

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
        st.markdown("Shock: 300")
        st.markdown("Sound: 560")
        st.markdown("Restlessness: 3/5")
    else:
        st.warning("Not monitoring.")
        st.markdown("Heart Rate: --")
        st.markdown("Temperature: --")
        st.markdown("Movement: --")
        st.markdown("Sleep Phase: --")
        st.markdown("Noise: --")
        st.markdown("Shock: --")
        st.markdown("Sound: --")
        st.markdown("Restlessness: --")

# --- AI Assistant ---
st.markdown("---")
with st.container(border=False):
    st.subheader("AI Sleep Assistant")
    log_button = st.button("Generate Personalized Routine", key="gen_routine", use_container_width=True)
        # Get the most recent sleep duration from logs
    sleep_duration = None
    restlessness_score = None
    if logs:
        last_log = logs[-1]
        sleep_duration = last_log.get("duration", 0)
        restlessness_score = last_log.get("restlessness", 2)  # Default to 2 if not present

    if log_button:
        if not sleep_duration or sleep_duration <= 0:
            st.error("No recent sleep data available. Please log some sleep first.")
        else:
            # Configure your API key
            client = genai.Client(api_key="")

            # Define the prompt for Gemini
            prompt = (
                f"You are a friendly AI sleep coach. Analyze the following sleep data "
                f"and provide a personalized sleep tip and actionable suggestions to improve their next night's sleep. "
                f"Keep it concise and encouraging.\n\n"
                f"The user slept for a total of {sleep_duration} hours.\n"
                f"Data Summary:\n{sleep_summary}"
            )

            # Get the response from Gemini
            try:
                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                ai_tip = response.text
                st.success(f"**Personalized Tip:** {ai_tip}")
            except Exception as e:
                st.error(f"An error occurred while generating the tip: {e}")

# --- Sleep History & Analytics ---
st.markdown("---")
st.header("Sleep History & Analytics")

if not logs:
    st.write("No sleep logs yet. Start tracking your sleep to see your history here!")
else:
    # Reverse logs to show latest first
    for i, log in enumerate(reversed(logs)):
        # Format date
        date_str = datetime.fromisoformat(log["date"]).strftime("%m/%d/%Y %H:%M:%S")
        label = f"{date_str} - {log.get('duration', 'N/A')} hours"

        with st.expander(label, expanded=False):
            st.write(f"**Duration:** {log.get('duration', 'N/A')} hours")
            st.write(f"**Restlessness:** {log.get('restlessness', 'N/A')}/5")
            st.write(f"**Noise Level:** {log.get('noise', 'N/A')}")
            st.write(f"**Temperature:** {log.get('temperature', 'N/A')}°C")
            st.write(f"**Movement:** {log.get('movement', 'N/A')}")
            st.write(f"**Phases:** {', '.join(log.get('phases', [])) if log.get('phases') else 'N/A'}")
            st.write(f"**Shock Detected:** {log.get('shock', 'N/A')}")
            st.write(f"**Sound Value:** {log.get('sound', 'N/A')}")

# --- Reset/Clear All Button ---
st.markdown("---")
with st.container(border=False):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🧹 Reset All (Clear Data)", key="reset_all", type="secondary"):
            # Remove data files if they exist
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
            st.success("All data has been cleared. Please refresh the page.")
            st.stop()