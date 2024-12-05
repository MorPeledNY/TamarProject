import asyncio
from printrun.printcore import printcore
from printrun import gcoder
import cv2

class Printer:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, port='COM16', baudrate=115200, wait=True):
        if not hasattr(self, 'printer'):
            self.printer = printcore()
            self.print_in_progress = False
            asyncio.create_task(self.connect(port, baudrate, wait))
    
    async def connect(self, port, baudrate, wait=True):
        await asyncio.to_thread(self.printer.connect, port, baudrate, wait)
        self.printer.startcb = self._start_callback
        self.printer.endcb = self._end_callback
        print("Connecting...")
    
    def _start_callback(self, *args):
        self.print_in_progress = True
        
    def _end_callback(self, *args):
        self.print_in_progress = False
    
    async def send_commands(self, commands: list, wait=True):
        """Send multiple G-code commands to the printer"""
        commands_gcode = gcoder.LightGCode(commands)
        await asyncio.to_thread(self.printer.startprint, commands_gcode)
        await asyncio.sleep(0.5)
        if wait:
            while self.print_in_progress:
                await asyncio.sleep(0.01)
    
    async def send_command(self, command: str):
        """Send a single G-code command"""
        await self.send_commands([command])
    
    async def graceful_shutdown(self):
        """Gracefully shutdown the printer with proper sequence"""
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
    
    async def convert_image_to_gcode(self, image_path, output_gcode_path, scale_factor=0.75):
        """Convert an image to G-code and save it to a file."""
        print('Start converting image to G-code')

        # Load the image in grayscale and threshold it
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to find or open the image at {image_path}")

        _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        gcode = []

        for contour in contours:
            # Scale the contour points
            scaled_contour = contour * scale_factor

            # Move to the starting point of the contour
            start_point = scaled_contour[0][0]
            gcode.append(f"G0 X{start_point[0]} Y{start_point[1]}")

            # Generate G1 commands to follow the contour
            for point in scaled_contour:
                x, y = point[0]
                gcode.append(f"G1 X{x} Y{y}")

        # Save the G-code to a file
        with open(output_gcode_path, 'w') as file:
            for line in gcode:
                file.write(line + '\n')

        print('Saved new G-code to file:', output_gcode_path)
        return output_gcode_path
        
    async def print_image(self, image_path):
        """Print an image on the printer"""
        # Convert the image to G-code
        gcode_path = await self.convert_image_to_gcode(image_path, 'temp_image.gcode')
        
        # Load the gcode file
        with open(gcode_path, 'r') as file:
            gcode_commands = file.readlines()
            
        # Send the gcode commands to the printer
        await self.send_commands(gcode_commands)

class SimulatedPrinter:
    def __init__(self):
        self.print_in_progress = False

    async def connect(self, port='COM16', baudrate=115200, wait=True):
        """Simulate connecting to a printer."""
        print("Simulated connection established.")

    async def print_image(self, image_path, scale_factor=0.75):
        """Simulate printing an image by painting contours."""
        print('Simulating image printing...')
        self.print_in_progress = True

        # Load the image in grayscale and threshold it
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to find or open the image at {image_path}")

        _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Simulate the time taken to print each contour
        for contour in contours:
            # Scale the contour points
            scaled_contour = contour * scale_factor

            # Simulate moving to the starting point of the contour
            start_point = scaled_contour[0][0]
            print(f"Simulated move to X{start_point[0]} Y{start_point[1]}")

            # Simulate generating G1 commands to follow the contour
            for point in scaled_contour:
                x, y = point[0]
                print(f"Simulated printing at X{x} Y{y}")
                await asyncio.sleep(0.01)  # Simulate time delay for printing

        print('Simulated printing complete.')
        self.print_in_progress = False