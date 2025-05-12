import streamlit as st
import time
import cv2
from ultralytics import YOLO

# Load the YOLOv8 model (adjust the path if necessary)
model_path = "yolov8n.pt"  # or yolov8n.torchscript
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

    .left {
        left: 0;
        border-right: 2px solid black;
        transform: translateX(0);
    }

    .right {
        right: 0;
        border-left: 2px solid black;
        transform: translateX(0);
    }

    .open .left {
        transform: translateX(-100%);
    }

    .open .right {
        transform: translateX(100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if 'is_open' not in st.session_state:
    st.session_state.is_open = False
    st.session_state.current_floor = 0
    st.session_state.target_floor = 0
    st.session_state.previous_floor = 0
    st.session_state.person_count = 0

# Function to run the model and capture the last frame
def run_model(duration):
    cap = cv2.VideoCapture(0)  # Open webcam
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return 0, None

    start_time = time.time()
    video_feed = st.empty()  # Placeholder for real-time feed
    person_count = 0
    last_frame = None  # To store the last frame

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            st.warning("Warning: Could not retrieve frame.")
            break

        # Run YOLO inference
        results = model(frame)
        persons = [det for det in results[0].boxes if det.cls[0] == 0]
        person_count = len(persons)

        # Annotate frame and display in real-time
        annotated_frame = results[0].plot()
        video_feed.image(annotated_frame, channels="BGR", use_column_width=True)

        # Store the last frame
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
floors = [0, 1, 2, 3, 4,5,6,7,8,9,10,11,12]
st.session_state.target_floor = st.selectbox("Select Floor to Go", floors, index=st.session_state.current_floor)

# Button to move the lift
if st.button("Move Lift"):
    st.session_state.previous_floor = st.session_state.current_floor

    # Simulate floor movement
    current_floor_placeholder = st.empty()
    while st.session_state.current_floor != st.session_state.target_floor:
        if st.session_state.current_floor < st.session_state.target_floor:
            st.session_state.current_floor += 1  # Move up
        else:
            st.session_state.current_floor -= 1  # Move down

        current_floor_placeholder.markdown(f"**Current Floor: {st.session_state.current_floor}**")
        current_floor_placeholder.markdown(f"**Model started on  Floor: {st.session_state.target_floor-2}**")

        time.sleep(1)  # Simulate time for moving between floors

    # Calculate model runtime based on floor difference
    duration = 2 #abs(st.session_state.target_floor - (st.session_state.previous_floor-1)) * 1  # 2 seconds per floor
      
    # Run YOLO model when lift reaches the target floor
    with st.spinner("Detecting persons..."):
        person_count, last_frame = run_model(duration)

    # Display final result
    if last_frame is not None:
        st.image(last_frame, channels="BGR", use_column_width=True)
        st.write(f"Persons detected: {person_count}")

    # Update door state based on detection
    if person_count > 0:
        st.session_state.is_open = True
        st.success("Persons detected! Doors are opening.")
    else:
        st.session_state.is_open = False
        st.warning("No persons detected. Doors remain closed.")

# Continuous status updates
status_placeholder = st.empty()
while True:
    if st.session_state.is_open:
        status_placeholder.markdown(f"**Lift is OPEN on Floor {st.session_state.current_floor}.**")
    else:
        status_placeholder.markdown(f"**Lift is CLOSED on Floor {st.session_state.current_floor}.**")

    time.sleep(1)
