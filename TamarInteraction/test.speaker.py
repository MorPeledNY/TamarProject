from pydub import AudioSegment
import simpleaudio as sa

# Load the MP3 file
audio = AudioSegment.from_mp3('TamarInteraction/used_files/haha.mp3')

# Play the audio using simpleaudio
playback = sa.play_buffer(
    audio.raw_data,
    num_channels=audio.channels,
    bytes_per_sample=audio.sample_width,
    sample_rate=audio.frame_rate
)

# Wait until playback is finished
playback.wait_done()
