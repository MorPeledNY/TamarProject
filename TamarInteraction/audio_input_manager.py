import asyncio
import pyaudio
import wave
import concurrent.futures
import os
from button_interface import ButtonInterface, SocketButton, GPIOButton

class AudioInputManager:
    def __init__(self):
        self.button = GPIOButton()
        self.recording_started = asyncio.Event()
        self.new_input_available = asyncio.Event()
        self.is_recording = False
        self.latest_user_input_path = None
        self.device_name = 'USB 3.0 Dual Video Dock'
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    async def run(self):
        """Main loop to monitor button and manage audio recording."""
        print("Starting audio input manager...")
        asyncio.get_running_loop().run_in_executor(self.executor, lambda: asyncio.run(self.button.start()))
        while True:
            if self.button.get_button_state() and not self.is_recording:
                print(self.button.get_button_state())
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
        print("Recording data")
        while self.button.get_button_state():
            data = stream.read(chunk)
            frames.append(data)
            asyncio.sleep(0.02)  # Allow time for button state updates

        # Stop and close the stream
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
        print('New input available:', self.latest_user_input_path)