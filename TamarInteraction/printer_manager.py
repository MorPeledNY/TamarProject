import cv2
from multiprocessing import Process
from PIL import Image, ImageDraw
import numpy as np
import multiprocessing
import asyncio
import requests
import json
import serial.tools.list_ports
import time
# Add Printrun_master to the Python path
import sys
import os
import random

file_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(file_path)
sys.path.append(os.path.abspath(f'{parent_path}/Printrun_master'))

from printrun.printcore import printcore
from printrun import gcoder

class Printer:
    def __init__(self):
        self.print_in_progress = False

    async def connect(self, port='COM16', baudrate=115200, wait=True):
        """Connect to a printer."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    async def print_image(self, image_path, scale_factor=0.75):
        """Print an image."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    async def send_commands(self, commands: list, wait=True):
        """Send multiple G-code commands to the printer."""
        raise NotImplementedError("This method should be overridden by subclasses.")

    async def send_command(self, command: str):
        """Send a single G-code command."""
        print(f"Sending command: {command}")
        if not self.printer.online:
            print("Printer is not online!")
            return False
            
        # Send the command directly through printcore
        self.printer.send_now(command)
        
        # Give some time for the command to be processed
        await asyncio.sleep(0.1)
        
        return True
        
    def euclidean_distance(self, point1, point2):
        """Calculate the Euclidean distance between two points."""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def get_contour_endpoints(self, contour):
        """Get the start and end points of a contour."""
        return contour[0][0], contour[-1][0]

    async def convert_image_to_gcode(self, image_path, output_gcode_path, ender3_max_x=90, ender3_max_y=120):
        """Convert an image to G-code and save it to a file."""
        print('Start converting image to G-code')

        # Load the image in grayscale and threshold it
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to find or open the image at {image_path}")

        _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Scale the contours to the printer's max x and y
        scale_factor = min(ender3_max_x / image.shape[1], ender3_max_y / image.shape[0])
        scaled_contours = [contour * scale_factor for contour in contours]
        
        # Modified G-code generation with extrusion
        gcode = [
            "G21",          # Set units to millimeters
            "G90",          # Use absolute positioning
            "G92 E0",       # Reset extruder position
            "M82",          # Use absolute distances for extrusion
            "M302 S0",      # Allow cold extrusion
            "G1 F1200",     # Set initial feedrate
            "G1 Z1.7"       # Set initial Z height to 1.7mm for printing
        ]
        
        current_e = 0
        extrusion_rate = -0.1  # Changed to negative to reverse direction
        
        for i, contour in enumerate(scaled_contours):
            start_point = contour[0][0]
            if i > 0:
                # Retract before move (now pushing in)
                current_e += 1
                gcode.append(f"G1 E{current_e} F1800")
                gcode.append(f"G0 X{start_point[0]} Y{start_point[1]} Z2 F3000")  # Changed to Z2
                current_e -= 1
            else:
                gcode.append(f"G0 X{start_point[0]} Y{start_point[1]} Z2")  # Changed to Z2

            # Generate G1 commands with extrusion
            prev_point = None
            for point in contour:
                x, y = point[0]
                if prev_point is not None:
                    # Calculate distance and required extrusion
                    distance = self.euclidean_distance((x, y), prev_point)
                    current_e += distance * extrusion_rate
                    # Z height changed to 1.7
                    gcode.append(f"G1 X{x} Y{y} Z2 E{current_e} F1200")  # Changed to Z2
                prev_point = (x, y)

        # Add end G-code
        gcode.extend([
            "G92 E0",       # Reset extruder position
            "G1 E-3 F1800", # Final retraction
            "G1 Z2",        # Lift Z (changed from 1.7)
            "G90"           # Absolute positioning
        ])

        # Save the G-code to a file
        with open(output_gcode_path, 'w') as file:
            for line in gcode:
                file.write(line + '\n')

        print('Saved new G-code to file:', output_gcode_path)
        return output_gcode_path

    async def graceful_shutdown(self):
        """Gracefully shutdown the printer with proper sequence."""
        raise NotImplementedError("This method should be overridden by subclasses.")

