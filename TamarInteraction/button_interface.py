from abc import ABC, abstractmethod
import asyncio
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory

class ButtonInterface(ABC):
    def __init__(self):
        self.is_button_pressed = False

    @abstractmethod
    async def start(self):
        """Start monitoring the button state"""
        pass

    @abstractmethod
    async def stop(self):
        """Stop monitoring the button state"""
        pass

    def get_button_state(self):
        """Return current button state"""
        return self.is_button_pressed 

class SocketButton(ButtonInterface):
    def __init__(self, host='10.100.102.12', port=12345):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None

    async def start(self):
        print("Starting button server")
        self.server = await asyncio.start_server(self._handle_connection, self.host, self.port)
        async with self.server:
            print("Button server started")
            await self.server.serve_forever()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def _handle_connection(self, reader, writer):
        print("Connection established with", writer.get_extra_info('peername'))
        while True:
            data = await reader.read(100)
            message = data.decode().strip()
            
            if message == "button_pressed":
                self.is_button_pressed = True
                print("Button pressed")
            elif message == "button_released":
                self.is_button_pressed = False
                print("Button released")

            await asyncio.sleep(0.1)

class GPIOButton(ButtonInterface):
    def __init__(self, pin=17):
        super().__init__()
        # Create a PiGPIO pin factory
        factory = PiGPIOFactory()
        try:
            self.button = Button(pin, pull_up=True, pin_factory=factory)
            print("GPIO button initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GPIO button: {str(e)}")
        self.running = False

    async def start(self):
        self.running = True
        self.button.when_pressed = self._on_pressed
        self.button.when_released = self._on_released
        # Keep the async task running
        print("Button started")
        while self.running:
            await asyncio.sleep(0.1)

    async def stop(self):
        self.running = False
        self.button.close()

    def _on_pressed(self):
        self.is_button_pressed = True
        print("Button pressed")

    def _on_released(self):
        self.is_button_pressed = False
        print("Button released")