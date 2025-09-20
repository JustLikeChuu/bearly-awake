import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# --- Helper Functions for Data Storage ---
DATA_FILE = "sleep_logs.json"

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

# --- App Content ---
st.set_page_config(
    page_title="Bear-ly Awake",
    page_icon="🐻",
    layout="centered",
)

st.title("Bear-ly Awake 🐻")
st.markdown("Your comfort companion for better sleep.")
st.markdown("---")

# --- Form to Log Sleep ---
st.header("Log Your Night")

col1, col2 = st.columns(2)
with col1:
    sleep_duration = st.number_input(
        "Sleep Duration (hours)",
        min_value=0.0,
        step=0.5,
        format="%.1f",
        placeholder="e.g., 7.5",
    )
with col2:
    restlessness_score = st.number_input(
        "Restlessness (1-5)",
        min_value=1,
        max_value=5,
        step=1,
        placeholder="e.g., 2",
    )

log_button = st.button(
    "Log Sleep",
    use_container_width=True,
    help="Click to log your sleep and get a personalized tip.",
)

# --- Logic for Logging and Displaying Messages ---
if log_button:
    if sleep_duration <= 0 or restlessness_score not in range(1, 6):
        st.error("Please enter a valid sleep duration and restlessness score.")
    else:
        # Simulate AI logic for a personalized tip
        tips = {
            "low_duration": "Your duration was a bit low. Try to get to bed 30 minutes earlier tonight.",
            "high_duration": "Great job! A longer sleep duration can do wonders for your health.",
            "high_restlessness": "Feeling restless? Try a 10-minute meditation before bed to calm your mind.",
            "low_restlessness": "A calm night! Consistency is key for deep, restorative sleep.",
        }

        tip_message = ""
        if sleep_duration < 7.0:
            tip_message = tips["low_duration"]
        else:
            tip_message = tips["high_duration"]

        if restlessness_score > 3:
            tip_message += " " + tips["high_restlessness"]
        else:
            tip_message += " " + tips["low_restlessness"]

        # Hardcoded array of uplifting messages
        uplifting_messages = [
            "You are amazing! Keep up the great work.",
            "Every small step towards better sleep is a victory.",
            "Remember to be kind to yourself. You're doing great.",
            "Your well-being is worth the effort."
        ]

        import random
        uplifting_message = random.choice(uplifting_messages)

        # Display messages
        st.success(f"**Personalized Tip:** {tip_message}")
        st.info(f"**Uplifting Message:** {uplifting_message}")

        # Save data
        new_log = {
            "date": datetime.now().isoformat(),
            "duration": sleep_duration,
            "restlessness": restlessness_score,
        }
        logs = load_data()
        logs.append(new_log)
        save_data(logs)

# --- Display Sleep History ---
st.markdown("---")
st.header("Your Sleep Log")

sleep_data = load_data()
if not sleep_data:
    st.write("No sleep logs yet. Log your first night above!")
else:
    df = pd.DataFrame(sleep_data)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M")
    df.rename(columns={
        "date": "Date",
        "duration": "Duration (hours)",
        "restlessness": "Restlessness (1-5)",
    }, inplace=True)
    
    st.dataframe(df, use_container_width=True)

# Add a simple audio player for the heartbeat sound simulation
st.markdown("---")
st.header("Activate Your Bear")
st.markdown("Click the button below to simulate your bear's comforting heartbeat.")

if st.button("Play Soothing Sound", use_container_width=True):
    import base64
    from io import BytesIO
    import numpy as np
    import soundfile as sf

    # Generate a simple sine wave to mimic a heartbeat sound
    sample_rate = 44100
    frequency = 80 # Hz, a low, thumpy sound
    duration = 0.5 # seconds
    t = np.linspace(0., duration, int(sample_rate * duration))
    # Simple rising and falling gain to mimic a heartbeat
    gain_ramp = np.concatenate([np.linspace(0, 1, int(t.size/2)), np.linspace(1, 0, int(t.size/2))])
    audio_data = np.sin(2. * np.pi * frequency * t) * gain_ramp

    wav_io = BytesIO()
    sf.write(wav_io, audio_data, sample_rate, format='WAV')
    wav_io.seek(0)
    audio_base64 = base64.b64encode(wav_io.read()).decode()

    st.markdown(f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}"></audio>', unsafe_allow_html=True)
    st.write("Playing a calming sound...")
