import socket
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, '..')
from modules.close_port import handle_close_port

class DatabaseService:
    def __init__(self, database_name='arqui.db'):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

        # Crear Tabla Rol
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rol (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_rol TEXT,
                descripcion TEXT
            )
        ''')

        # Crear Tabla area
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS area (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                piso TEXT,
                sede TEXT
            )
        ''')

        # Crear Tabla trabajadores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                area_id INTEGER,
                correo TEXT,
                contraseña TEXT,
                rol_id INTEGER,
                codigo_personal INTEGER,
                rut TEXT,
                FOREIGN KEY (area_id) REFERENCES area(id),
                FOREIGN KEY (rol_id) REFERENCES rol(id)
            )
        ''')

        # Crear Tabla Acceso
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS acceso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tipo_acceso INTEGER,
                qr_code,
                FOREIGN KEY (user_id) REFERENCES usuario(id)
            )
        ''')

        # Crear Tabla Registro
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                fecha_hora DATE,
                registro TEXT,
                FOREIGN KEY (user_id) REFERENCES usuario(id)
            )
        ''')

        # Crear Tabla Visita
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS visita (
                id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                nombre INTEGER,
                rut TEXT,
                fecha DATE,
                FOREIGN KEY (user_id) REFERENCES usuario(id),
                FOREIGN KEY (nombre) REFERENCES usuario(nombre),
                FOREIGN KEY (rut) REFERENCES usuario(rut)
            )
        ''')
        self.connection.commit()

        # Crear Ejemplos
        # Areas
        self.cursor.execute('''
            SELECT COUNT(*) FROM area
        ''',)

        existe_area = self.cursor.fetchone()[0]
        if not existe_area:
            self.cursor.execute('''
                INSERT INTO area (nombre, piso, sede)
                VALUES ('Ejercito 441', '1', 'Ingenieria y Ciencias')
            ''',)
            self.cursor.execute('''
                INSERT INTO area (nombre, piso, sede)
                VALUES ('Ejercito 441', '2', 'Ingenieria y Ciencias')
            ''',)
            self.cursor.execute('''
                INSERT INTO area (nombre, piso, sede)
                VALUES ('Ejercito 441', '3', 'Ingenieria y Ciencias')
            ''',)
            self.cursor.execute('''
                INSERT INTO area (nombre, piso, sede)
                VALUES ('Ejercito 441', '4', 'Ingenieria y Ciencias')
            ''',)
            self.cursor.execute('''
                INSERT INTO area (nombre, piso, sede)
                VALUES ('Ejercito 441', '5', 'Ingenieria y Ciencias')
            ''',)
            self.connection.commit()

        # Rol
        self.cursor.execute('''
            SELECT COUNT(*) FROM rol
        ''',)

        existe_rol = self.cursor.fetchone()[0]
        if not existe_area:
            self.cursor.execute('''
                INSERT INTO rol (nombre_rol, descripcion)
                VALUES ('Administrador', 'Administrador del sistema.')
            ''',)
            self.cursor.execute('''
                INSERT INTO rol (nombre_rol, descripcion)
                VALUES ('Guardia', 'Permite el ingreso de los trabajadores.')
            ''',)
            self.cursor.execute('''
                INSERT INTO rol (nombre_rol, descripcion)
                VALUES ('Trabajador', 'Trabajador de una oficina.')
            ''',)
            self.cursor.execute('''
                INSERT INTO rol (nombre_rol, descripcion)
                VALUES ('Visita', 'Visitante de una oficina.')
            ''',)
            self.connection.commit()

    def fecha_hora(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def imprimir(self, data):
        print("DB| ", data)

    def buscar_rut(self,rut):
        self.cursor.execute('''
            SELECT id FROM usuario where rut = ?
        ''',(rut))

        result = self.cursor.fetchone()
        if result is not None:
            id = result[0]
            return id
        else:
            return None

    def registrar_usuario(self,data):
        self.cursor.execute(
            "INSERT INTO usuario (nombre, area_id, correo, contraseña, rol_id, rut, codigo_personal) VALUES (?, ?, ?, ?, ?, ?, ?)",
            data
        )
        self.connection.commit()

        self.cursor.execute('SELECT last_insert_rowid()')
        id_usuario = self.cursor.fetchone()[0]

        return id_usuario


    def ingresar_usuario(self,data):
        self.cursor.execute(
            "INSERT INTO REGISTRO (user_id, fecha_hora, registro) VALUES (?, ?, ?)",
            data[0], self.fecha_hora(), data[1]
        )

    def handle_request(self, request):
        try:
            service_name = request[5:10]
            data_content = request[10:]
            data = data_content.split(',')
            status = "OK"

            if service_name == "regis":
                response = self.ingresar_usuario(data)
            elif service_name == "ingre":
                response = self.ingresar_usuario(data)
            elif service_name == "busca":
                response = self.buscar_rut(data)
            elif service_name == "salid":
                response = self.registrar_usuario(data)
            elif service_name == "estad":
                response = self.registrar_usuario(data)
            else:
                response = (f"No se encuentra el servicio '{service_name}'.")
                status = "BD"
            response = f"{str(status)}{str(response)}"
            self.imprimir(response)
            return response
        except Exception as e:
            response = (f"{BD}{e}")
            self.imprimir(e)
            return response
               

        # Agrega más lógica para otros tipos de solicitudes de base de datos aquí...

    def run(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 5003))  # Asignar un puerto para el servicio de base de datos
                s.listen(1)
                print("Servicio de Base de Datos iniciado en puerto 5003")
                while True:
                    try:
                        conn, addr = s.accept()
                        with conn:
                            data = conn.recv(1024).decode()
                            response = self.handle_request(data)
                            conn.sendall(response.encode())
                    except Exception as e:
                        self.imprimir(e)

if __name__ == "__main__":
    handle_close_port()
    database_service = DatabaseService()
    database_service.run()
