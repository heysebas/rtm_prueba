from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import mysql.connector
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)

# Conexión a MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['CendaPro']
mongo_collection = mongo_db['exampleCollection']

# Conexión a MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",  # Contraseña actualizada
    database="Cenda"
)
mysql_cursor = mysql_conn.cursor()

def pixel_to_lux(intensity):
    return intensity * 0.1  # Ajusta este factor según sea necesario

@app.route('/')
def index():
    return render_template('index.html')

def capture_frame():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray_frame

@app.route('/capture_image')
def capture_image():
    gray_frame = capture_frame()
    if gray_frame is None:
        return jsonify({"error": "Error al capturar la imagen"}), 500

    _, buffer = cv2.imencode('.png', gray_frame)
    image_data = base64.b64encode(buffer).decode('utf-8')

    return jsonify({"imageData": f"data:image/png;base64,{image_data}"})

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    if 'imageData' not in data or 'plate' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    image_data = data['imageData']
    plate = data['plate']

    try:
        # Decodifica la imagen
        image_data = image_data.split(',')[1]  # Extrae el contenido base64
        image_data = base64.b64decode(image_data)  # Decodifica base64

        # Guarda en MongoDB
        mongo_collection.insert_one({
            'plate': plate,
            'image': image_data
        })

        # Guarda en MySQL (como datos binarios)
        sql = "INSERT INTO RTM (placa, image) VALUES (%s, %s)"
        mysql_cursor.execute(sql, (plate, image_data))
        mysql_conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error al guardar los datos"}), 500

@app.route('/measure_lux', methods=['POST'])
def measure_lux():
    data = request.json

    if 'imageData' not in data or 'x' not in data or 'y' not in data or 'size' not in data or 'width' not in data or 'height' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    image_data = data['imageData']
    x = int(data['x'])
    y = int(data['y'])
    size = int(data['size'])
    width = int(data['width'])
    height = int(data['height'])

    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_data))
    image = np.array(image.convert('L'))

    x1 = max(x - size // 2, 0)
    y1 = max(y - size // 2, 0)
    x2 = min(x + size // 2, width)
    y2 = min(y + size // 2, height)

    region = image[y1:y2, x1:x2]
    average_intensity = np.mean(region)

    lux = pixel_to_lux(average_intensity)

    return jsonify({"lux": lux})

@app.route('/get_auto_selection', methods=['POST'])
def get_auto_selection():
    data = request.json
    if 'imageData' not in data or 'pattern' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    pattern = data['pattern']
    image_data = data['imageData']
    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_data))
    image = np.array(image.convert('L'))

    # Aquí puedes ajustar la lógica de selección en función del patrón
    x, y, size = 0, 0, 4
    max_lux = -1

    if pattern == "ECE-R":
        # Lógica para ECE-R
        pass
    elif pattern == "ECE-L":
        # Lógica para ECE-L
        pass
    elif pattern == "ECE-simétrico":
        # Lógica para ECE-simétrico
        pass
    elif pattern == "VOL":
        # Lógica para VOL
        pass
    elif pattern == "VOR":
        # Lógica para VOR
        pass
    elif pattern == "DOT/SAE mecánico":
        # Lógica para DOT/SAE mecánico
        pass

    # Ejemplo de lógica básica (sin cambios)
    for i in range(0, image.shape[0] - size, size):
        for j in range(0, image.shape[1] - size, size):
            region = image[i:i+size, j:j+size]
            average_intensity = np.mean(region)
            if average_intensity > max_lux:
                max_lux = average_intensity
                x, y = j + size // 2, i + size // 2

    return jsonify({"x": x, "y": y, "size": size})

if __name__ == '__main__':
    app.run(debug=True)
