import socket
import sys

sys.path.insert(0, '..')
from modules.close_port import handle_close_port
from modules.codigo_generator import generar_codigo

class ServiceRegistro:
    def __init__(self):
        self.server_address = ('localhost', 5001)

    def imprimir(self, data):
        print("Registro| ", data)

    def handle_request(self, client_socket):
        try:
            request = client_socket.recv(1024).decode()
            
            # Agregar Codigo Usuario Aleatorio
            indice = request.rfind(')')
            request = request[:indice] + f", '{generar_codigo()}'" + request[indice:]
            self.imprimir(request)

            # Manejo de datos
            transaccion = request[:5]
            service_name = request[5:10]
            data_content = request[10:]
            data = data_content.split(',')
            print(data[5])
            rut_trabajador = data[5]

            # Comunicación con el servicio de Base de Datos
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                # Buscar trabajador por rut
                request_id = (f"{transaccion}busca{rut_trabajador}")
                db_socket.connect(('localhost', 5003))
                db_socket.send(request_id.encode())
                db_response = db_socket.recv(1024).decode()
                
                id_trabajador = db_response[2:]
                    
                # Registrar trabajador
                if(id_trabajador is None):
                    request_regis = (f"{transaccion}{service_name}{data}")
                    db_socket.send(request_regis.encode())
                    db_response = db_socket.recv(1024).decode()
                    status= db_response[:2]
                    id_trabajador = db_response[2:]
                    response = {f"{transaccion}{db_response}Usuario registrado con id '{id_trabajador}'."}
                else:
                    response = (f"{transaccion}SREl usuario ya se encuentra registrado con id '{id_trabajador}'.")

                # Respuesta Cliente
                self.imprimir(response)
                client_socket.sendall(response.encode())
            except Exception as e:
                self.imprimir(e)
                response = (f"{SR}{e}")
                return response


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.server_address)
            s.listen(1)
            self.imprimir(f"Servicio de Registro iniciado en {self.server_address}")
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
