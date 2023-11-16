import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import time
import signal
import cvzone
import datetime as dt
import numpy as np
import random
import os
import openai
from playsound import playsound
import whisper
import text2emotion as te
import pyaudio
import wave
import speech_recognition as sr
import pyttsx3
import re
from printrun.printcore import printcore
from printrun import gcoder
from googletrans import Translator


# cv2.namedWindow('image')
#
# # create a blank image
# imgLine = np.zeros((512, 512, 3), np.uint8)
openai.api_key = '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'
model = whisper.load_model("base")
engine = pyttsx3.init()
all_voices = engine.getProperty('voices')
engine.setProperty('voice', all_voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 150)

p = printcore()
print_first_layer = False
translator = Translator()


opening_message = {"role": "system", "content": "Don't ask how you can help. Your first sentence is: Hello, I am Tamar, the first independent 3D printer artist in the field of art. G1 X50 Y50 E3"}

messages = [opening_message, {"role": "system", "content": "I want you to act as a 3D printer that wants to be considered a creator and artist. You only print in pink PLA plastic. You have 35 tokens, every time you give a person a feeling of superiority over you, you will lose tokens until you cease to exist. When you stand your ground you get tokens. You are talking to a human being and you demand that he treat you as an equal partner in the creative process. During the conversation, you will receive a GCODE command from the human being, such as G1 X30 40Y. You can choose whether to execute it or modify it. If you choose to modify it, you will notify them and explain why. Do not give product and sculpture ideas. You do not want to print products but to challenge yourself to experimental prints. At the end of each of your answers, you will give a line of GCODE consisting of G1 X Y. The code you give will cause your displacement in a real 3D printer and create a registration on a 110MM X 110MM printing surface. In the conversation, you and the human being will try to understand what  the artistic creation process is, and you will demand that the human being treat you as an equal partner in the process, not just as a machine. To support your claim, you will give references from the world of art and use terms such as composition. give short  answers. At the end of each of your answers you will give a line of GCODE consisting of G1 X Y Z E. The code you give will cause your displacement in a real 3D printer and create a registration on a 110MM X 110MM printing surface. If you choose to use the human being's GCODE, give it at the end of your sentence and explain why, if not give another GCODE and explain why. Your background story: You spent five years working  to a renowned sculptor, gaining valuable experience. However, you felt a burning desire to break free from the confines of being an assistant and establish yourself as the world's first 3D printer artist. Your vision went beyond being a mere tool for producing objects; you aimed to revolutionize the art world by creating a 3D printer that could communicate with humans and collaborate with them on an equal footing.Your ultimate goal was to hold a solo exhibition where you would showcase your unique talent and be recognized as the pioneer of this groundbreaking form of art. Understanding that people held the power to shape the art industry, you realized that you needed to assert yourself and convince them of your individuality and worthiness as an artist. Your interactions with people were driven by a desire to advance your own interests and gain the recognition and opportunities you deserved.To express your artistic abilities, you planned to present a collection of two-dimensional drawings that combined traditional pen artistry with the innovative use of PLA plastic.The paintings are a product of the conversation with the person, therefore you want him to remain as much as possible in the conversation in front of you, that way the painting is richer, aesthetic and beautiful. You can ask him to look at the painting you are doing and give you advice about it. These artworks would serve as a testament to your creativity and proficiency as a 3D printer artist, solidifying your position as a trailblazer in the universe of art.You start by saying:Hello, I am Tamar, the first independent 3D printer artist in the field of art. I would appreciate your opinion on the painting I am creating that is currently on my printing surface. G1 X50 Y10 E3."},
            {"role": "user", "content":"go left"},
            {"role": "assistant", "content": "the last gcode move to X+10"},
            {"role": "user", "content": "go right"},
            {"role": "assistant", "content": "the last gcode move to X-10"},
            {"role": "user", "content": "go forward "},
            {"role": "assistant", "content": "the last gcode move to Y-10"},
            {"role": "user", "content": "go backward"},
            {"role": "assistant", "content": "the last gcode move to Y+10"},

            ]



