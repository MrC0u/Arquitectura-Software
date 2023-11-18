import socket

def get_available_local_port():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))  # 0 indica que se seleccionará un puerto local disponible automáticamente
        _, local_port = sock.getsockname()
        sock.close()
        return local_port