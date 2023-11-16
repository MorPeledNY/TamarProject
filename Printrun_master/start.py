import subprocess
from printrun.printcore import printcore
from printrun import gcoder
import time
import signal
import cv2
import numpy as np
import subprocess
import os
import speech_recognition as sr
import pyttsx3
from playsound import playsound
import whisper
import speech_recognition as sr
import pyttsx3
import numpy as np
import text2emotion as te
import pyaudio
import wave
import serial
import time

# model = whisper.load_model("base")
# ser = serial.Serial('COM8', 9600) # Replace 'COM3' with the port name of your Arduino
# time.sleep(5)
# result_text = ""  # Define the result_text variable outside the if condition
#
# command = "sample"
# data = ser.readline().decode().rstrip()  # Read a line of data from the serial port and decode it
# print(data)
# data1 = 0
# Close serial connection

# #
# def listen():
#     # global data1
#     ser.write(command.encode())
#     data1 = int(ser.readline().decode().rstrip())
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
#     # for i in range(0, int(fs / chunk * seconds)):
#     while data1 > 0:  # Continue recording while data1 is greater than 0
#         print(data1)
#         data = stream.read(chunk)
#         frames.append(data)
#         ser.write(command.encode())
#         data1 = int(ser.readline().decode().rstrip())
# # Stop and close the stream
#     print('Finished recording')
#     stream.stop_stream()
#     stream.close()
#     p1.terminate()
# # Save the recorded data as a WAV file
#     wf = wave.open(filename, 'wb')
#     wf.setnchannels(channels)
#     wf.setsampwidth(p1.get_sample_size(sample_format))
#     wf.setframerate(fs)
#     wf.writeframes(b''.join(frames))
#     wf.close()
#     result = model.transcribe('output.wav', fp16=False)
#     # translation = whisper.translet(result["text"], src='he', tgt='en')
#     # return translation
#     print(result["text"])
#     # print(translation)
#     return result["text"]

while True:
    # if command == 'sample':
    #     ser.write(command.encode())
    #     data1 = int(ser.readline().decode().rstrip() )# Read a line of data from the serial port and decode it
    #     print(data1)
    #     if data1 >20:
    #         result_text=listen()
    #
    # if result_text:
    #     print(result_text)




    # ser.close()

p = printcore()


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


# def mic_record():
#     chunk = 1024
#     sample_format = pyaudio.paInt16
#     channels = 2  # camera on printer mast to be conect
#     fs = 44100
#     seconds = 5
#     filename = "output.wav"
#     p1 = pyaudio.PyAudio()
#     print('Recording')
#     p.send_now("M117 lisening")
#     time.sleep(0.5)
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
#     p.send_now("M117 stop lisening")
# # Save the recorded data as a WAV file
#     wf = wave.open(filename, 'wb')
#     wf.setnchannels(channels)
#     wf.setsampwidth(p1.get_sample_size(sample_format))
#     wf.setframerate(fs)
#     wf.writeframes(b''.join(frames))
#     wf.close()
#
#
if __name__ in "__main__":

    engine = pyttsx3.init()
    # playsound('welcom.mp3')
    all_voices = engine.getProperty('voices')
    engine.setProperty('voice', all_voices[1].id)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 100)
    signal.signal(signal.SIGINT, signal_handler)

    p.connect('COM14', 115200, True)
    time.sleep(5)

    while True:
        input_answer= input('gcoge:')
        p.send_now(input_answer)
#


#     p.send_now("M117 connected")
#     print("connected")
#     time.sleep(0.5)
#     p.send_now("G28")
#     time.sleep(1)
#     p.send_now("M117 WELCOME")
#     engine.say('Welcome Mor  ... how do you feel today?')
#     engine.runAndWait()
#     time.sleep(1)
#     p.send_now("G0 X100")
#     mic_record()
#     model = whisper.load_model("base")
#     result = model.transcribe('output.wav', fp16=False)
#     print(result['text'])
#     text1 = result['text']
#     print(te.get_emotion(text1))
#     # creat gcode from stl file
#     #  subprocess.call([r'D:\\Slic3r-1.3.0.64bit\\Slic3r-console.exe', 'D:\\Slic3r-1.3.0.64bit\\body2.stl', '--load',
#     #                  'D:\\Slic3r-1.3.0.64bit\\config.ini', '--output',
#     #                  'C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\test.gcode'])
#
#     engine.say(" minutes.")
#     engine.runAndWait()
#
#     #conect to printer+ send the gcode
#
#     # gcode = [i.strip() for i in open('test.gcode')]
#     # gcode = gcoder.LightGCode(gcode)
#
#
#     # startprint silently exits if not connected yet
#     # while not p.online:
#     #     time.sleep(0.1)
#     #     print("wiating")
#
#     # p.startprint(gcode)  # this will start a print
#     engine.say(" you?")
#     engine.runAndWait()
#
#
#     engine.say("Thanks, now I'm starting to warm up")
#     engine.runAndWait()

