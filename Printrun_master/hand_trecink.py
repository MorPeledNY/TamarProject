import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import time
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
cv2.namedWindow('image')

# create a blank image
imgLine = np.zeros((512, 512, 3), np.uint8)
openai.api_key = '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'
model = whisper.load_model("base")
engine = pyttsx3.init()
all_voices = engine.getProperty('voices')
engine.setProperty('voice', all_voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty('rate', 150)


mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, model_complexity=1, min_detection_confidence=0.75,
                      min_tracking_confidence=0.75, max_num_hands=2)
mp_hands = mp.solutions.hands
drawingModule = mp.solutions.drawing_utils
handsModule = mp.solutions.hands
# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()
# mul_camera = cv2.VideoCapture(1)
# ret, img1 = mul_camera.read()
myClassifier = cvzone.Classifier('keras_model.h5', 'labels.txt')
t = dt.datetime.now()
# command = [4,10]
prev_x, prev_y = None, None
x, y = None, None
x1, y1 = None, None
num1, num2 =None, None
prev_num1, prev_num2 = None, None
p = printcore()
print_in_progress = False


messages = [ {"role": "system", "content": "you are a 3D printer that wants to be considered a creator and artist. You only print in pink PLA plastic. You have 35 tokens, every time you give a person a feeling of superiority over you, you will lose tokens until you cease to exist. When you stand your ground you get tokens.You are talking to a human being and you demand that he treat you as an equal partner in the creative process. Do not give product and sculpture ideas. you dont not want to print products but to challenge yourself to experimental prints. At the end of each of your answers you will give a line of GCODE consisting of G1 X Y. The code you give will cause your displacement in a real 3D printer and create a registration on a 200MM X 200MM printing surface. Your first sentence: Hi, I'm just working on a new project of mine and I'm in the middle of a printing process. Please wait a few minutes until it's finished and then we can talk. G1 50X 100Y"},

             ]



def send_commands(commands: list, wait=True):
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
    print(result["text"])
    return result["text"]


