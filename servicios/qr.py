from flask import Flask, render_template, request, send_file
import qrcode
import os

app = Flask(__name__)

# Variables para el código QR y datos del formulario
qr_data = "Ejemplo de datos para el código QR"
usuario_valido = "1"
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
    # Generar el código QR
    qr_path = 'static/temp_qr.png'
    generate_qr_code(qr_data, qr_path)

    # Enviar el archivo como respuesta para descargar
    return send_file(qr_path, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

# Ruta para la página principal con el formulario
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')

        if usuario == usuario_valido and clave == clave_valida:
            mensaje = "Credenciales correctas. Descarga el QR."
            qr_path = "temp_qr.png"
        else:
            mensaje = "Credenciales incorrectas. Acceso no autorizado."
            qr_path = ""
    else:
        mensaje = "Ingrese sus credenciales"
        qr_path = ""
    return render_template('index.html', mensaje=mensaje, qr_path=qr_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
