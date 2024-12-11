import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QTextEdit

class PrinterClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Connect Button
        self.connect_button = QPushButton('Connect to Printer', self)
        self.connect_button.clicked.connect(self.connect_to_printer)
        layout.addWidget(self.connect_button)

        # Image Upload
        self.upload_button = QPushButton('Upload Image', self)
        self.upload_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_button)

        self.image_label = QLabel('No image selected', self)
        layout.addWidget(self.image_label)

        # G-code Input
        self.gcode_input = QTextEdit(self)
        self.gcode_input.setPlaceholderText('Enter G-code here...')
        layout.addWidget(self.gcode_input)

        # Send G-code Button
        self.send_gcode_button = QPushButton('Send G-code', self)
        self.send_gcode_button.clicked.connect(self.send_gcode)
        layout.addWidget(self.send_gcode_button)

        self.setLayout(layout)
        self.setWindowTitle('Printer Client')
        self.setGeometry(300, 300, 400, 300)

    def connect_to_printer(self):
        response = requests.post('http://localhost:5000/connect', json={})
        if response.status_code == 200:
            self.connect_button.setText('Connected')
        else:
            self.connect_button.setText('Failed to Connect')

    def upload_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
        if file_name:
            self.image_label.setText(file_name)
            response = requests.post('http://localhost:5000/print_image', json={'image_path': file_name})
            if response.status_code == 200:
                self.image_label.setText('Image uploaded successfully')
            else:
                self.image_label.setText('Failed to upload image')

    def send_gcode(self):
        gcode = self.gcode_input.toPlainText()
        response = requests.post('http://localhost:5000/send_gcode', json={'commands': gcode.splitlines()})
        if response.status_code == 200:
            self.gcode_input.setPlainText('G-code sent successfully')
        else:
            self.gcode_input.setPlainText('Failed to send G-code')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = PrinterClient()
    client.show()
    sys.exit(app.exec_())