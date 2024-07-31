import cv2
import numpy as np

# Definir los valores para cada celda de la cuadrícula
values = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]

# Inicializa la cámara web
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

print("Presiona 'c' para capturar una foto.")
print("Presiona 'q' para salir del programa.")

# Definir una función de conversión de intensidad a lux
def pixel_to_lux(intensity):
    # Esta es una conversión de ejemplo, ajusta según sea necesario
    return intensity * 0.1  # Cambia este factor según tus necesidades

# Función para obtener la celda de la cuadrícula en función de las dimensiones de la imagen
def get_cell_from_position(x, y, cell_width, cell_height):
    col = x // cell_width
    row = y // cell_height
    return col, row

# Variables para el selector
selector_color = (0, 0, 255)  # Rojo
selector_thickness = 2
selector_size = 10  # Tamaño del selector

# Variables del selector
selector_x, selector_y = -1, -1  # Posición inicial del selector
selector_active = False  # Estado del selector

def mouse_callback(event, x, y, flags, param):
    global selector_x, selector_y, selector_active
    if event == cv2.EVENT_LBUTTONDOWN:
        selector_x, selector_y = x, y
        selector_active = True  # Activa el selector

while True:
    # Captura un fotograma de la cámara
    ret, frame = cap.read()

    if not ret:
        print("No se pudo capturar un fotograma.")
        break

    # Crea una copia del fotograma para dibujar la cuadrícula y el selector
    grid_frame = frame.copy()

    # Define la altura y el ancho de la cuadrícula
    cell_width = frame.shape[1] // 2  # La imagen tiene 2 columnas
    cell_height = frame.shape[0] // 13  # La imagen tiene 13 filas

    # Dibuja la cuadrícula
    for i in range(13):
        for j in range(2):
            # Dibuja rectángulos en ambas columnas
            top_left = (j * cell_width, i * cell_height)
            bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
            cv2.rectangle(grid_frame, top_left, bottom_right, (0, 255, 0), 1)

    # Añade el texto solo en la columna izquierda
    for i in range(13):
        if i < len(values):
            text = f'{values[i]}%'
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            text_x = 5  # Margen de 5 píxeles desde el borde izquierdo de la columna izquierda
            text_y = (i * cell_height) + (cell_height + text_size[1]) // 2
            cv2.putText(grid_frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)  # Color verde

    # Dibuja el selector en la posición del clic si está activo
    if selector_active:
        # Dibuja un rectángulo alrededor del área seleccionada
        top_left = (selector_x - selector_size, selector_y - selector_size)
        bottom_right = (selector_x + selector_size, selector_y + selector_size)
        cv2.rectangle(grid_frame, top_left, bottom_right, selector_color, selector_thickness)

        # Calcula la región de interés en la imagen
        roi_x1 = max(selector_x - selector_size, 0)
        roi_y1 = max(selector_y - selector_size, 0)
        roi_x2 = min(selector_x + selector_size, frame.shape[1])
        roi_y2 = min(selector_y + selector_size, frame.shape[0])

        # Extrae la región de interés en la imagen capturada
        roi_gray = cv2.cvtColor(frame[roi_y1:roi_y2, roi_x1:roi_x2], cv2.COLOR_BGR2GRAY)

        # Calcula la intensidad promedio de los píxeles en la región de interés
        average_intensity = np.mean(roi_gray)
        lux_value = pixel_to_lux(average_intensity)

        # Muestra el valor de lux en la consola
        print(f"Región seleccionada: ({roi_x1}, {roi_y1}) a ({roi_x2}, {roi_y2})")
        print(f"Valor de luz (lux): {lux_value:.2f}")

    # Muestra el fotograma con la cuadrícula y el selector en una ventana
    cv2.imshow('Video en vivo', grid_frame)

    # Configura el callback del mouse
    cv2.setMouseCallback('Video en vivo', mouse_callback)

    # Espera a que se presione una tecla
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        # Captura una imagen
        captured_image = frame.copy()
        cv2.imshow('Imagen Capturada', captured_image)
        cv2.waitKey(0)  # Espera hasta que se presione una tecla

    elif key == ord('q'):
        # Salir del bucle
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
