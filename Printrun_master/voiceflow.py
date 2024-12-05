import requests
import pygame

# Set up the VOICEFLOW API endpoint and API key
endpoint = "https://general-runtime.voiceflow.com/state/{state_id}/interact"
api_key = "your_api_key_here"

# Set up the TTS block ID
tts_block_id = "your_tts_block_id_here"

# Set up the text that you want to convert to speech
text_to_speak = "Hello, world!"

# Send the text to the TTS block and retrieve the audio file
response = requests.post(endpoint.format(state_id=tts_block_id), headers={"Authorization": api_key}, json={"request": {"type": "text", "payload": {"text": text_to_speak}}})
audio_url = response.json()["response"]["audio"]["url"]
audio_response = requests.get(audio_url)

# Play back the audio file using Pygame
pygame.mixer.init()
pygame.mixer.music.load(audio_response.content)
pygame.mixer.music.play()

# Wait for the audio to finish playing
while pygame.mixer.music.get_busy():
    pygame.time.wait(1000)

