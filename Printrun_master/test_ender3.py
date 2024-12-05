from openai import OpenAI
from playsound import playsound

client = OpenAI()



response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world! This is a streaming test.",
)

# Directly save the response content to a file
with open("speech_file_path.mp3", "wb") as file:
    file.write(response.content)

# Play the saved audio file
playsound("speech_file_path.mp3")
