from flask import Flask, request, jsonify
import asyncio
from printer_manager import RealPrinter
import os
app = Flask(__name__)
printer = RealPrinter()

@app.before_request
def initialize_printer():
    if not hasattr(app, '_got_first_request'):
        app._got_first_request = True
        asyncio.create_task(printer.start())

@app.route('/connect', methods=['POST'])
async def connect_printer():
    await printer.start()
    return jsonify({"status": "connected"}), 200

@app.route('/send_gcode', methods=['POST'])
async def send_gcode():
    data = request.json
    commands = data.get('commands', [])
    
    if not commands:
        return jsonify({"error": "No G-code commands provided"}), 400
    
    await printer.send_commands(commands)
    return jsonify({"status": "commands sent"}), 200

@app.route('/print_image', methods=['POST'])
async def print_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join('/tmp', file.filename)
    file.save(file_path)

    try:
        # First home the printer and set absolute position mode
        await printer.send_command("G0 Z5")
        await printer.print_image(file_path)
        return jsonify({"status": "image printing started"}), 200
    finally:
        # Ensure the file is deleted after processing
        if os.path.exists(file_path):
            os.remove(file_path)
            
@app.route('/load_gcode', methods=['POST'])
async def load_gcode():
    data = request.json
    gcode_path = data.get('gcode_path', '')
    if not gcode_path:
        return jsonify({"error": "No G-code file path provided"}), 400
    
    # Read the generated G-code
    with open(gcode_path, 'r') as file:
        gcode_commands = file.readlines()
    
    await printer.send_commands(gcode_commands)
    return jsonify({"status": "G-code loaded"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 