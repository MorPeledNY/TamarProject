from printrun.printcore import printcore
from printrun import gcoder
import time
import signal
from printrun.plugins import PRINTCORE_HANDLER
import cv2
import numpy

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

def welcome():
    p.send_now("M117 welcome")
    time.sleep(2)
    p.send_now("G28")
    p.send_now("G1 X100")
    p.send_now("M117 hoe do you fill")



p = printcore()
p.connect('COM3', 115200, True)
welcome()


signal.signal(signal.SIGINT, signal_handler)





# time.sleep(2)
# p.send_now("G1 X10")
# time.sleep(2)
# print("move X")

# p.send_now("G1 Y5")
# time.sleep(2)
# print("move Y")



#p = printcore()
# p.connect('COM3', 115200, True)
# print("hi")
# gcode=[i.strip() for i in open('test.gcode')] # or pass in your own array of gcode lines instead of reading from a file
# gcode = gcoder.LightGCode(gcode)
#
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
# signal.signal(signal.SIGINT, signal_handler)
#
# # startprint silently exits if not connected yet
# while not p.online:
#   time.sleep(0.1)
#   print("wiating")
#
# p.startprint(gcode)  # this will start a print
# p.send_now("M105")
#If you need to interact with the printer:
# p.connect()
#p.send_now("G1 Z5") # this will send M105 immediately, ahead of the rest of the print
# p.pause() # use these to pause/resume the current print
# p.resume()
# p.disconnect() # this is how you disconnect from the printer once you are done. This will also stop running prints.



#
# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#
# eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
#
# cap = cv2.VideoCapture(0)
# is_print = True
# state_count = 0
# while 1:
#     ret, img = cap.read()
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     if len(faces) > 0:
#         if not is_print:
#             state_count += 1
#             if state_count > 5:
#                 is_print = not is_print
#                 p.resume()
#                 print("found eyes. continue")
#         else:
#             state_count = 0
#     else:
#         if is_print:
#             state_count += 1
#             if state_count > 5:
#                 is_print = not is_print
#                 p.pause()
#                 print("eyes just disappeared")
#
#         else:
#             state_count = 0
#
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
#         roi_gray = gray[y:y + h, x:x + w]
#         roi_color = img[y:y + h, x:x + w]
#
#         eyes = eye_cascade.detectMultiScale(roi_gray)
#
#         for (ex, ey, ew, eh) in eyes:
#             cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
#
#
#
#
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

# detector = HandDetector(detectionCon=0.8, maxHands=1)
# sucess, img = cap.read()
# hands, img = detector.findHands(img)
#     if hands:
#         hand = hands[0]
#         handType = hand["type"]
#         if handType == "Left":
#             if direction != "Left":
#                 change_state_count += 1
#                 if change_state_count > 5:
#                     direction = "Left"
#                     change_state_count = 0
#             else:
#                 change_state_count = 0
#
#             if handType == "Right":
#                 if direction != "Right":
#                     change_state_count += 1
#                     if change_state_count > 5:
#                         direction = "Right"
#                         change_state_count = 0
#                 else:
#                     change_state_count = 0
#
#     cv2.imshow("images", img)
#     k = cv2.waitKey(30) & 0xff
#     if k == 27:
#         break
#     time.sleep(0.1)
# cap.release()
# cv2.destroyAllWindows()

