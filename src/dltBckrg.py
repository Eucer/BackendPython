import cv2
import numpy as np

# Carga la imagen
img = cv2.imread("imagen.jpg")

# Convierte la imagen a una escala de grises
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Aplica un umbral binario para separar el fondo y el objeto
ret, thresh = cv2.threshold(
    gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Encuentra los contornos en la imagen umbralizada
contours, hierarchy = cv2.findContours(
    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Crea una máscara negra
mask = np.zeros_like(img)

# Dibuja los contornos en la máscara
cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)

# Aplica la máscara a la imagen original para eliminar el fondo
result = cv2.bitwise_and(img, mask)

# Muestra y guarda la imagen resultante
cv2.imshow("Result", result)
cv2.imwrite("resultado.jpg", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
