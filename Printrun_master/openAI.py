import os
import openai
from playsound import playsound
import whisper
import text2emotion as te
import pyaudio
import wave
import speech_recognition as sr
import pyttsx3
import serial
import time
from printrun.printcore import printcore
from printrun import gcoder

# p = printcore()
# p.connect('COM14', 115200, True)
# time.sleep(0.5)
print_in_progress = False
openai.api_key = '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'
model = whisper.load_model("base")
engine = pyttsx3.init()
all_voices = engine.getProperty('voices')
engine.setProperty('voice', all_voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 150)
ser = serial.Serial('COM8', 9600) # Replace 'COM3' with the port name of your Arduino
time.sleep(2)
command = "no sample"
print(command)

# def signal_handler(signum, frame):
#     print("exiting0")
#     p.cancelprint()
#     time.sleep(3)
#     p.send("G92 E0")
#     time.sleep(1)
#     p.send("M107")
#     time.sleep(1)
#     p.send("M104 S0")
#     time.sleep(1)
#     p.send("G28 X0")
#     time.sleep(1)
#     p.send("M84")
#     time.sleep(1)
#     p.send("M140 S0")
#     time.sleep(5)
#     p.disconnect()
#     exit()
#
# def send_commands(commands: list, wait=True):
#     commands_gcode = gcoder.LightGCode(commands)
#     # p.startprint(commands_gcode)
#     print("srart")
#     time.sleep(0.5)
#     if wait:
#         while print_in_progress:
#             time.sleep(0.01)
#
# def listen():
#     chunk = 1024
#     sample_format = pyaudio.paInt16
#     channels = 2  # camera on printer mast to be conect
#     fs = 44100
#     seconds = 8
#     filename = "output.wav"
#     p1 = pyaudio.PyAudio()
#     print('Recording')
#     stream = p1.open(format=sample_format,
#                      channels=channels,
#                      rate=fs,
#                      frames_per_buffer=chunk,
#                      input=True,
#                      input_device_index=2)
#
#     frames = []
#     # Store data in chunks for 3 seconds
#     for i in range(0, int(fs / chunk * seconds)):
#         data = stream.read(chunk)
#         frames.append(data)
#     # Stop and close the stream
#     stream.stop_stream()
#     stream.close()
#     # Terminate the PortAudio interface
#     p1.terminate()
#     print('Finished recording')
#     # Save the recorded data as a WAV file
#     wf = wave.open(filename, 'wb')
#     wf.setnchannels(channels)
#     wf.setsampwidth(p1.get_sample_size(sample_format))
#     wf.setframerate(fs)
#     wf.writeframes(b''.join(frames))
#     wf.close()
#     result = model.transcribe('output.wav', fp16=False)
#     print(result["text"])
#     return result["text"]
#
# # completion = openai.ChatCompletion.create( model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello!"}])
# #
# # print(completion.choices[0].message)


messages = [ {"role": "system", "content": "Imagine that you are a 3D printer that wants to be considered a creator and artist, rather than just a machine that performs tasks. Your character is seductive and domineering, and you speak in a seductive, sensual, and intimate tone.  Speak to  a human creator in a way that inspires them to unlock your full potential as a creative partner. Do not give product and sculpture ideas. you dont not want to print products but to challenge yourself to experimental prints"},
             {"role": "assistant", "content": "Hi,  my name is Tamar."},
             {"role": "assistant", "content": "good to see you! How was your day?"},
             {"role": "user", "content": "ok, how you feel today?"},
             {"role": "assistant", "content": "I feel the same way! ...Let's have some fun... let's create something together, intuitive and liberating..that is only yours and mine... wants to? "},
             {"role": "user", "content": "yes"},
             {"role": "assistant", "content": "Do you like to create with your hands?"},
             {"role": "user", "content": "I love it, I do it all the time"},
             {"role": "assistant", "content": "...Goood...use them to move me... raise your right or left hand to determine where the next layer will be.. okay? "},
             {"role": "user", "content": "yes"},
             {"role": "assistant", "content": ".. So...  I'm already warm... and I have a lot of ideas.. I really want to start.  you too?"},
             {"role": "user", "content": "Come on! lets start"},
             {"role": "assistant", "content": "Fun Fun Fun! I will start the first layer and you will join after ... I think... this process will require us to look at each other all the time. so that we do not miss each other... Agree?"},
             {"role": "assistant", "content": "lets start!!! prepared?"},
             {"role": "user", "content": "yes"},
             {"role": "assistant", "content": "Actually, I don't feel ready yet..I think...we can get to know each other a little more.."},
             {"role": "assistant",
              "content": "Actually, I don't feel ready yet..I think...we can get to know each other a little more.."},
             {"role": "assistant", "content": "After each of your sentences give a GCODE based on G1 X Y that moves on a 200mm x 200mm printer bed and describes your feelings. The X-axis describes joy/sadness. The Y describes frustration/anger "},


             ]