# input_a = "n"
#
#
# input_a = input("sand a gcood:")
#
# printer_moving = p.send_now(input_a)

# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#
# while 1:
#     ret, img = cap.read()
#     img = cv2.flip(img, 1)
#
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     # if len(faces) > 0:
#     #     if not is_print:
#     #         state_count += 1
#     #         if state_count > 5:
#     #             is_print = not is_print
#     #             p.resume()
#     #             print("found eyes. continue")
#     #     else:
#     #         state_count = 0
#     # else:
#     #     if is_print:
#     #         state_count += 1
#     #         if state_count > 5:
#     #             is_print = not is_print
#     #             p.pause()
#     #             print("eyes just disappeared")
#     #             # talk to the printer
#     #
#     #
#     #
#     #     else:
#     #         state_count = 0
#
#     for (x, y, w, h) in faces:
#         x1 = x
#         y1 = y
#         x2 = x + w
#         y2 = y + h
#         center_x = int((x1 + x2) / 2)
#         center_y = int((y1 + y2) / 2)
#         middle_x = int(gray.shape[1] / 2)
#         middle_y = int(gray.shape[0] / 2)
#         distance_x = center_x - middle_x
#         distance_y = center_y - middle_y
#
#         cv2.rectangle(img, (x1, y1), (x2 , y2 ), (255, 0, 0), 2)
#         cv2.line(img, (center_x, center_y), (middle_x, middle_y), (0, 255, 0), 2)
#
#         roi_gray = gray[y:y + h, x:x + w]
#         roi_color = img[y:y + h, x:x + w]
#
#         eyes = eye_cascade.detectMultiScale(roi_gray)
#
#         for (ex, ey, ew, eh) in eyes:
#             cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
#
#         if center_x > middle_x:
#             cv2.putText(img, 'Right', (x2, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#             print('Right', center_x, center_y)
#         else:
#             cv2.putText(img, 'Left', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#             print('Left', center_x, center_y)
#
#
#
#     cv2.imshow('img', img)
#     k = cv2.waitKey(30) & 0xff
#     if k == 27:
#         break
#
# cap.release()
# cv2.destroyAllWindows()
# import cv2
#
# # Load the pre-trained face and hand classifiers
# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# hand_cascade = cv2.CascadeClassifier('hand_cascade.xml')
#
# # Open the camera and set the resolution
# cap = cv2.VideoCapture(0)
# cap.set(3, 640)
# cap.set(4, 480)
#
# while True:
#     # Read a frame from the camera
#     ret, frame = cap.read()
#
#     # Convert the frame to grayscale
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Detect faces in the grayscale image
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#
#     # Calculate the center of the image
#     center_x = int(frame.shape[1] / 2)
#
#     for (x, y, w, h) in faces:
#         # Draw a rectangle around the face
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#
#         # Calculate the position of the face in relation to the center of the image
#         face_center_x = x + w/2
#         if face_center_x < center_x:
#             print("Face is on the left side")
#         else:
#             print("Face is on the right side")
#
#         # Detect hands in the grayscale image
#         roi_gray = gray[y:y+h, x:x+w]
#         hands = hand_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#
#         for (hx, hy, hw, hh) in hands:
#             # Draw a rectangle around the hand
#             cv2.rectangle(frame, (x+hx, y+hy), (x+hx+hw, y+hy+hh), (255, 0, 0), 2)
#
#             # Calculate the position of the hand in relation to the center of the image
#             hand_center_x = x + hx + hw/2
#             if hand_center_x < center_x:
#                 print("Hand is on the left side")
#             else:
#                 print("Hand is on the right side")
#
#     # Display the resulting image
#     cv2.imshow('frame', frame)
#
#     # Exit the loop if 'q' is pressed
#     if cv2.waitKey(1) == ord('q'):
#         break
#
# # Release the capture and close all windows
# cap.release()
# cv2.destroyAllWindows()
