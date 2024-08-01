import cv2
import numpy as np
import base64
from flask import Flask, render_template, Response, jsonify, request
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Definir una función de conversión de intensidad a lux
def pixel_to_lux(intensity):
    return intensity * 0.1  # Ajusta este factor según sea necesario

auto_selection_position = (0, 0)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    global auto_selection_position
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Convertir a escala de grises
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Encontrar la región con mayor iluminación
        max_loc = find_brightest_region(gray_frame, 50, 50)
        if max_loc:
            auto_selection_position = max_loc
            # Dibujar la selección fija en la región más iluminada
            cv2.rectangle(frame, max_loc, (max_loc[0] + 50, max_loc[1] + 50), (255, 0, 0), 2)

        # Convertir la imagen de nuevo a BGR para mostrarla en color con OpenCV
        frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

        # Dibuja la cuadrícula
        cell_width = gray_frame.shape[1] // 2
        cell_height = gray_frame.shape[0] // 13

        for i in range(13):
            for j in range(2):
                top_left = (j * cell_width, i * cell_height)
                bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
                cv2.rectangle(frame, top_left, bottom_right, (255, 255, 255), 1)

        # Añade el texto
        values = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        for i in range(13):
            if i < len(values):
                text = f'{values[i]}%'
                text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                text_x = 5
                text_y = (i * cell_height) + (cell_height + text_size[1]) // 2
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_str = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_str + b'\r\n')

    cap.release()

def find_brightest_region(gray_frame, box_width, box_height):
    """Encuentra la región con mayor iluminación en el frame."""
    max_avg_intensity = 0
    brightest_loc = None
    for y in range(0, gray_frame.shape[0] - box_height, box_height):
        for x in range(0, gray_frame.shape[1] - box_width, box_width):
            roi = gray_frame[y:y+box_height, x:x+box_width]
            avg_intensity = np.mean(roi)
            if avg_intensity > max_avg_intensity:
                max_avg_intensity = avg_intensity
                brightest_loc = (x, y)
    return brightest_loc

@app.route('/get_auto_selection')
def get_auto_selection():
    global auto_selection_position
    x, y = auto_selection_position
    return jsonify({'x': x, 'y': y})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/measure_lux', methods=['POST'])
def measure_lux():
    data = request.json

    # Verificar que los datos estén presentes
    if 'imageData' not in data or 'x' not in data or 'y' not in data or 'size' not in data or 'width' not in data or 'height' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        # Decodificar la imagen base64
        header, encoded = data['imageData'].split(',', 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data))
        image = np.array(image)

        # Convertir la imagen a escala de grises
        if image.shape[2] == 4:  # RGBA
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        else:
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        width = int(data['width'])
        height = int(data['height'])

        # Extraer la región de interés
        x = int(data['x'])
        y = int(data['y'])
        size = int(data['size'])

        roi_x1 = max(x - size, 0)
        roi_y1 = max(y - size, 0)
        roi_x2 = min(x + size, width)
        roi_y2 = min(y + size, height)

        roi_gray = gray_image[roi_y1:roi_y2, roi_x1:roi_x2]

        average_intensity = np.mean(roi_gray)
        lux_value = pixel_to_lux(average_intensity)

        return jsonify({'lux': lux_value})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error al procesar la imagen"}), 500

if __name__ == "__main__":
    app.run(debug=True)
