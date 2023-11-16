from cvzone.HandTrackingModule import HandDetector
from printrun.printcore import printcore
from printrun import gcoder
import time
import signal
from printrun.plugins import PRINTCORE_HANDLER
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from playsound import playsound
import cvzone
import cv2
import datetime as dt



y_move = 0
x_move = 0


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

def add_new_p(gcode_list: list, direction : str):
    global y_move, x_move
    time.sleep(0.1)
    gcode_list.insert(1, "G91;")
    gcode_list.insert(2, f"G1 X{int(direction == 'Left') * '-'}1 Y{int(direction == 'Left') * '-'}1 F3000 ;")
    gcode_list.insert(3, f"G1 Y{y_move} X{x_move}")
    # gcode_list.insert(4, f"G1 Z{z_move}")
    print(gcode_list[0:9])
    gcode_list.insert(4, f'M117 {direction} direction')
    gcode_list.insert(5, "G90 ;Absolute positioning")
    gcode_list.insert(6, "G92 E0 X0 Y0 ; Reset Extruder")
    gcode_list.append("G1 X0 YO")
    time.sleep(0.2)
    y_move = 0
    x_move =0
    return gcode_list


if __name__ in "__main__":
    # configure printer for communication
    print_in_progress = False
    p = printcore()
    p.connect('COM10', 115200, True)
    time.sleep(0.5)
    p.startcb = start_callback
    p.endcb = end_callback
    signal.signal(signal.SIGINT, signal_handler)
    direction = "Right"
    change_state_count = 0
    input_answer = 'n'
    t = dt.datetime.now()

    # startprint silently exits if not connected yet
    while not p.online:
      time.sleep(1)
    time.sleep(5)

    send_commands([i.strip() for i in open('to home.txt')])
    cap = cv2.VideoCapture(0)
    success, img = cap.read()
    mul_camera = cv2.VideoCapture(1)
    ret, img1 = mul_camera.read()

    if not print_in_progress:
        input_answer= input("to be continu?")


    if input_answer == 'y':

        # print first layer
        print('first layer')
        gcode = [i.strip() for i in open('oneSribua.txt')]
        gcode = gcoder.LightGCode(gcode)
        p.startprint(gcode)
        time.sleep(0.2)

        # start continues printing
        layer_template = [i.strip() for i in open('oneSribua_rel.txt')]
        layer_number = 1
        mpHands = mp.solutions.hands
        hands = mpHands.Hands(static_image_mode=False, model_complexity=1, min_detection_confidence=0.75,
                              min_tracking_confidence=0.75, max_num_hands=2)

        # Start capturing video from webcam
        cap = cv2.VideoCapture(1)
        mul_camera = cv2.VideoCapture(2)
        myClassifier = cvzone.Classifier('keras_model.h5', 'labels.txt')

        while True:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)

            delta = dt.datetime.now() - t
            if delta.seconds >= 20:
                print("30 sconed")
                # Update 't' variable to new time
                t = dt.datetime.now()
                ret, img1 = mul_camera.read()
                # img1 = cv2.flip(img1, 0)
                prediction, index = myClassifier.getPrediction(img1)
                print(index)
                cv2.imshow('image', img1)
                if index == 0:
                    print('new comand 0')
                    y_move = -5
                    x_move = -40
                    t = dt.datetime.now()
                if index == 2:
                    print('new comand 1')
                    y_move = -30
                    x_move = -20
                    t = dt.datetime.now()
                if index == 3:
                    print('new comand 3')
                    y_move = 10
                    x_move = 5
                    t = dt.datetime.now()
                if index == 3:
                    print('new comand 3')
                    y_move = 90
                    x_move = 40
                    t = dt.datetime.now()
                if index == 4:
                    print('new comand 4')
                    y_move = 30
                    x_move = 15
                    t = dt.datetime.now()


            if not print_in_progress:
                # get the template layer and add the prefix gcode before we start the layer
                print('new layer')
                new_layer = layer_template[:]
                new_layer = add_new_p(new_layer, direction)
                new_layer = gcoder.LightGCode(new_layer)
                p.startprint(new_layer)
                time.sleep(0.2)
                # layer_number += 1
                # p.send_now(f'layer number {layer_number}')

            if results.multi_hand_landmarks:

                # Both Hands are present in image(frame)
                if len(results.multi_handedness) == 2:
                    # Display 'Both Hands' on the image
                    cv2.putText(img, 'Both Hands', (250, 50),
                                cv2.FONT_HERSHEY_COMPLEX,
                                0.9, (0, 255, 0), 2)
                    p.pause()
                    time.sleep(5)



                # If any hand present
                else:
                    for i in results.multi_handedness:

                        # Return whether it is Right or Left Hand
                        label = MessageToDict(i)['classification'][0]['label']

                        if label == 'Left':
                            # Display 'Left Hand' on
                            # left side of window
                            cv2.putText(img, label + ' Hand',
                                        (20, 50),
                                        cv2.FONT_HERSHEY_COMPLEX,
                                        0.9, (0, 255, 0), 2)
                            if direction != "Left":
                                change_state_count += 1
                                if change_state_count > 5:
                                    direction = "Left"
                                    print('changed to ' + direction)
                                    time.sleep(0.1)
                                    change_state_count = 0
                            else:
                                change_state_count = 0

                        if label == 'Right':
                            # Display 'Left Hand'
                            # on left side of window
                            cv2.putText(img, label + ' Hand', (460, 50),
                                        cv2.FONT_HERSHEY_COMPLEX,
                                        0.9, (0, 255, 0), 2)
                            if direction != "Right":
                                change_state_count += 1
                                if change_state_count > 5:
                                    direction = "Right"
                                    print('changed to ' + direction)
                                    time.sleep(0.1)
                                    change_state_count = 0
                            else:
                                change_state_count = 0

                # Display Video and when 'q'
                # is entered, destroy the window
            cv2.imshow('Image', img)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break



    if input_answer == 'c':
        send_commands(['M117 connected', 'G28', 'M117 welcome','G1 X100'])
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
        time.sleep(5)

        # say something
        send_commands(['G1 Y30', 'M117 Speaking', 'G1 X120', 'G1 X80', 'G1 X120','G1 X100'])
        playsound('CreatWithYourHands.mp3')

        send_commands(['G1 Y-30', 'M117 Listening'])
        time.sleep(3)

        send_commands(['M117 Speaking', 'G0 Z20 X130 Y30', 'G0 Z30 X60', 'G1 X120', 'G1 X60','G0 Z-30 X100 Y-30'], False)
        playsound('UseThamToMoveMe.mp3')

        send_commands(['M117 Listening'])
        time.sleep(3)
        #
        send_commands([i.strip() for i in open('CE3E3V2_IGUL2.txt')], False)
        playsound('WantToStart.mp3')
        time.sleep(1)


        send_commands(['M117 Listening'])
        time.sleep(3)

        send_commands(['M117 Speaking', 'G0 Z7','G0 Z4','G0 Z7','G0 Z4',' G0 Z40 Y-20','G1 X120 Y6', 'G1 X80 Y4', 'G1 X120 Y5','G1 X100', 'G0 Z-40 y-10'])
        playsound('FunFunFun.mp3')
        time.sleep(1)

        send_commands(['M117 Listening'])
        time.sleep(3)

        send_commands(['G0 Z7 y10', 'M117 Speaking','G0 Z4 y4','G0 Z7 y10','G0 Z4 y4' ])
        playsound('LetsStart.mp3')

        input_answer = input("to be continu?")

