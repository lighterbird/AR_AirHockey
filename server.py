from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to track the state of each control button
flags = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "scaleXPlus": False,
    "scaleXMinus": False,
    "scaleYPlus": False,
    "scaleYMinus": False,
}

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('frame')
def handle_frame(data):
    try:
        client_id = request.sid
        img_data = base64.b64decode(data.split(',')[1])
        img = Image.open(BytesIO(img_data))
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Process frame using Game logic and current flags
        processed_frame = process_game_frame(client_id, frame, flags)

        # Encode and send back the processed frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{encoded_image}"
        emit('processed_frame', image_data)
    except Exception as e:
        print(f"Error handling frame: {e}")

@socketio.on('control')
def handle_control(data):
    button = data['button']
    is_pressed = data['isPressed']
    flags[button] = is_pressed
    print(f"Button {button} is {'pressed' if is_pressed else 'released'}")

# Function to simulate game frame processing based on flags (stub for actual game logic)
def process_game_frame(client_id, frame, flags):
    # Example processing based on flags (for actual game logic, implement as needed)
    if flags["up"]:
        cv2.putText(frame, "Moving UP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if flags["down"]:
        cv2.putText(frame, "Moving DOWN", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if flags["left"]:
        cv2.putText(frame, "Moving LEFT", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if flags["right"]:
        cv2.putText(frame, "Moving RIGHT", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # Similar for scale flags...

    return frame

# Run the app
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('certificates/cert.pem', 'certificates/key.pem'))
