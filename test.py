import pyaudio

# Initialize PyAudio
p = pyaudio.PyAudio()

# List all audio devices
print("Available audio devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# Parameters for the stream
sample_format = pyaudio.paInt16  # Sample format
channels = 1  # Mono or stereo channels (1 for mono, 2 for stereo)
rate = 44100  # Sampling rate
frames_per_buffer = 1024  # Buffer size

# Try opening the stream with a specific device
device_index = int(input("\nEnter the device index you want to use for input: "))

try:
    print("Opening stream...")
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=rate,
                    frames_per_buffer=frames_per_buffer,
                    input=True,
                    input_device_index=device_index)

    print("Stream opened successfully!")
    # Close the stream after use
    stream.stop_stream()
    stream.close()

except OSError as e:
    print(f"Failed to open stream: {e}")

finally:
    p.terminate()
