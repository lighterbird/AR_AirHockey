import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import threading

from flask import request
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from src.game import Game

app = Flask(__name__)
socketio = SocketIO(app)

my_game = Game()
my_thread = threading.Thread(target=my_game.RenderThread)
my_thread.start()

# Dictionary to track the state of each control button
client_flags = {}

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Initialize flags for this client when they connect
    client_flags[request.sid] = {
        'up': False,
        'down': False,
        'left': False,
        'right': False,
        'scaleXPlus': False,
        'scaleXMinus': False,
        'scaleYPlus': False,
        'scaleYMinus': False
    }
    print(f"Client {request.sid} connected.")

@socketio.on('disconnect')
def handle_disconnect():
    # Remove this client's flags when they disconnect
    client_id = request.sid
    my_game.RemovePlayer(client_id)
    if request.sid in client_flags:
        del client_flags[request.sid]
    print(f"Client {request.sid} disconnected.")

@socketio.on('frame')
def handle_frame(data):
    # print("Entered handle_frame")
    try:
        # Get the ID of the client
        client_id = request.sid

        # Decode the base64 image from the phone
        img_data = base64.b64decode(data.split(',')[1])

        # Convert to PIL image, then to OpenCV format (numpy array)
        img = Image.open(BytesIO(img_data))
        frame = np.array(img)

        # Convert RGB to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        processed_frame = my_game.UpdateFrame(client_id, frame, client_flags[client_id])
        processed_frame = np.uint8(np.absolute(processed_frame))

        # Send back to client
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{encoded_image}"

        # Send the processed image back to the phone
        emit('processed_frame', image_data)

    except Exception as e:
        print(f"Error handling frame: {e}")

@socketio.on('control')
def handle_control(data):
    client_id = request.sid  # Use the unique session ID for the client
    button = data['button']
    is_pressed = data['isPressed']

    # Update the client's flags dictionary
    if client_id in client_flags:
        client_flags[client_id][button] = is_pressed

    # Optional: Print or log the button state change
    # print(f"Client {client_id} - Button '{button}' is {'pressed' if is_pressed else 'released'}")

# Run the app
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('certificates/cert.pem', 'certificates/key.pem'))
