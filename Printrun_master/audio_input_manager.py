import asyncio
import pyaudio
import wave
import concurrent.futures
import os

class AudioInputManager:
    def __init__(self, host='127.0.0.1', port=8104):
        self.is_button_pressed = False
        self.recording_started = asyncio.Event()
        self.new_input_available = asyncio.Event()
        self.is_recording = False
        self.latest_user_input_path = None
        self.device_name = 'USB 3.0 Dual Video Dock'
        self.host = host
        self.port = port
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    async def run(self):
        """Main loop to monitor button and manage audio recording."""
        print("Starting audio input manager...")
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        print("Server created")
        async with server:
            print("Server started")
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        """Handle incoming connections and update button state."""
        # Log that a connection was established
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

            if self.is_button_pressed and not self.is_recording:
                # Run start_recording in a separate thread
                asyncio.get_running_loop().run_in_executor(self.executor, self.start_recording)

            await asyncio.sleep(0.1)

    def start_recording(self):
        """Start recording audio when the button is pressed."""
        self.is_recording = True
        self.recording_started.set()  # Emit event to stop GPT tasks
        print("Recording started...")

        # Get the current file path
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        file_path = os.path.join(current_directory, "output.wav")
        
        # Audio recording setup
        fs = 44100
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        p1 = pyaudio.PyAudio()

        stream = p1.open(format=sample_format,
                         channels=channels,
                         rate=fs,
                         frames_per_buffer=chunk,
                         input=True)

        frames = []

        # Record while the button is pressed
        stream.start_stream()
        while self.is_button_pressed:
            print("Recording data")
            data = stream.read(chunk)
            print("Recorded", len(data), "samples")
            frames.append(data)
            asyncio.sleep(0.02)  # Allow time for button state updates

        # Stop and close the stream
        print("Stopping stream")
        stream.stop_stream()
        stream.close()
        p1.terminate()

        print("Recording finished.")

        # Save the recorded data as a WAV file
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p1.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Simulate transcription (replace with actual transcription logic)
        self.latest_user_input_path = file_path
        self.is_recording = False
        self.new_input_available.set()  # Emit event for new input availability