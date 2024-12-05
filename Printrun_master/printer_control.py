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


def mic_record():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2  # camera on printer mast to be conect
    fs = 44100
    seconds = 5
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


if __name__ in "__main__":

    engine = pyttsx3.init()
    # playsound('welcom.mp3')
    all_voices = engine.getProperty('voices')
    engine.setProperty('voice', all_voices[1].id)
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 100)
    signal.signal(signal.SIGINT, signal_handler)
    engine.say('Welcome Mor  ... how do you feel today?')
    engine.runAndWait()
    mic_record()
    model = whisper.load_model("base")
    result = model.transcribe('output.wav', fp16=False)
    print(result['text'])
    text1 = result['text']
    print(te.get_emotion(text1))
    # creat gcode from stl file
    subprocess.call([r'D:\\Slic3r-1.3.0.64bit\\Slic3r-console.exe', 'D:\\Slic3r-1.3.0.64bit\\body2.stl', '--load',
                     'D:\\Slic3r-1.3.0.64bit\\config.ini', '--output',
                     'C:\\Users\\Mor\\PycharmProjects\\pythonProject\\Printrun_master\\test.gcode'])

    engine.say(" minutes.")
    engine.runAndWait()

    #conect to printer+ send the gcode
    p = printcore()
    p.connect('COM3', 115200, True)
    print("hi")
    gcode = [i.strip() for i in open('test.gcode')]
    gcode = gcoder.LightGCode(gcode)


    # startprint silently exits if not connected yet
    while not p.online:
        time.sleep(0.1)
        print("wiating")

    p.startprint(gcode)  # this will start a print
    engine.say(" you?")
    engine.runAndWait()


    engine.say("Thanks, now I'm starting to warm up")
    engine.runAndWait()

    # open camera
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    cap = cv2.VideoCapture(0) # 0 computer 1 camera on printer
    is_print = True
    state_count = 0
    while 1:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            if not is_print:
                state_count += 1
                if state_count > 5:
                    is_print = not is_print
                    p.resume()
                    print("found eyes. continue")
            else:
                state_count = 0
        else:
            if is_print:
                state_count += 1
                if state_count > 5:
                    is_print = not is_print
                    p.pause()
                    print("eyes just disappeared")
                    # talk to the printer



            else:
                state_count = 0

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

        cv2.imshow('img', img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

