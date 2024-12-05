import socket
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout

# Global variable to hold the socket connection
s = None

def on_button_press():
    """Handle button press event."""
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 13346))
    s.sendall("button_pressed".encode())

def on_button_release():
    """Handle button release event."""
    global s
    s.sendall("button_released".encode())
    s.close()
    s = None

def main():
    """Main function to set up the UI."""
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
    app.exec_()

if __name__ == "__main__":
    main()