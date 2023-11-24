import socket
import sys
import re
from tabulate import tabulate

sys.path.insert(0, '..')
from modules.error_message import error_print
from modules.get_port import get_available_local_port
from modules.send_request import send_request
from modules.codigo_generator import generar_codigo
from modules.handle_response import response_print
from modules.qr_read import leer_qr

class Admin:
    def __init__(self):
        pass

    def run(self):
        while True:
            try:
                print("\n--- Sistema de Administracion ---")
                print("1. Registrar trabajador")
                print("2. Ingreso de trabajador")
                print("3. Salida de trabajador")
                print("4. Verificar estado de trabajador por rut")
                print("5. Historial de accesos")
                print("6. Verificar cantidad de empleados dentro de un departamento")
                print("7. Salir")

                opcion = int(input("Seleccione una opción: "))
                local_port = get_available_local_port()
                # Registro de trabajador
                if opcion == 1:
                    # Ingreso de datos
                    nombre = input("Ingrese el nombre del trabajador: ")
                    rut = input("Ingrese el rut del trabajador: ")
                    email = input("Ingrese el email del trabajador: ")
                    contraseña = input("Ingrese la contraseña del trabajador: ")
                    area_id = input("Ingrese el id del area: ")
                    print("Roles: 1=Admin, 2=Guardia, 3=Trabajador, 4=Visita")
                    rol_id = input("Ingrese el id del rol: ")
                    data = (nombre, area_id, email, contraseña, rol_id, rut)
                    
                    # Envio de datos
                    response = send_request("regis", data, local_port)
                    response_print(response)
                
                # Ingreso de trabajador
                elif opcion == 2:
                    # Activar para saltar la lectura de codigo (Y obtener el ultimo de la BD).
                    #bypass = input("[ADMIN] Bypass activado? y/n: ")
                    bypass = "n"
                    
                    if(bypass == 'y' or bypass == '1'):
                        print("--- o ---")
                        data_request = input("Ingrese el 'id' del trabajador: ")
                        service_name = "qring"
                    else:
                        # Lectura de QR
                        print("Acerque el codigo QR a la camara.")
                        service_name = "ingre"
                        data_request = leer_qr()

                    response = send_request(service_name, data_request, local_port)
                    
                    transaccion = response[:5]
                    status = response[5:7]
                    data = response[7:]

                    response_print(response)
                # Salida de trabajador
                elif opcion == 3:
                    # Activar para saltar la lectura de codigo (Y obtener el ultimo de la BD).
                    #bypass = input("[ADMIN] Bypass activado? y/n: ")
                    bypass = "n"
                    
                    if(bypass == 'y' or bypass == '1'):
                        print("--- o ---")
                        data_request = input("Ingrese el 'id' del trabajador: ")
                        service_name = "qrsal"
                    else:
                        # Lectura de QR
                        print("Acerque el codigo QR a la camara.")
                        service_name = "salid"
                        data_request = leer_qr()

                    response = send_request(service_name, data_request, local_port)
                    
                    transaccion = response[:5]
                    status = response[5:7]
                    data = response[7:]

                    response_print(response)
                # Verificar estado del trabajador
                elif opcion == 4:
                    rut_trabajador = input("Ingrese rut del trabajador: ")
                    service_name = "infou"
                    response = send_request(service_name, rut_trabajador, local_port)
                    
                    transaccion = response[:5]
                    status = response[5:7]
                    data = response[7:]

                    if(status == "SI"):
                        response_print(response)
                    else:
                        data_content = re.findall(r"'([^']+)'", data)
                        response_print(f"{transaccion}{status}\n# Rut: {rut_trabajador} \n# Nombre: {data_content[2]} \n# Registro: {data_content[1]} \n# Fecha: {data_content[0]}")
                # Historial de accesos
                elif opcion == 5:
                    service_name = "histo"
                    response = send_request(service_name, "None", local_port)
                    
                    transaccion = response[:5]
                    status = response[5:7]
                    data = response[7:]
                    lista = eval(data)
                    print(lista)
                    if(status == "SI"):
                        response_print(response)
                    else:
                        tabla = tabulate(lista, headers=["ID","User ID","Nombre","RUT","ID Area","Registro","Fecha Y Hora"], tablefmt="grid")
                        response_print(f"{transaccion}{status}\n{tabla}")
                
                
                # Cantidad de usuarios dentro de un departamento
                elif opcion == 6:
                    service_name = "canti"
                    id_departamento = input("Ingrese el id del departamento: ")
                    response = send_request(service_name, id_departamento, local_port)
                    
                    transaccion = response[:5]
                    status = response[5:7]
                    data = response[7:]

                    response_print(response)
                # Salir
                elif opcion == 7:
                    break
            except Exception as e:
                error_print(e)

if __name__ == "__main__":
    admin_client = Admin()
    admin_client.run()
