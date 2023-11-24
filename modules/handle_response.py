def response_print(data):
    transaccion = data[:5]
    status = data[5:7]
    response = data[7:]
    print("\n======= o =======")
    print(f"Transaccion: {transaccion}")
    print(f"Status: {status}")
    print(f"Mensaje: {response}")
    print("=======---=======")
