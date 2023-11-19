from flask import Flask, render_template, request, send_file
import qrcode
import os
import socket
import sys
import re

sys.path.insert(0, '..')
from modules.close_port import handle_close_port
from modules.codigo_generator import generar_codigo

app = Flask(__name__)

# Variables para el código QR y datos del formulario
#qr_data = "Ejemplo de datos para el código QR"
correo_valido = "1"
clave_valida = "1"

# Directorio para almacenar temporalmente la imagen del código QR
TEMP_DIR = 'temp'

# Función para generar el código QR
def generate_qr_code(data, path):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Crear el directorio si no existe
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Guardar la imagen en la ruta especificada
    img.save(path)

# Ruta para obtener el código QR como imagen
@app.route('/get_qr_code', methods=['POST'])
def get_qr_code():
    # Enviar el archivo como respuesta para descargar
    return send_file('static/temp_qr.png', mimetype='image/png', as_attachment=True, download_name='qr_code.png')

# Ruta para la página principal con el formulario
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        correo = request.form.get('correo')
        clave = request.form.get('clave')
        # Comunicación con el servicio de Base de Datos
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
            # Buscar por correo y comprobar clave
            data = (f"({correo},{clave})")
            service_name = "login"
            transaccion = f"{(len(service_name) + len(data)):05}"  
            request_db = (f"{transaccion}{service_name}('{correo}','{clave}')")
            db_socket.connect(('localhost', 5003))
            db_socket.send(request_db.encode())
            db_response = db_socket.recv(1024).decode()
            db_response_data = db_response[2:]
            id_response = db_response_data.strip("()").split(',')
            print('data: ', id_response)

        if(str(id_response[0]) != 'False'):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket2:
                # 
                print(id_response)
                qr_data = f"({id_response[0]}.{generar_codigo()})"
                qr_path = "static/temp_qr.png"
                generate_qr_code(qr_data, qr_path)

                data = (f"('{id_response[0]}','{id_response[1]}','{qr_data}')")
                service_name = "setqr"
                transaccion = f"{(len(service_name) + len(data)):05}"  
                request_db = (f"{transaccion}{service_name}{data}")

                db_socket2.connect(('localhost', 5003))
                db_socket2.send(request_db.encode())
                db_response = db_socket2.recv(1024).decode()

                response = db_response[2:]
                if(str(response) == 'True'):
                    mensaje = "Credenciales correctas. Descarga el QR."
                    qr_path = "temp_qr.png"
                else:
                    mensaje = "Error generando el codigo. Comuniquese con el equipo tecnico."
                    qr_path = ""
        else:
            mensaje = "Credenciales incorrectas. Acceso no autorizado."
            qr_path = ""
    else:
        mensaje = "Ingrese sus credenciales"
        qr_path = ""
    return render_template('index.html', mensaje=mensaje, qr_path=qr_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10001)
