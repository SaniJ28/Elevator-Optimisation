import streamlit as st
import time

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

    /* Open State */
    .open .left {
        transform: translateX(-100%);
    }

    .open .right {
        transform: translateX(100%);
    }

    .info {
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session states if not already set
if 'is_open' not in st.session_state:
    st.session_state.is_open = False  # Initial state: doors closed
    st.session_state.start_time = None  # No start time initially
    st.session_state.current_floor = 0  # Start on ground floor
    st.session_state.target_floor = 0  # No target floor initially
    st.session_state.move_in_progress = False  # Track if the lift is moving

# Button to toggle lift state (manual override)
if st.button("Open/Close Lift (Manual)"):
    st.session_state.is_open = not st.session_state.is_open  # Toggle the state
    if st.session_state.is_open:
        st.session_state.start_time = time.time()  # Log the open time

# Determine the CSS class for the container
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

# Floor Selection
floors = [0, 1, 2, 3, 4]  # List of floors
st.session_state.target_floor = st.selectbox("Select Floor to Go", floors, index=st.session_state.current_floor)

# Button to move lift to selected floor
if st.button("Move Lift"):
    st.session_state.move_in_progress = True  # Set moving status
    st.success(f"Moving to floor {st.session_state.target_floor}...")

    # Placeholder for current floor updates
    current_floor_placeholder = st.empty()

    # Simulate moving to the selected floor, one floor at a time
    while st.session_state.current_floor != st.session_state.target_floor:
        # Update current floor based on the direction of movement
        if st.session_state.current_floor < st.session_state.target_floor:
            st.session_state.current_floor += 1  # Move up
        else:
            st.session_state.current_floor -= 1  # Move down
        
        # Update current floor display after moving
        current_floor_placeholder.markdown(f"**Current Floor: {st.session_state.current_floor}**")

        time.sleep(1)  # Wait for 1 second for each floor

    st.session_state.is_open = True  # Open doors on arrival
    st.session_state.start_time = time.time()  # Start timer for door auto-close

# Placeholder for continuous updates
status_placeholder = st.empty()

# Continuous status updates
while True:
    # Update the placeholder with the current status
    if st.session_state.is_open:
        status_placeholder.markdown(f"**The lift is currently OPEN on Floor {st.session_state.current_floor}.**")
    else:
        status_placeholder.markdown(f"**The lift is currently CLOSED on Floor {st.session_state.current_floor}.**")

    # Check if the lift has been open for more than 5 seconds
    if st.session_state.is_open and st.session_state.start_time:
        if time.time() - st.session_state.start_time > 5:
            st.session_state.is_open = False  # Auto-close the doors
            st.session_state.start_time = None  # Reset start time

    # Pause for a moment before the next update
    time.sleep(1)  # Adjust the sleep time as needed
