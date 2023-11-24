import socket

def send_request(service_name, data, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', port))

        if(service_name == "regis"):
            destination_address = ('localhost', 5001)
        if(service_name == "ingre" or service_name == "qring" or service_name == "qrsal" or service_name == "salid"):
            destination_address = ('localhost', 5005)
        if(service_name == "infou" or service_name == "canti" or service_name == "histo"):
            destination_address = ('localhost', 5002)
            
        sock.connect(destination_address)
        transaction = f"{(len(service_name) + len(data)):05}{service_name}{data}"

        sock.sendall(transaction.encode())
        response = sock.recv(1024).decode()
    return response