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
    # Create a blank white image
    width, height = 500, 500  # Example dimensions
    output_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(output_image)

    current_position = (0, 0)

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
                draw.line([current_position, new_position], fill="red", width=2)
                current_position = new_position

                # Convert PIL image to OpenCV format and display
                cv_image = cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)
                cv2.imshow('Drawing', cv_image)
                cv2.waitKey(int(delay * 1000))  # Wait for the specified delay in milliseconds

    cv2.destroyAllWindows()
    output_image.save(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12346) 