import pyaudio
import wave
import os
from pydub import AudioSegment
import simpleaudio as sa

def test_recording(duration_seconds=5):
    # Audio recording parameters
    fs = 44100  # Sample rate
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16
    channels = 1
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Get the current file path for saving
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "test_output.wav")
    
    print(f"Recording for {duration_seconds} seconds...")
    
    # Open stream
    stream = p.open(format=sample_format,
                   channels=channels,
                   rate=fs,
                   frames_per_buffer=chunk,
                   input=True)
    
    frames = []  # Array to store frames
    
    # Record for the specified duration
    for i in range(0, int(fs / chunk * duration_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("Recording finished!")
    
    # Save the recorded data as a WAV file
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"Recording saved to: {file_path}")

def play_recording(file_path):
    print(f"Playing recording from: {file_path}")
    audio = AudioSegment.from_wav(file_path)
    
    # Play the audio using simpleaudio
    playback = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )
    
    # Wait until playback is finished
    playback.wait_done()
    print("Playback finished!")

if __name__ == "__main__":
    # Record audio
    test_recording()
    
    # Play the recorded audio
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "test_output.wav")
    play_recording(file_path) 