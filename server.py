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

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

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
        processed_frame = my_game.UpdateFrame(client_id, frame)
        processed_frame = np.uint8(np.absolute(processed_frame))

        # Send back to client
        _, buffer = cv2.imencode('.jpg', processed_frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{encoded_image}"

        # Send the processed image back to the phone
        emit('processed_frame', image_data)

    except Exception as e:
        print(f"Error handling frame: {e}")

# Run the app
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('certificates/cert.pem', 'certificates/key.pem'))
