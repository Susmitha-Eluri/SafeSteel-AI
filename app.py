import streamlit as st
import cv2
import time
from safety_logic import evaluate_safety_state
from vision import process_frame

# --- Configuration ---
st.set_page_config(page_title="SafeSteel-AI", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS Injection ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: #58a6ff;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Main App Container */
    .stApp {
        background: radial-gradient(circle at top left, #1f2937, #0d1117 80%);
    }

    /* Metric & Alert Boxes (Glassmorphism) */
    div[data-testid="stMetric"], .stAlert {
        background: rgba(33, 38, 45, 0.6) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        padding: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover, .stAlert:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.7);
    }
    
    /* Buttons */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #238636, #2ea043);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ea043, #3fb950);
        box-shadow: 0 0 25px rgba(46, 160, 67, 0.8);
        transform: scale(1.02);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #58a6ff;
        box-shadow: 0 0 10px #58a6ff;
    }
    
    /* Red Alerts (Critical) */
    div[data-baseweb="notification"]:has(div:contains("CRITICAL")),
    div[data-baseweb="notification"]:has(div:contains("LOCKED")),
    div[data-baseweb="notification"]:has(div:contains("Missing")) {
        background: rgba(215, 58, 73, 0.15) !important;
        border: 1px solid #d73a49 !important;
        box-shadow: 0 0 20px rgba(215, 58, 73, 0.5);
        animation: pulse-red 1.5s infinite;
    }
    
    @keyframes pulse-red {
        0% { box-shadow: 0 0 15px rgba(215, 58, 73, 0.4); }
        50% { box-shadow: 0 0 25px rgba(215, 58, 73, 0.8); }
        100% { box-shadow: 0 0 15px rgba(215, 58, 73, 0.4); }
    }
    
    /* Adjust Streamlit Top Padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("SafeSteel-AI — Industrial Guardian Dashboard")

# --- Session State Initialization ---
if 'interlock_locked' not in st.session_state:
    st.session_state.interlock_locked = False
if 'degassing_start_time' not in st.session_state:
    st.session_state.degassing_start_time = None
if 'safety_score' not in st.session_state:
    st.session_state.safety_score = "100% — OPTIMAL"
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'run_video' not in st.session_state:
    st.session_state.run_video = False
if 'incident_logs' not in st.session_state:
    st.session_state.incident_logs = []
if 'cover_status' not in st.session_state:
    st.session_state.cover_status = 'IDLE'

# --- Helper Functions ---
def reset_interlock():
    st.session_state.interlock_locked = False
    st.session_state.degassing_start_time = None
    st.session_state.alerts = []

def start_degassing():
    st.session_state.degassing_start_time = time.time()

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col2:
    st.header("Telemetry & Controls")
    
    # Safety Index
    if st.session_state.safety_score == "100% — OPTIMAL":
        st.success(f"### Plant Safety Index: {st.session_state.safety_score}")
    else:
        st.error(f"### Plant Safety Index: {st.session_state.safety_score}")
        
    # Alerts
    if st.session_state.alerts:
        for alert in st.session_state.alerts:
            st.warning(alert)
            
    st.markdown("---")
    
    # Pillar 1: Structural Non-Compliance
    st.subheader("1. Structural Compliance")
    if st.session_state.cover_status == 'MISSING':
        st.error("CV Sensor: Ladle Cover Missing!")
    elif st.session_state.cover_status == 'COVERED':
        st.success("CV Sensor: Ladle Cover Detected!")
    else:
        st.info("CV Sensor: Idle (No Ladle Detected)")
    
    # Pillar 2: Process-Skipping Watchdog
    st.subheader("2. Process Watchdog (Degassing)")
    DEGASSING_DURATION = 15 # Seconds for demo purposes
    
    degassing_progress = 0
    degassing_advanced_early = False
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("Start Degassing"):
            start_degassing()
    with col_d2:
        advance_clicked = st.button("Advance to Next Step")
        
    if st.session_state.degassing_start_time is not None:
        elapsed = time.time() - st.session_state.degassing_start_time
        if elapsed < DEGASSING_DURATION:
            degassing_progress = elapsed / DEGASSING_DURATION
            st.progress(degassing_progress)
            st.info(f"Degassing in progress... ({int(elapsed)}/{DEGASSING_DURATION}s)")
            if advance_clicked:
                degassing_advanced_early = True
                timestamp = time.strftime('%H:%M:%S')
                log_msg = f"[{timestamp}] ALERT: User initiated casting sequence at {int(elapsed):02d} seconds. Mandatory {DEGASSING_DURATION}s degassing window violated. Incident report auto-sent to Plant Safety Director."
                st.session_state.incident_logs.append(log_msg)
        else:
            st.progress(1.0)
            st.success("Degassing Complete.")
    elif advance_clicked:
        degassing_advanced_early = True
        timestamp = time.strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] ALERT: User initiated casting sequence early. Mandatory degassing skipped. Incident report auto-sent to Plant Safety Director."
        st.session_state.incident_logs.append(log_msg)

    if st.session_state.incident_logs:
        for log in st.session_state.incident_logs:
            st.error(log)

    # Pillar 3: Proximity Protection
    st.subheader("3. Proximity Protection")
    casting_sequence_active = st.checkbox("Initiate Ladle Casting Sequence", value=False)
    
    st.markdown("---")
    
    # Interlock Status
    st.subheader("Automated Machine Interlock")
    if st.session_state.interlock_locked:
        st.error("🔒 CRANE LOCKED: Safety violation detected. Require manual reset.")
        if st.button("Clear Zone / Reset Interlock"):
            reset_interlock()
            st.rerun()
    else:
        st.success("⚙️ CRANE ROTATION MECHANISM: UNLOCKED")

    st.markdown("---")
    st.session_state.run_video = st.checkbox("Enable Live Video Feed", value=False)

# --- Logic Evaluation ---
# We evaluate safety state continuously, but geofence breach is handled inside the video loop
# to avoid full page reruns on every frame, which is slow.
# We will check Pillar 1 and 2 here.

p1_p2_interlock, _, _ = evaluate_safety_state(
    st.session_state.cover_status == 'MISSING', 
    degassing_advanced_early, 
    False, # geofence breach placeholder 
    casting_sequence_active
)

# If P1 or P2 tripped, we lock
if p1_p2_interlock and not st.session_state.interlock_locked:
    st.session_state.interlock_locked = True
    st.rerun()

with col1:
    st.header("Live Feed")
    frame_placeholder = st.empty()
    
    if st.session_state.run_video:
        cap = cv2.VideoCapture(0)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            st.error("Error: Could not open webcam.")
        else:
            while st.session_state.run_video:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture image")
                    break
                
                # Resize for consistency
                frame = cv2.resize(frame, (640, 480))
                
                processed_frame, breach_detected, cover_status = process_frame(frame, casting_sequence_active)
                st.session_state.cover_status = cover_status
                
                # Evaluate full safety state
                interlock, score, alerts = evaluate_safety_state(
                    (cover_status == 'MISSING'),
                    degassing_advanced_early,
                    breach_detected,
                    casting_sequence_active
                )
                
                # Convert BGR to RGB for Streamlit
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB")
                
                # If a new lock occurs, update state and rerun to update UI
                if interlock and not st.session_state.interlock_locked:
                    st.session_state.interlock_locked = True
                    st.session_state.safety_score = score
                    st.session_state.alerts = alerts
                    st.rerun()
                    
                time.sleep(0.03) # Small sleep to reduce CPU load
                
        if cap:
            cap.release()
    else:
        frame_placeholder.info("Video feed disabled. Check 'Enable Live Video Feed' to start.")
