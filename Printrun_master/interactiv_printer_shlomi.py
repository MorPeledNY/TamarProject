# imports
import time
import signal
import cv2
from printrun.printcore import printcore
from printrun import gcoder
from playsound import playsound
import whisper
import text2emotion as te
import pyaudio
import wave
import pyttsx3
import mediapipe as mp
from google.protobuf.json_format import MessageToDict

# globals
all_states = ['not_connected', 'connecting', 'dialog', 'print_center', 'print_right_left', 'paus_print']
current_state = all_states[0]
p = printcore()
model = whisper.load_model("base")
print_in_progress = False
mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, model_complexity=1, min_detection_confidence=0.75,
                      min_tracking_confidence=0.75, max_num_hands=2)
moving_direction='left'


def send_commands(commands: list, wait=True):
    commands_gcode = gcoder.LightGCode(commands)
    p.startprint(commands_gcode)
    time.sleep(0.5)
    if wait:
        while print_in_progress:
            time.sleep(0.01)

def add_commands(commands: list):
    for command in commands:
        p.send(command)

def send_command(command: str):
    send_commands([command])

def end_callback():
    global print_in_progress
    print_in_progress = False
    print('job finished')


def start_callback(printer):
    global print_in_progress
    print_in_progress = True
    print('job started')


def add_new_p(gcode_list: list, _direction: str):
    gcode_list.insert(0, "G91;")
    gcode_list.insert(1, f"G1 X{int(_direction == 'Left') * '-'}1 Y0.15 F3000 ;")
    gcode_list.insert(2, "G1 Z2 ;")
    gcode_list.insert(3, "G90 ;Absolute positioning")
    gcode_list.insert(4, "G92 E0 X0 Y0 ; Reset Extruder")
    gcode_list.append("G1 X0 Y0")
    return gcode_list


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


def listen():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2  # camera on printer mast to be conect
    fs = 44100
    seconds = 3
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
    return result["text"]


def set_state(state_number: int):
    global current_state
    prev_state = current_state
    current_state = all_states[state_number]
    print(f'moving from {prev_state} to {current_state}')


