import cv2
import numpy as np

# Función de calibración: Define la relación entre intensidad promedio y lux
# Estos valores deben ser ajustados en función de tu calibración
PIXEL_TO_LUX_CONVERSION_FACTOR = 0.1  # Ejemplo, ajustar según la calibración

def pixel_to_lux(pixel_intensity):
    return pixel_intensity * PIXEL_TO_LUX_CONVERSION_FACTOR

# Inicializa la cámara web
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

print("Presiona 'c' para capturar una foto.")

while True:
    # Captura un fotograma de la cámara
    ret, frame = cap.read()

    if not ret:
        print("No se pudo capturar un fotograma.")
        break

    # Muestra el fotograma en una ventana
    cv2.imshow('Video en vivo', frame)

    # Espera a que se presione una tecla
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        # Captura una imagen
        captured_image = frame.copy()

        # Convierte la imagen a escala de grises
        gray_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)

        # Calcula la intensidad promedio de los píxeles
        average_intensity = np.mean(gray_image)

        # Convierte la intensidad promedio a lux
        lux_value = pixel_to_lux(average_intensity)

        # Muestra el valor de lux en la consola
        print(f"Valor de luz (lux): {lux_value:.2f}")

        # Muestra la imagen capturada
        cv2.imshow('Imagen Capturada', captured_image)
        cv2.waitKey(0)  # Espera hasta que se presione una tecla

        # Salir del bucle
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
