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
    # result = model.transcribe('output.wav', fp16=False)
    # return result["text"]


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

    # printer initializations
    p.startcb = start_callback
    p.endcb = end_callback
    signal.signal(signal.SIGINT, signal_handler)
    print_first_layer = False

    # main loop
    while True:

        # camera recognitions
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # recognize and draw all hands
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for i in results.multi_handedness:
                # Return whether it is Right or Left Hand
                label = MessageToDict(i)['classification'][0]['label']
                position = (460, 50) if label == "Right" else (20, 50)
                cv2.putText(img, label + ' Hand', position,
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.9, (0, 255, 0), 2)

                if label == 'Left':
                    if direction != "Left":
                        change_direction += 1
                        if change_direction > 5:
                            print('change to left direction')
                            direction = "Left"
                            change_direction = 0
                    else:
                        change_direction = 0

                if label == 'Right':
                    if direction != "Right":
                        change_direction += 1
                        if change_direction > 5:
                            print('change to Right direction')
                            direction = "Right"
                            change_direction = 0
                    else:
                        change_direction = 0

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

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

        if change_look_count > 5:
            is_look_at_me = not is_look_at_me
            print('now i see you' if is_look_at_me else 'i dont see you anymore')

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

        # not connected state
        if current_state == all_states[0]:
            if is_look_at_me:
                p.connect('COM3', 115200, True)
                print("connecting...")
                set_state(1)

            else:
                continue

        # connecting state
        if current_state == all_states[1]:
            # are we connected?
            if p.online:
                # preparing gcode
                send_commands(['M117 connected', 'G28', 'M117 welcome', 'G1 X100'])
                set_state(2)
            continue

        # dialog state
        if current_state == all_states[2]:

            # did we finish preparing?
            if print_in_progress:
                continue

            # asking the user for inputs
            playsound('how was your day.mp3')

            # now listening
            send_command('M117 Listening')
            user_input = listen()

            # say something
            send_commands(['G1 Y30', 'M117 Speaking'])
            playsound('Operating Instructions.mp3')

            # now listening
            send_commands(['G1 Y-30', 'M117 Listening'])
            user_input = listen()

            # say something
            send_commands(['G1 Y30', 'M117 Speaking', 'G1 X111.128 Y116.806'])
            playsound('eye contact.mp3')

            # # now listening
            # send_commands(['G1 Y-30', 'M117 Listening'])
            # user_input = listen()

            # say something
            send_commands(['G1 Y30', 'M117 Speaking'])
            playsound('Thank you2.mp3')

            # preparing print for printing
            send_commands([i.strip() for i in open('preper_printer.txt')])

            # move on to next state
            set_state(3)
            continue

        # print center state
        if current_state == all_states[3]:
            # did we finish preparing?
            if print_in_progress:
                continue

            center_layer = [i.strip() for i in open('retangel0.5mm.gcode')]
            send_commands(center_layer, False)
            print_first_layer = True
            print("first layer has started")
            set_state(4)
            continue

        # print right state
        if current_state == all_states[4]:
            if not is_look_at_me and p.printing:
                p.pause()
                print_in_progress = True
                print('pause')
            elif is_look_at_me and not p.printing:
                p.resume()
                print('resume')

            # did we finish first layer?
            if print_first_layer:
                if not print_in_progress:
                    print_first_layer = False
                    print('finished first layer')
                continue

            # did we finish printing?
            if not print_in_progress:
                print(f"start layer number {layer_number}")
                new_layer = layer_template[:]
                new_layer = add_new_p(new_layer, direction)
                for act in new_layer:
                    print(act)
                send_commands(new_layer, False)
                layer_number += 1
                p.send_now(f'M117 change to {direction}')

    cap.release()
    cv2.destroyAllWindows()
