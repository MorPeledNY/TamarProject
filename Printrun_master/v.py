import whisper
import speech_recognition as sr
import pyttsx3
import numpy as np
import text2emotion as te


import pyaudio
import wave

def mic_record():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 5
    filename = "output.wav"



    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

# Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

# Stop and close the stream
    stream.stop_stream()
    stream.close()
# Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

# Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


engine = pyttsx3.init()

# playsound('welcom.mp3')
all_voices = engine.getProperty('voices')
engine.setProperty('voice', all_voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 100)
engine.say('Welcome Mor  ... how do you feel today?')
engine.runAndWait()

mic_record()

model = whisper.load_model("base")
result = model.transcribe('output.wav', fp16=False)
print(result['text'])

text1 = result['text']
print(te.get_emotion(text1))

emoshion_d = te.get_emotion(text1)
print(emoshion_d)

namber_max_value = max(emoshion_d.values())
print(namber_max_value)

if namber_max_value != 0:

    max_valeu= max(emoshion_d, key=emoshion_d.get)
    print(max_valeu)

    if max_valeu == 'Happy':
        print(1)
    else:
        print(0)

else:
    print('natural')



#model = whisper.load_model("base")
#result = model.transcribe(vo, fp16=False)
#print(result["text"])