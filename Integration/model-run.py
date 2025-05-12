import streamlit as st
import time
import cv2
from ultralytics import YOLO

# Load the YOLOv8 model (adjust the path if necessary)
model_path = "yolov8n.pt"  # or yolov8n.torchscript
model = YOLO(model_path)

def run_model():
    # Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return

    # Create placeholders for the video feed and person count
    video_feed = st.empty()
    person_count_placeholder = st.empty()

    # Timer for 10 seconds
    start_time = time.time()
    last_frame = None  # Store the last frame
    last_person_count = 0  # Store the person count for the last frame

    # Real-time streaming loop
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            st.warning("Warning: Could not retrieve frame.")
            break

        # Run YOLOv8 inference
        results = model(frame)

        # Filter out only 'person' detections
        persons = [det for det in results[0].boxes if det.cls[0] == 0]  # Class 0 is 'person'
        person_count = len(persons)

        # Annotate the frame
        annotated_frame = results[0].plot()

        # Display the real-time frame and person count
        video_feed.image(annotated_frame, channels="BGR", use_column_width=True)
        person_count_placeholder.write(f"Persons detected: {person_count}")

        # Save the last frame and person count
        last_frame = annotated_frame
        last_person_count = person_count

    # Release the webcam
    cap.release()

    # Display the last frame and the person count
    if last_frame is not None:
        st.write("Final Frame:")
        st.image(last_frame, channels="BGR", use_column_width=True)
        st.write(f"Persons detected in final frame: {last_person_count}")

# Streamlit UI
st.title("YOLOv8 Real-Time Person Detection")

if st.button("Start Model"):
    run_model()