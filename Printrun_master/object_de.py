# import cvzone
# import cv2
# from time import time
#
# previous = time()
# delta = 0
# mul_camera = cv2.VideoCapture(2)
# up_camera = cv2.VideoCapture(1)
# myClassifier = cvzone.Classifier('keras_model.h5', 'labels.txt')
# while True:
#     ret, frame1 = up_camera.read()
#     cv2.imshow('camera1', frame1)
#
#
#     # prediction, index = myClassifier.getPrediction(frame)
#
#     # # print(prediction)
#     # # print(index)
#     current = time()
#     delta += current - previous
#     previous = current
#     if delta > 10:
#         print(delta)
#         ret, img = mul_camera.read()
#         img = cv2.flip(img, 0)
#         prediction, index = myClassifier.getPrediction(img)
#         # Operations on image
#         # Reset the time counter
#         cv2.imshow('image', img)
#         cv2.waitKey(1)
#         delta = 0
#
#     cv2.waitKey(1)
#
#
#         # cv2.imshow('image', img)
#         # # cv2.waitKey(1)
#
# mul_camera.release()
# up_camera.release()
# cv2.destroyAllWindows()
#
#
import datetime as dt

# Save the current time to a variable ('t')
t = dt.datetime.now()

while True:
    delta = dt.datetime.now()-t
    if delta.seconds == 10:
        print("30 Min")
        # Update 't' variable to new time
        # t = dt.datetime.now()
    if delta.seconds == 60:
        print("60 Min")
        # Update 't' variable to new time
        t = dt.datetime.now()

