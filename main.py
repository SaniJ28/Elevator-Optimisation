import streamlit as st
import time
import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model_path = "yolov8n.pt"
model = YOLO(model_path)

# CSS Styling for the Lift Container and Doors
st.markdown(
    """
    <style>
    .container {
        position: relative;
        width: 300px;
        height: 400px;
        background-color: #333;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
        margin: 20px auto;
    }
    .door {
        position: absolute;
        height: 100%;
        width: 50%;
        background-color: #555;
        transition: transform 2s ease-in-out;
    }
    .left { left: 0; border-right: 2px solid black; transform: translateX(0); }
    .right { right: 0; border-left: 2px solid black; transform: translateX(0); }
    .open .left { transform: translateX(-100%); }
    .open .right { transform: translateX(100%); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'is_open' not in st.session_state:
    st.session_state.is_open = False
    st.session_state.current_floor = 0
    st.session_state.target_floor = 0
    st.session_state.person_count = 0
    st.session_state.detection_done = False  # Track if detection has been performed

# Function to run the model for a specified duration
def run_model(duration):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return 0, None

    start_time = time.time()
    video_feed = st.empty()
    person_count = 0
    last_frame = None

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            st.warning("Warning: Could not retrieve frame.")
            break

        # Run YOLO inference
        results = model(frame)
        persons = [det for det in results[0].boxes if det.cls[0] == 0]
        person_count = len(persons)

        # Annotate and display frame in real-time
        annotated_frame = results[0].plot()
        video_feed.image(annotated_frame, channels="BGR", use_column_width=True)
        last_frame = annotated_frame

    cap.release()
    return person_count, last_frame

# Lift container and doors
container_class = "open" if st.session_state.is_open else ""
st.markdown(
    f"""
    <div class="container {container_class}">
        <div class="door left"></div>
        <div class="door right"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Floor selection
floors = list(range(13))
st.session_state.target_floor = st.selectbox("Select Floor to Go", floors, index=st.session_state.current_floor)

# Button to move the lift
if st.button("Move Lift"):
    moving_floor = st.session_state.current_floor  # Temporary moving floor value
    current_floor_placeholder = st.empty()

    # Calculate the duration for the model to run based on the floor difference
    duration = max(abs(st.session_state.target_floor - st.session_state.current_floor), 1)

    # Start YOLO model detection during lift movement
    with st.spinner("Detecting persons..."):
        st.session_state.person_count, last_frame = run_model(duration)
        st.session_state.detection_done = True  # Mark detection as completed

    # Simulate floor movement visually
    while moving_floor != st.session_state.target_floor:
        if moving_floor < st.session_state.target_floor:
            moving_floor += 1  # Move up
        else:
            moving_floor -= 1  # Move down

        current_floor_placeholder.markdown(f"**Current Floor: {moving_floor}**")
        time.sleep(1)

    # Update current floor after reaching target
    st.session_state.current_floor = st.session_state.target_floor
    st.warning("Press 'Open Door' to check for persons.")

# New button to open the lift door
if st.button("Open Door"):
    if st.session_state.detection_done:
        if st.session_state.person_count > 0:
            st.session_state.is_open = True
            st.success("Persons detected! Doors are opening.")
        else:
            st.session_state.is_open = False
            st.warning("No persons detected. Doors remain closed.")
    else:
        st.warning("Move the lift first to enable door control.")

# Status updates
status_placeholder = st.empty()
if st.session_state.is_open:
    status_placeholder.markdown(f"**Lift is OPEN on Floor {st.session_state.current_floor}.**")
else:
    status_placeholder.markdown(f"**Lift is CLOSED on Floor {st.session_state.current_floor}.**")
