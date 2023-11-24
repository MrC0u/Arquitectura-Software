import socket
import sys
import re

sys.path.insert(0, '..')
from modules.close_port import handle_close_port
from modules.codigo_generator import generar_codigo

class ServiceAuth:
    def __init__(self):
        self.server_address = ('localhost', 5005)

    def imprimir(self, data):
        print("Auth| ", data)

    def handle_request(self, client_socket):
        try:
            request = client_socket.recv(1024).decode()
            # Manejo de datos
            transaccion = request[:5]
            service_name = request[5:10]
            data_content = request[10:]
            
            # Obtencion de id_trabajador segun servicio
            if(service_name == 'qring' or service_name == 'qrsal'):
                data = data_content.split(',')
                id_trabajador = data[0]
            else:
                data = data_content.strip('()').split('.')
                if(len(data) != 2):
                    response = f"{transaccion}SACodigo QR no valido."
                    self.imprimir("CodigoQR No valido")
                    client_socket.sendall(response.encode())
                    return None
                id_trabajador = data[0] 
                qr_code = data[1]

            # Verificar existencia de id_trabajador
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket0:
                # Buscar trabajador por rut
                request_id = (f"{transaccion}check('{id_trabajador}')")
                db_socket0.connect(('localhost', 5003))
                db_socket0.send(request_id.encode())
                db_response = db_socket0.recv(1024).decode()
                response = db_response[2:]
                
            if(str(response) == "None"):
                service_response = f"{transaccion}SAEl usuario con id '{id_trabajador}' no existe."
                self.imprimir(service_response)
                client_socket.sendall(service_response.encode())
                return None

            # Obtener ultimo QR desde base de datos
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                # Buscar trabajador por rut
                request_id = (f"{transaccion}getqr('{id_trabajador}')")
                db_socket.connect(('localhost', 5003))
                db_socket.send(request_id.encode())
                db_response = db_socket.recv(1024).decode()
                response = db_response[2:]

            if(str(response) == "None"):
                service_response = f"{transaccion}SAEl usuario con id '{id_trabajador}' no ha generado un codigo QR."
                self.imprimir(service_response)
                client_socket.sendall(service_response.encode())
                return None

            response = response.strip('()')
            qr_response = response.split('.')
            # Bypass
            if(service_name == 'qring' or service_name == 'qrsal'):
                    qr_code = qr_response[1]

            # Verificacion de QR
            if(qr_code == qr_response[1]):
                # Comunicación con el servicio de Base de Datos
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket1:
                    # Buscar trabajador por rut
                    request_id = (f"{transaccion}estad('{id_trabajador}')")
                    db_socket1.connect(('localhost', 5003))
                    db_socket1.send(request_id.encode())
                    db_response = db_socket1.recv(1024).decode()
                    registro = db_response[2:]
                    if(registro != "None"):
                        registro = re.findall(r"'([^']+)'", registro)
                    else:
                        registro = ('None',)

                print(registro)
                if(service_name == "qring" or service_name == "ingre"):
                    print("ingresando")
                    if(str(registro[0]) == "None" or str(registro[0]) == "retirado"):
                        # Comunicación con el servicio de Base de Datos
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket2:
                            # Buscar trabajador por rut
                            request_id = (f"{transaccion}ingre('{id_trabajador}','ingresado')")
                            db_socket2.connect(('localhost', 5003))
                            db_socket2.send(request_id.encode())
                            db_response = db_socket2.recv(1024).decode()
                            ingreso = db_response[2:]

                            service_response = f"{transaccion}OKUsuario ingresado."
                    
                    else:
                        service_response = f"{transaccion}SAAcceso Denegado: El usuario con id '{id_trabajador}' ya se encuentra ingresado."
                elif(service_name == "qrsal" or service_name == "salid"):
                    if(str(registro[0]) == "None" or str(registro[0]) == "ingresado"):
                        # Comunicación con el servicio de Base de Datos
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket2:
                            # Buscar trabajador por rut
                            request_id = (f"{transaccion}salid('{id_trabajador}','retirado')")
                            db_socket2.connect(('localhost', 5003))
                            db_socket2.send(request_id.encode())
                            db_response = db_socket2.recv(1024).decode()
                            ingreso = db_response[2:]

                            service_response = f"{transaccion}OKUsuario retirado."
                    
                    else:
                        service_response = f"{transaccion}SAAcceso Denegado: El usuario con id '{id_trabajador}' ya se encuentra retirado."
            else:
                service_response = f"{transaccion}SAAcceso Denegado: El codigo QR no es el ultimo registrado en el sistema para el usuario id '{id_trabajador}'."
            # Respuesta Cliente
            self.imprimir(service_response)
            client_socket.sendall(service_response.encode())
        except Exception as e:
            self.imprimir(e)
            response = (f"SR{e}")
            return response


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.server_address)
            s.listen(1)
            self.imprimir(f"Servicio de Autenticacion iniciado en {self.server_address}")
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        self.handle_request(conn)
                except Exception as e:
                        self.imprimir(e)

if __name__ == "__main__":
    handle_close_port()
    auth_service = ServiceAuth()
    auth_service.run()