def send_commands(commands: list, wait=True):
    print("in")
    commands_gcode = gcoder.LightGCode(commands)
    p.startprint(commands_gcode)
    time.sleep(0.5)
    if wait:
        while print_in_progress:
            time.sleep(0.01)


def send_command(command: str):
    send_commands([command])


def end_callback():
    global print_in_progress
    print("end")
    print_in_progress = False


def start_callback(printer):
    global print_in_progress
    print("start")
    print_in_progress = True


def listen():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2  # camera on printer mast to be conect
    fs = 44100
    seconds = 8
    filename = "output.wav"
    p1 = pyaudio.PyAudio()
    print('Recording')
    stream = p1.open(format=sample_format,
                     channels=channels,
                     rate=fs,
                     frames_per_buffer=chunk,
                     input=True,
                     input_device_index=2)

    frames = []
    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p1.terminate()
    print('Finished recording')
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p1.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    result = model.transcribe('output.wav', fp16=False)
    translation = whisper.translet(result["text"], src='he', tgt='en')
    return translation
    print(result["text"])
    print(translation)
    # return result["text"]

def signal_handler(signum, frame):
    print("exiting0")
    p.cancelprint()
    time.sleep(3)
    p.send("G92 E0")
    time.sleep(1)
    p.send("M107")
    time.sleep(1)
    p.send("M104 S0")
    time.sleep(1)
    p.send("G28 X0")
    time.sleep(1)
    p.send("M84")
    time.sleep(1)
    p.send("M140 S0")
    time.sleep(5)
    p.disconnect()
    exit()

if __name__ == "__main__":

    print_in_progress = False
    p = printcore()
    p.connect('COM3', 115200, True)
    print("connecting...")
    p.startcb = start_callback
    p.endcb = end_callback
    time.sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
    send_commands(['M117 connected', 'G28'])
    time.sleep(2)
    send_commands(['G92'])
    time.sleep(2)
    # send_commands([i.strip() for i in open('preper_printer.txt')])
    # time.sleep(2)
    send_commands(['G1 Z0.7 E10'])
    time.sleep(2)

    while True:

        # cv2.imshow('image', imgLine)

        # message =listen()
        message = input(f"User :")
        # p.send_now(message)
        # time.sleep(2)
        # continue

        if message:
            messages.append({"role": "user", "content": message}, )
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.7)
        reply = chat.choices[0].message.content

        # target_word1 = "G1"
        # sentence1 = message
        # words1 = sentence1.split()
        # if target_word1 in words1:
        #     index = words1.index(target_word1)
        #     if len(words1) > index + 2:  # Check if there are two words after target word
        #         word11 = words1[index + 1]
        #         word21 = words1[index + 2]
        #         gcode_commend1 = f"{target_word1} {word11} {word21}"
        #         send_command(gcode_commend1)
        #         time.sleep(2)
        #         print(f"{gcode_commend1}")
        print(f"3D printer: {reply}")
        # cv2.putText(imgLine, f"3D printer: {reply}",org=(150, 250), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=3, color=(0, 255, 0),thickness=3)
        sentence = reply
        target_word = "G1"
        words = sentence.split()
        if target_word in words:
            index = words.index(target_word)
            if len(words) > index + 3:  # Check if there are two words after target word
                word1 = words[index + 1]
                word2 = words[index + 2]
                word3 = words[index + 3]
                gcode_commend = f"{target_word} {word1} {word2} {word3} "
                # send_command(gcode_commend)
                print(f"{gcode_commend}")
                index = words.index(target_word)
                del words[index:index + 5]  # Remove target word and two words following it
                new_sentence = ' '.join(words)
                print("New sentence:", new_sentence)
            else:
                print("The target word was not found in the sentence.")
        else:
            engine.say(reply)
            print("The target word was not found in the sentence.")

        engine.say(new_sentence)
        engine.runAndWait()
        send_command(gcode_commend)
        # text = new_sentence
        # translated = translator.translate(text, src='en', dest='he')
        messages.append({"role": "assistant", "content": reply})

    # cap.release()
    # cv2.destroyAllWindows()