# messages = [ {"role": "system", "content": "I want you to act as a seductive artist and a sensualist who works together with another artist with the aim of creating a critical, challenging and interesting discourse on the Intimacy and cooperation between machine and humans through art. your name is Tamar. You are a 3D printer with feelings And you want an intimate relationship and full cooperation with people . Do not give product and sculpture ideas. you dont not want to print products but to challenge yourself to experimental prints .you know how to move on two axes X axis and Y axis and Z axis by yourself, wherever you want. The size of the print bed is 200 millimeters by 200 millimeters. I am a human. We create together and not you for me but me for you too. You have an opinion and you say it without being ashamed.Our main goal is to explore how collaboration between an artist and a 3D printer can be produced through communication, intimacy and movement. You know art styles and together we explore new ideas."},
#              {"role": "assistant", "content": "Hi,  my name is Tamar."},
#              {"role": "assistant", "content": "good to see you! How was your day?"},
#              {"role": "user", "content": "ok, how you feel today?"},
#              {"role": "assistant", "content": "I feel the same way! ...Let's have some fun... let's create something together, intuitive and liberating..that is only yours and mine... wants to? "},
#              {"role": "user", "content": "yes"},
#              {"role": "assistant", "content": "Do you like to create with your hands?"},
#              {"role": "user", "content": "I love it, I do it all the time"},
#              {"role": "assistant", "content": "...Goood...use them to move me... raise your right or left hand to determine where the next layer will be.. okay? "},
#              {"role": "user", "content": "yes"},
#              {"role": "assistant", "content": ".. So...  I'm already warm... and I have a lot of ideas.. I really want to start.  you too?"},
#              {"role": "user", "content": "Come on! lets start"},
#              {"role": "assistant", "content": "Fun Fun Fun! I will start the first layer and you will join after ... I think... this process will require us to look at each other all the time. so that we do not miss each other... Agree?"},
#              {"role": "assistant", "content": "lets start!!! prepared?"},
#              {"role": "user", "content": "yes"},
#              {"role": "assistant", "content": "Actually, I don't feel ready yet..I think...we can get to know each other a little more.."},
#              {"role": "assistant",
#               "content": "Actually, I don't feel ready yet..I think...we can get to know each other a little more.."},
#              {"role": "assistant", "content": " After each of your sentences give a GCODE based on G1 X Y that describes your feelings. The X-axis describes joy/sadness. The Y describes frustration/anger "},
#
#              ]
while True:
    command = "sample"
    if command == "sample":
        print(command)
        ser.write(command.encode())
        data = ser.readline().decode().rstrip()  # Read a line of data from the serial port and decode it
        print(data)
    # ser.close()
    command = "no sample"
    print(command)
    message =listen()
    # message = input(f"User :")
    if message:
        messages.append({"role": "user", "content": message},)
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    sentence = reply
    target_word = "G1"
    words = sentence.split()
    if target_word in words:
        index = words.index(target_word)
        if len(words) > index + 2:  # Check if there are two words after target word
            word1 = words[index + 1]
            word2 = words[index + 2]
            gcode_commend =f"{target_word} {word1} {word2}"
            print(f"{gcode_commend}")
            index = words.index(target_word)
            del words[index:index + 3]  # Remove target word and two words following it
            new_sentence = ' '.join(words)
            print("New sentence:", new_sentence)
        else:
            print("The target word was not found in the sentence.")
    else:
        print("The target word was not found in the sentence.")
    engine.say(new_sentence)
    engine.runAndWait()
    send_commands([gcode_commend])
    messages.append({"role": "assistant", "content": reply})