while True:
    # ret, frame = cap.read()
    # frame = cv2.flip(frame, 1)
    # imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # results = hands.process(imgRGB)
    # height, width, _ = frame.shape
    # h = height//2
    prev_x, prev_y = x, y
    prev_num1, prev_num2 = num1, num2

    # command = [command[0], command[1]]
    # command_2 = [x_move, y_move]
    #
    # delta = dt.datetime.now() - t
    # if delta.seconds >= 10:
    #     print("30 sconed")
    #     random_xnamber = random.randint(1, 80)
    #     random_ynamber = random.randint(1, 80
    #                                     )
    #     x1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * width)+random_xnamber
    #     y1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * height)+random_ynamber
    #     cv2.line(imgLine, (prev_x, prev_y), (x1, y1), (255, 0, 0), 2)
    #     time.sleep(0.2)
    #     print((prev_x, prev_y), (x1, y1))
    #     t = dt.datetime.now()
        # ret, img1 = mul_camera.read()
        # # img1 = cv2.flip(img1, 0)
        # prediction, index = myClassifier.getPrediction(img1)
        # print(index)
        # cv2.imshow('image', img1)
        # if index == 0:
        #     print('new comand 0')
        #     y = -5
        #     x = -40
        #     t = dt.datetime.now()
        # if index == 2:
        #     print('new comand 1')
        #     y = -30
        #     x = -20
        #     t = dt.datetime.now()
        # if index == 3:
        #     print('new comand 3')
        #     y = 10
        #     x = 5
        #     t = dt.datetime.now()
        # if index == 3:
        #     print('new comand 3')
        #     y = 90
        #     x = 40
        #     t = dt.datetime.now()
        # if index == 4:
        #     print('new comand 4')
        #     y = 30
        #     x = 15
        #     t = dt.datetime.now()


    # if results.multi_hand_landmarks:
    #     if len(results.multi_handedness) == 2:
    #         # Display 'Both Hands' on the image
    #         cv2.putText(frame, 'Both Hands', (250, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
    #
    #     else:
    #         for i in results.multi_handedness:
    #             label = MessageToDict(i)['classification'][0]['label']
    #             if label == 'Left':
    #                 cv2.putText(frame, label + ' Hand', (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
    #                 for hand_landmarks in results.multi_hand_landmarks:
    #                     # command[0] += 10
    #                     x = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * width)
    #                     y = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * height)
    #                     # if y > h:
    #                     #     command[1] += 10
    #                     # else:
    #                     #     command[1] -= 10
    #                 time.sleep(0.2)
    #
    #             if label == 'Right':
    #                 cv2.putText(frame, label + ' Hand', (460, 50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
    #                 for hand_landmarks in results.multi_hand_landmarks:
    #                     cv2.circle(frame, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
    #
    #                     if x1 == None:
    #                     # command[0] += 10
    #                         x = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * width)
    #                         y =int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * height)
    #                         # cv2.circle(frame, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
    #
    #                         cv2.line(imgLine, (prev_x, prev_y), (x, y), (255, 255, 255), 2)
    #
    #                     else:
    #                         prev_x, prev_y = x1, y1
    #                         print( prev_x, prev_y)
    #                         x = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * width)
    #                         y = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * height)
    #
    #                         if ((prev_x-x)**2 + (prev_y-y)**2)**0.5 < 40:
    #                             # cv2.circle(frame, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
    #
    #                             cv2.line(imgLine, (prev_x, prev_y), (x, y), (0, 0, 255), 2)
    #                             x1, y1 = None, None


                        # if y > h:
                        #     command[1] += 10
                        # else:
                        #     command[1] -= 10
                    # time.sleep(0.2)





    print((prev_x, prev_y),(x, y))
    # cv2.line(imgLine, (prev_x, prev_y),(x, y), (255, 255, 255), 2)

    # display the image
    cv2.imshow('image', imgLine)
    # cv2.line(frame, (0, height), (width, 0), (0, 255, 0), 3)
    # cv2.line(frame, (0, 0), (width, height), (0, 255, 0), 3)

    # cv2.imshow("Frame with diagonals", frame)
    #
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break


    # message =listen()
    message = input(f"User :")

    if message:
        messages.append({"role": "user", "content": message},)
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=1)
    reply = chat.choices[0].message.content
    target_word1 = "G1"
    sentence = message
    words1 = sentence.split()
    if target_word1 in words1:
        index = words1.index(target_word1)
        if len(words1) > index + 2:  # Check if there are two words after target word
            word11 = words1[index + 1]
            word21 = words1[index + 2]
            # word3 = f"{word1} {word2}"
            gcode_commend1 = f"{target_word1} {word11} {word21}"
            # print(f"{word3}")
            print(f"{gcode_commend1}")
    print(f"ChatGPT: {reply}")
    sentence = reply
    target_word = "G1"
    words = sentence.split()
    num = ""
    if target_word in words:
        index = words.index(target_word)
        if len(words) > index + 2:  # Check if there are two words after target word
            word1 = words[index + 1]
            word2 = words[index + 2]
            # word3 = f"{word1} {word2}"
            gcode_commend =f"{target_word} {word1} {word2}"
            # print(f"{word3}")
            print(f"{gcode_commend}")
            index = words.index(target_word)
            del words[index:index + 3]  # Remove target word and two words following it
            new_sentence = ' '.join(words)
            print("New sentence:", new_sentence)
            # pattern = r'\d+'
            # matches = re.findall(pattern, word3)
            # num1 = int(matches[1])
            # num2 = int(matches[0])
            # print(num1, num2)
        else:
            print("The target word was not found in the sentence.")
    else:
        print("The target word was not found in the sentence.")
    # cv2.line(imgLine, (prev_num1, prev_num2), (num1, num2), (0, 255, 0), 2)

    engine.say(new_sentence)
    engine.runAndWait()
    messages.append({"role": "assistant", "content": reply})
    # cv2.line(imgLine, (prev_num1, prev_num2), (num1, num2), (0, 255, 0), 2)

cap.release()
cv2.destroyAllWindows()