class RealPrinter(Printer):
    # Add class variables at the start of the class
    MAX_X = 90
    MAX_Y = 120
    
    _instance = None
    
    # Add temperature constants
    EXTRUDER_TEMP = 220  # Temperature for PLA
    BED_TEMP = 60
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, baudrate=115200, wait=True):
        super().__init__()
        if not hasattr(self, 'printer'):
            self.printer = printcore()
            self.baudrate = baudrate
            self.wait = wait
            self.port = None
            self.thinking_task = None
            self.printing_task = None
            self.printing_cancelled = False
            self.is_heated = False  # Add flag to track heating status

    def detect_usb_port(self):
        """Auto-detect the first available USB serial port."""
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if 'ttyUSB' in port.device:
                return port.device
        return None

    async def start(self):
        """Initialize printer at start of conversation"""
        await self.connect(self.port, self.baudrate, self.wait)
        if not self.is_heated:
            await self.heat_up()
            self.is_heated = True
        await self.send_commands(["G28", "G0 Z2", "G90"])  # Keep Z2 for non-printing moves

    async def connect(self, port=None, baudrate=115200, wait=True):
        # Auto-detect port if not specified
        if port is None:
            port = self.detect_usb_port()
            if port is None:
                raise RuntimeError("No USB serial port found")
            print(f"Detected printer on port: {port}")

        self.printer.startcb = self._start_callback
        self.printer.endcb = self._end_callback
        await asyncio.to_thread(self.printer.connect, port, baudrate, wait)
        
        # Wait for printer to be online or timeout
        timeout = time.time() + 10
        while not self.printer.online:
            if time.time() > timeout:
                raise RuntimeError("Printer did not connect within 10 seconds")
            await asyncio.sleep(0.1)
        print("Connecting...")
    
    def _start_callback(self, *args):
        self.print_in_progress = True
        
    def _end_callback(self, *args):
        self.print_in_progress = False
    
    async def send_commands(self, commands: list, wait=True):
        # Validate and clip commands if necessary
        validated_commands = []
        for cmd in commands:
            cmd = cmd.strip()
            if cmd.startswith(('G0', 'G1')):
                # Extract X and Y coordinates
                parts = cmd.split()
                new_parts = []
                for part in parts:
                    if part.startswith('X'):
                        x = min(float(part[1:]), self.MAX_X)
                        new_parts.append(f'X{x}')
                    elif part.startswith('Y'):
                        y = min(float(part[1:]), self.MAX_Y)
                        new_parts.append(f'Y{y}')
                    else:
                        new_parts.append(part)
                validated_commands.append(' '.join(new_parts))
            else:
                validated_commands.append(cmd)

        commands_gcode = gcoder.LightGCode(validated_commands)
        await asyncio.to_thread(self.printer.startprint, commands_gcode)
        
        # רק אם wait=True, נחכה עד שההדפסה תסתיים
        if wait:
            timeout = time.time() + 300  # 5 minutes timeout
            while self.print_in_progress and not self.printing_cancelled:
                if time.time() > timeout:
                    print("Warning: Command timeout reached")
                    break
                await asyncio.sleep(0.1)

    async def graceful_shutdown(self):
        print("Executing graceful shutdown...")
        await asyncio.to_thread(self.printer.cancelprint)
        await asyncio.sleep(3)
        
        shutdown_sequence = [
            "G92 E0",
            "M107",      # Fan off
            "M104 S0",   # Extruder heater off
            "G28 X0",    # Home X axis
            "M84",       # Disable motors
            "M140 S0"    # Bed heater off
        ]
        
        for command in shutdown_sequence:
            await self.send_command(command)
            await asyncio.sleep(1)
            
        await asyncio.to_thread(self.printer.disconnect)
        print("Printer shutdown complete")
        
    async def print_image(self, image_path):
        """Print an image on the printer"""
        await self.stop_all(keep_heat=True)  # Keep printer heated
        self.printing_task = asyncio.create_task(self._print_image_task(image_path))

    async def _print_image_task(self, image_path):
        """Background task for image printing"""
        try:
            if not self.is_heated:
                await self.heat_up()
                self.is_heated = True
            
            # Move to start position with Z1.7 for printing
            await self.send_commands(["G28", "G0 Z1.7", "G90"], wait=True)
            
            temp_gcode_path = 'temp_print.gcode'
            gcode_path = await self.convert_image_to_gcode(image_path, temp_gcode_path)
            
            # Read the generated G-code and clean it
            with open(gcode_path, 'r') as file:
                gcode_commands = [line.strip() for line in file.readlines() if line.strip()]
            
            print(f"Starting to print image with {len(gcode_commands)} G-code commands")
            
            # Send commands in batches of 10 instead of one at a time
            batch_size = 10
            for i in range(0, len(gcode_commands), batch_size):
                if self.printing_cancelled:
                    print("Printing cancelled")
                    break
                
                batch = gcode_commands[i:i + batch_size]
                print(f"Sending commands {i+1}-{i+len(batch)}/{len(gcode_commands)}")
                await self.send_commands(batch, wait=True)
                
                # Reduced delay between batches
                await asyncio.sleep(0.1)  # 100ms delay between batches instead of 500ms
            
            print("Finished printing image")
            
        except asyncio.CancelledError:
            print("Image printing cancelled")
            raise
        except Exception as e:
            print(f"Error printing image: {e}")
            raise

    async def stop_all(self, keep_heat=False):
        """Stop all current printer operations"""
        self.print_in_progress = False
        self.printing_cancelled = True
        
        # Cancel existing tasks
        if self.thinking_task:
            self.thinking_task.cancel()
            try:
                await self.thinking_task
            except asyncio.CancelledError:
                pass
            self.thinking_task = None
            
        if self.printing_task:
            self.printing_task.cancel()
            try:
                await self.printing_task
            except asyncio.CancelledError:
                pass
            self.printing_task = None
        
        # Emergency stop sequence
        stop_commands = [
            "G91",        # Relative positioning
            "G1 Z2",      # Raise Z to 2 after printing
            "G90",        # Back to absolute positioning
            "G92 E0",     # Reset extruder position
            "M84"         # Disable motors
        ]
        
        # Only turn off heat if keep_heat is False
        if not keep_heat:
            stop_commands.extend([
                "M104 S0",  # Turn off extruder
                "M140 S0"   # Turn off bed
            ])
            self.is_heated = False
        
        for cmd in stop_commands:
            await self.send_command(cmd)
        
        self.printing_cancelled = False

    async def start_thinking(self):
        """Move randomly within bounds to simulate thinking"""
        await self.stop_all(keep_heat=True)  # Keep printer heated
        
        if self.thinking_task and not self.thinking_task.done():
            return  # Already thinking
            
        self.thinking_task = asyncio.create_task(self._thinking_loop())

    async def _thinking_loop(self):
        """Background loop for random movement while thinking"""
        try:
            if not self.is_heated:
                await self.heat_up()
                self.is_heated = True

            commands = [
                "G90",                     # Absolute positioning
                "G0 Z2",                   # Move up to safe height
                f"G0 X{self.MAX_X/2} Y{self.MAX_Y/2} F3000",  # Move to center faster
            ]
            await self.send_commands(commands, wait=True)
            
            while True:
                if self.printing_cancelled:
                    break

                # Calculate new random point within safe bounds
                margin = 10  # Safety margin from edges
                next_x = random.uniform(margin, self.MAX_X - margin)
                next_y = random.uniform(margin, self.MAX_Y - margin)

                commands = [
                    f"G1 X{min(next_x, self.MAX_X):.1f} Y{min(next_y, self.MAX_Y):.1f} F1500",
                    "G4 P50"  # Shorter pause of 50ms for smoother movement
                ]
                await self.send_commands(commands, wait=True)
                await asyncio.sleep(0.05)  # Reduced sleep time for smoother movement
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"Error in thinking loop: {e}")
            raise

    async def heat_up(self):
        """Heat up the printer to PLA temperatures"""
        print("Heating up printer...")
        heat_commands = [
            f"M140 S{self.BED_TEMP}",     # Start heating bed
            f"M104 S{self.EXTRUDER_TEMP}", # Start heating extruder
            f"M190 S{self.BED_TEMP}",      # Wait for bed temp
            f"M109 S{self.EXTRUDER_TEMP}", # Wait for extruder temp
        ]
        for cmd in heat_commands:
            await self.send_command(cmd)

