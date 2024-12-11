from flask import Flask, request, jsonify
import asyncio
from TamarInteraction.printer_manager import RealPrinter

app = Flask(__name__)
printer = RealPrinter()

@app.route('/connect', methods=['POST'])
def connect_printer():
    data = request.json
    port = data.get('port', '/dev/ttyAMA0')
    baudrate = data.get('baudrate', 115200)
    wait = data.get('wait', True)
    
    asyncio.run(printer.connect(port, baudrate, wait))
    return jsonify({"status": "connected"}), 200

@app.route('/send_gcode', methods=['POST'])
def send_gcode():
    data = request.json
    commands = data.get('commands', [])
    
    if not commands:
        return jsonify({"error": "No G-code commands provided"}), 400
    
    asyncio.run(printer.send_commands(commands))
    return jsonify({"status": "commands sent"}), 200

@app.route('/print_image', methods=['POST'])
def print_image():
    data = request.json
    image_path = data.get('image_path')
    scale_factor = data.get('scale_factor', 0.75)
    
    if not image_path:
        return jsonify({"error": "No image path provided"}), 400
    
    asyncio.run(printer.print_image(image_path, scale_factor))
    return jsonify({"status": "image printing started"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 