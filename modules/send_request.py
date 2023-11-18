import socket

def send_request(service_name, data, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', port))

        if(service_name == "regis"):
            destination_address = ('localhost', 5001)

            
        sock.connect(destination_address)
        transaction = f"{(len(service_name) + len(data)):05}{service_name}{data}"

        sock.sendall(transaction.encode())
        response = sock.recv(1024).decode()
    return response