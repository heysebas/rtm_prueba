from flask import Flask, jsonify, Response
import cv2
import numpy as np

app = Flask(__name__)

# Inicializa la cámara web
cap = cv2.VideoCapture(0)

def pixel_to_lux(intensity):
    return intensity * 0.1

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Opcional: procesar el frame aquí (añadir cuadrícula, etc.)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/lux_value')
def lux_value():
    ret, frame = cap.read()
    if not ret:
        return jsonify({'error': 'No se pudo capturar el fotograma'}), 500
    
    # Define la región de interés
    roi_x, roi_y, roi_width, roi_height = 100, 100, 50, 50
    roi_gray = cv2.cvtColor(frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width], cv2.COLOR_BGR2GRAY)
    average_intensity = np.mean(roi_gray)
    lux_value = pixel_to_lux(average_intensity)
    return jsonify({'lux_value': lux_value})

if __name__ == '__main__':
    app.run(debug=True)