class SimulatedPrinter(Printer):
    def __init__(self):
        super().__init__()

    async def connect(self, port='COM16', baudrate=115200, wait=True):
        print("Simulated connection established.")

    async def print_image(self, image_path, scale_factor=0.75):
        print('Simulating image printing...')
        self.print_in_progress = True

        drawing_process = multiprocessing.Process(target=self.draw_contours_on_image, args=(image_path, 'output_image.png', scale_factor))
        drawing_process.start()

        while drawing_process.is_alive():
            await asyncio.sleep(0.1)

        print('Simulated printing complete.')
        self.print_in_progress = False

    def draw_contours_on_image(self, image_path, output_path, scale_factor=0.75, delay=1):
        # Load the image in grayscale and threshold it
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to find or open the image at {image_path}")

        _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a white image
        height, width = image.shape
        output_image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(output_image)

        for contour in contours:
            scaled_contour = contour * scale_factor
            for i in range(len(scaled_contour) - 1):
                start_point = scaled_contour[i][0]
                end_point = scaled_contour[i + 1][0]
                # Convert to integers
                x1, y1 = int(start_point[0]), int(start_point[1])
                x2, y2 = int(end_point[0]), int(end_point[1])
                draw.line((x1, y1, x2, y2), fill="red", width=2)
                output_image.save(output_path)  # Save the image after each line is drawn

                # Convert PIL image to OpenCV format and display
                cv_image = cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)
                cv2.imshow('Drawing', cv_image)
                cv2.waitKey(int(delay))  # Wait for the specified delay in milliseconds

        cv2.destroyAllWindows()
        
