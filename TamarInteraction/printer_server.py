from flask import Flask, request, jsonify
import cv2
import numpy as np
from PIL import Image, ImageDraw
import os

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "Server is alive"}), 200

@app.route('/send_gcode', methods=['POST'])
def send_gcode():
    data = request.get_json()
    commands = data.get('commands', [])
    if not commands:
        return jsonify({"error": "No G-code commands provided"}), 400

    # Process the G-code commands
    try:
        draw_gcode(commands)
        return jsonify({"status": "G-code processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def draw_gcode(commands, output_path='output_image.png', delay=1):
    # First pass to determine the maximum width and height
    max_x = max_y = 0
    for command in commands:
        if command.startswith('G0') or command.startswith('G1'):
            parts = command.split()
            for part in parts:
                if part.startswith('X'):
                    x = float(part[1:])
                    max_x = max(max_x, x)
                elif part.startswith('Y'):
                    y = float(part[1:])
                    max_y = max(max_y, y)

    # Create a blank white image with determined dimensions
    width, height = int(max_x), int(max_y)
    output_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output_image)

    # Use the first command's position as the starting point
    first_command = commands[0]
    parts = first_command.split()
    start_x = start_y = 0
    for part in parts:
        if part.startswith('X'):
            start_x = float(part[1:])
        elif part.startswith('Y'):
            start_y = float(part[1:])
    current_position = (start_x, start_y)

    # Second pass to draw the lines
    for command in commands:
        if command.startswith('G0') or command.startswith('G1'):
            parts = command.split()
            x = y = None
            for part in parts:
                if part.startswith('X'):
                    x = float(part[1:])
                elif part.startswith('Y'):
                    y = float(part[1:])
            if x is not None and y is not None:
                new_position = (x, y)
                if command.startswith('G1'):  # Only draw lines for G1 commands
                    draw.line([current_position, new_position], fill="red", width=2)
                current_position = new_position

                # Convert PIL image to OpenCV format and display
                cv_image = cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)
                cv2.imshow('Drawing', cv_image)
                cv2.waitKey(int(delay))  # Wait for the specified delay in milliseconds

    cv2.destroyAllWindows()
    output_image.save(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12346) 