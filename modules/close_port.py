import signal
import sys

def signal_handler(sig, frame):
    print("Cerrando puerto...")
    sys.exit(0)

def handle_close_port():
    signal.signal(signal.SIGINT, signal_handler)  # Capturar la señal Ctrl+C