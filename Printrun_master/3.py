# import numpy as np
# import time
# import os
# import HandTrackingModule as htm
# import cv2
#
# folderPath = "Header"
# myList = os.listdir(folderPath)
# print(myList)
# overlayList = []
# for imPath in myList:
#     image = cv2.imread(f'{folderPath}/{imPath}')
#     overlayList.append(image)
# print(len(overlayList))
# header = overlayList[0]
# drawColor = (255, 0, 255)
# cap = cv2.VideoCapture(0)
# cap.set(3, 1280)
# cap.set(4, 720)
#
# while True:
#
#     # 1. Import image
#     success, img = cap.read()
#     # img[0:125, 0:1280] = header
#
#     cv2.imshow("Image", img)
#     cv2.waitKey(1)

import wave

filename = "output.wav"

with wave.open(filename, 'rb') as audio_file:
    channels = audio_file.getnchannels()

print(channels)