class ServerPrinter(Printer):
    def __init__(self, hostname='10.100.102.50', port=12346):
        super().__init__()
        self.server_url = f"http://{hostname}:{port}"
        self.server_ready = False

    async def connect(self, port='COM16', baudrate=115200, wait=True):
        ping_url = f"{self.server_url}/ping"
        try:
            response = await asyncio.to_thread(requests.get, ping_url)
            if response.status_code == 200:
                self.server_ready = True
                print(f"Connected to server at {self.server_url}. Server is ready.")
            else:
                print(f"Failed to connect to server. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error connecting to server: {e}")

    async def send_commands(self, commands: list, wait=True):
        if not self.server_ready:
            try:
                await self.connect()
            except Exception as e:
                print(f"Error connecting to server: {e}")
                return
            
            # Still not ready?
            if not self.server_ready:
                print("Server is not ready. Make sure the server is running.")
                return

        try:
            # Send the commands as a JSON list in the POST request body
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_url}/send_gcode",
                json={'commands': commands}
            )
            if response.status_code == 200:
                print("Sent all commands successfully.")
            else:
                print(f"Failed to send commands. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error sending commands: {e}")

    async def send_command(self, command: str):
        await self.send_commands([command])

    async def print_image(self, image_path, scale_factor=0.75):
        print('Sending image G-code to server...')
        gcode_path = await self.convert_image_to_gcode(image_path, 'temp_image.gcode')

        with open(gcode_path, 'r') as file:
            gcode_commands = file.readlines()

        await self.send_commands(gcode_commands)

    async def graceful_shutdown(self):
        print("Executing graceful shutdown... (no commands sent)")
        