if __name__ == "__main__":

    # camera initializations
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False, model_complexity=1, min_detection_confidence=0.75,
                          min_tracking_confidence=0.75, max_num_hands=2)

    cap = cv2.VideoCapture(1)
    count_number = 0
    layer_template = [i.strip() for i in open('retangel0.5mm_rel.gcode')]
    layer_number = 1
    change_state_count = 0
    direction = "Right"
    change_look_count = 0
    change_direction = 0
    is_look_at_me = False
    prev_is_look_at_me = False
    hade_side = 0
    hade_position = 'left'
    input_answer = 'n'

    # printer initializations
    p.startcb = start_callback
    p.endcb = end_callback
    signal.signal(signal.SIGINT, signal_handler)
    print_first_layer = False
    p.connect('COM16', 115200, True)

    # main loop
    while True:

        # camera recognitions
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        prev_is_look_at_me = is_look_at_me

        if len(faces) > 0:
            if not is_look_at_me:
                change_look_count += 1
            else:
                change_look_count = 0
        else:
            if is_look_at_me:
                change_look_count += 1
            else:
                change_look_count = 0

        if change_look_count > 3:
            is_look_at_me = not is_look_at_me
            print('now i see you' if is_look_at_me else 'i dont see you anymore')

        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x + w
            y2 = y + h
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            middle_x = int(gray.shape[1] / 2)
            middle_y = int(gray.shape[0] / 2)
            distance_x = center_x - middle_x
            distance_y = center_y - middle_y
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.line(img, (center_x, center_y), (middle_x, middle_y), (0, 255, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            if center_x > middle_x:
                cv2.putText(img, 'Right', (x2, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                hade_position = 'right'
            else:
                cv2.putText(img, 'Left', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                hade_position = 'left'




        cv2.imshow('img', img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

        # not connected state
        if current_state == all_states[0] and input_answer=='n':
            if is_look_at_me:
                print("connecting...")
                time.sleep(0.2)
                send_commands(['M117 connected', 'G28'])
                input_answer = input("to be continu?")
                if input_answer =='c':
                    set_state(2)
            else:
                continue


        # dialog state
        if current_state == all_states[2] and input_answer == 'c':

            # did we finish preparing?
            if print_in_progress:
                continue


            send_commands(['M117 welcome','G1 X100'])
            playsound('myNameIsTamar.mp3')
            time.sleep(0.1)

            # say something
            send_commands(['G1 Y30', 'M117 Speaking', 'G0 Z10'])
            playsound('HowWasYourDay.mp3')
            time.sleep(0.1)
            #
            # now listening
            send_commands(['G1 Y-30', 'M117 Listening'])
            time.sleep(4)
            #
            # say something
            send_commands([i.strip() for i in open('CE3E3V2_IGUL.gcode')], False)
            playsound('IFeelTheSameCreatTogether.mp3')
            time.sleep(1.2)
            #
            # now listening
            send_commands(['G0 Y-30','M117 Listening'])
            time.sleep(3)

            # say something
            send_commands(['M117 Speaking', 'G1 Y30 X120', 'G1 X90', 'G1 X100'])
            playsound('CreatWithYourHands.mp3')

            send_commands(['G1 Y-30', 'M117 Listening'])
            time.sleep(3)

            send_commands(['M117 Speaking', 'G0 Z20 X130 Y30', 'G0 Z30 X60', 'G1 X90', 'G1 X70','G0 Z-30 X100 Y-30'])
            playsound('UseThamToMoveMe.mp3')
            time.sleep(1)

            send_commands(['M117 Listening'])
            time.sleep(3)
            #
            send_commands([i.strip() for i in open('CE3E3V2_IGUL2.txt')], False)
            playsound('WantToStart.mp3')
            time.sleep(1)

            send_commands(['M117 Listening'])
            time.sleep(3)

            send_commands(['M117 Speaking', 'G0 Z5', 'G0 Z7','G0 Z5', 'G0 Z7','G0 Z5','G0 Z7','G0 Z5','G0 Z7','G0 Z40 Y-20','G1 X120 Y6', 'G1 X80 Y4', 'G1 X120 Y5','G1 X100', 'G0 Z-40 y-10'])
            playsound('FunFunFun.mp3')
            time.sleep(1)

            send_commands(['M117 Listening'])
            time.sleep(3)

            send_commands([ 'M117 Speaking','G0 Z7 y10','G0 Z5 y4','G0 Z7 y10','G0 Z5 y4' ])
            playsound('LetsStart.mp3')
            time.sleep(6)

            send_commands(['G1 YO X0','M117 Speaking','G1 Y100', 'G1 X30'])
            playsound('1.mp3')
            time.sleep(1)

            send_commands([ 'G1 X100','M117 lets play', 'G1 Y-30 Z40'])
            playsound('2.mp3')

            send_commands(['M117 Listening'])

            input_answer = input("to be continu?")
            if input_answer == 'p':
                prev_is_look_at_me = False

        if input_answer == 'p':
            if hade_position == 'left' and moving_direction != 'left':
                moving_direction = 'left'
                send_commands(["G1 X93"], False)
            elif hade_position == 'right' and moving_direction != 'right':
                moving_direction = 'right'
                send_commands(["G1 X113"], False)

            if prev_is_look_at_me != is_look_at_me:
                if is_look_at_me:
                    send_commands(['M117 I see you'], False)
                else:
                    send_commands(['M117 I dont see you'], False)
                    playsound("lost.mp3")
                    input_answer = 'y'

        if input_answer == 'y':

            send_commands(['M117 Speaking', 'G1 Z-40', 'G0 Y120', 'G0 X120 Y90'])
            playsound('3.mp3')
            time.sleep(0.2)

            send_commands(['G1 Z5', 'M117 Touch me', 'G1 X70', 'G1 X110', 'Y-30'])
            playsound('7.mp3')
            time.sleep(5)

            send_commands(['G0 Z7','G0 Z5','G0 Z7','M117 It tickles','G0 Z5','G0 Z7','G0 Z5','G0 Z7','G0 Z5','G1 X100','G1 Y-30','G0 Y100 Z30'])
            playsound('8.mp3')
            time.sleep(0.2)

            send_commands(['M117 put your hand', 'G1 Z45','Z40'])
            playsound('9.mp3')
            time.sleep(1)

            send_commands([i.strip() for i in open('CE3E3V2_IGUL2.txt')])
            time.sleep(1)

            send_commands(['M117 Speaking', 'G1 X30 Z0', 'G1 Y-100', 'G0 Y0 X0','M117 Bye Bye'])
            playsound('11.mp3')
            time.sleep(1)
            signal_handler()

    cap.release()
    cv2.destroyAllWindows()
