import socket
import time
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout

# Global variable to hold the socket connection
s = None

def reconnect():
    """Attempt to reconnect the socket."""
    global s
    s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Retry mechanism with exponential backoff
    max_retries = 5
    base_delay = 1  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            s.connect(('10.100.102.50', 12345))
            print("Reconnected to the server.")
            return True
        except socket.error:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # exponential backoff
                time.sleep(delay)
            else:
                print("Failed to reconnect to the server after several attempts.")
                return False

def on_button_press():
    """Handle button press event."""
    global s
    try:
        s.sendall("button_pressed".encode())
    except socket.error:
        print("Socket error on button press. Attempting to reconnect...")
        if reconnect():
            s.sendall("button_pressed".encode())

def on_button_release():
    """Handle button release event."""
    global s
    try:
        s.sendall("button_released".encode())
    except socket.error:
        print("Socket error on button release. Attempting to reconnect...")
        if reconnect():
            s.sendall("button_released".encode())

def main():
    """Main function to set up the UI."""
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Retry mechanism with exponential backoff
    max_retries = 5
    base_delay = 1  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            s.connect(('10.100.102.50', 12345))
            break
        except socket.error:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # exponential backoff
                time.sleep(delay)
            else:
                print("Failed to connect to the server after several attempts.")
                return

    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Button Simulator")

    button = QPushButton("Press Me")
    button.pressed.connect(on_button_press)
    button.released.connect(on_button_release)

    layout = QVBoxLayout()
    layout.addWidget(button)
    window.setLayout(layout)

    window.show()

    # Ensure the socket is closed when the application exits
    app.aboutToQuit.connect(lambda: s.close())

    app.exec_()

if __name__ == "__main__":
    main()