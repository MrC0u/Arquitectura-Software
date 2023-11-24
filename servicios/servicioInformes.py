import socket
import sys

sys.path.insert(0, '..')
from modules.close_port import handle_close_port
from modules.codigo_generator import generar_codigo

class ServiceRegistro:
    def __init__(self):
        self.server_address = ('localhost', 5002)

    def imprimir(self, data):
        print("Informes| ", data)

    def handle_request(self, client_socket):
        try:
            request = client_socket.recv(1024).decode()
            
            # Manejo de datos
            transaccion = request[:5]
            service_name = request[5:10]
            data_content = request[10:]

            self.imprimir(f"Solicitud al servicio '{service_name}'")

            if(service_name == "infou"):
                data = data_content.split(',')
                rut_trabajador = data[0]
                # Comunicación con el servicio de Base de Datos

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                    # Buscar trabajador por rut
                    request = f"{transaccion}infou('{rut_trabajador}')"
                    db_socket.connect(('localhost', 5003))
                    db_socket.send(request.encode())
                    db_response = db_socket.recv(1024).decode()
                    db_status = db_response[2:]

                    if(db_status == "None"):
                        response = f"{transaccion}SINo se encuentran registros para el rut ingresado."
                    else:
                        response = f"{transaccion}{db_response}"

            if(service_name == "histo"):
                # Comunicación con el servicio de Base de Datos

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                    # Buscar trabajador por rut
                    request = f"{transaccion}histo('')"
                    db_socket.connect(('localhost', 5003))
                    db_socket.send(request.encode())
                    db_response = db_socket.recv(1024).decode()
                    db_status = db_response[:2]
                    db_data = db_response[2:]

                    if(db_status == "BD" or db_data == "[]"):
                        response = f"{transaccion}SINo se encuentran registros."
                    else:
                        response = f"{transaccion}{db_status}{db_data}"

            if(service_name == "canti"):
                data = data_content.split(',')
                id_area = data[0]
                # Comunicación con el servicio de Base de Datos

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                    # Buscar trabajador por rut
                    request = f"{transaccion}canti('{id_area}')"
                    db_socket.connect(('localhost', 5003))
                    db_socket.send(request.encode())
                    db_response = db_socket.recv(1024).decode()
                    db_status = db_response[:2]
                    db_data = db_response[2:]

                    if(db_status == "BD"):
                        response = f"{transaccion}SINo se encuentran registros para el id ingresado."
                    else:
                        response = f"{transaccion}{db_status}Se encuentran '{db_data}' usuarios en el edificio con id '{id_area}'."

            # Respuesta Cliente
            self.imprimir(response)
            client_socket.sendall(str(response).encode())
        except Exception as e:
            self.imprimir(e)
            response = (f"SI{e}")
            return response


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.server_address)
            s.listen(1)
            self.imprimir(f"Servicio de Informes iniciado en {self.server_address}")
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        self.handle_request(conn)
                except Exception as e:
                        self.imprimir(e)

if __name__ == "__main__":
    handle_close_port()
    registro_service = ServiceRegistro()
    registro_service.run()
