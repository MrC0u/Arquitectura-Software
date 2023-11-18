# sudo apt-get install libgl1-mesa-glx
# sudo apt-get install libzbar0
# pip install opencv-python
# pip install pyzbar


import cv2
from pyzbar.pyzbar import decode

def leer_qr():
    # Abre la cámara. Puedes ajustar el índice de la cámara según tu configuración.
    cap = cv2.VideoCapture(0)

    while True:
        # Lee un fotograma de la cámara
        _, frame = cap.read()

        # Decodifica los códigos QR
        qr_codes = decode(frame)

        # Si se detecta algún código QR, imprime el contenido y sale del bucle
        if qr_codes:
            for qr_code in qr_codes:
                qr_data = qr_code.data.decode('utf-8')
                print(f"Resultado del código QR: {qr_data}")
            break

        # Muestra el fotograma de la cámara (puedes comentar esta línea si no quieres visualizar la cámara)
        #cv2.imshow('Camara QR', frame)

        # Sale del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera los recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    leer_qr()
