# USAGE
# python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2

# import the necessary packages
from mysql.connector import errorcode
from rasp4 import *
from Functions import *
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
from imutils.video import VideoStream
import base64
import websocket
import json
import random
import datetime as dt
import numpy as np
import mysql
import dlib
import imagezmq
import argparse
import imutils
import cv2
import time

#Connect to Django Server
# ws = websocket.WebSocket()
# ws.connect('ws://192.168.123.149:8000/ws/realtimeData/')

frameDict = {}
lastActive = {}
lastActiveCheck = datetime.now()

# Predict and display
ESTIMATED_NUM_PIS = 4
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = 1

# parameter
distracton_initlized = False
eye_initialized = False
mouth_initialized = False

EAR_THRESHOLD = 0.2

MAR_THRESHOLD = 10

CONSECUTIVE_FRAMES = 20

model_path = 'shape_predictor_68_face_landmarks.dat' #Your model path

# Initialize two counters
BLINK_COUNT = 0
FRAME_COUNT_EAR = 0
FRAME_COUNT_MAR = 0
FRAME_COUNT_DISTR = 0

print("[INFO]Loading the predictor.....")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# Grab the indexes of the facial landamarks for the left and right eye respectively
(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

count_sleep = 0
count_yawn = 0
# video=cv2.VideoCapture(0)
# time.sleep(2)
vs = VideoStream(src=0,).start()
time.sleep(1.0)

# imageHub = imagezmq.ImageHub()
# time.sleep(2)

while True:
    # (rpiName, frame) = imageHub.recv_image()
    frame=vs.read()
    rpiName="Pi_1"
    
    if rpiName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(rpiName))

    lastActive[rpiName] = datetime.now()

    # # imageHub.send_reply(b'OK')
    # cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(frame, 1)
    
    if len(rects) > 0:
        rect = get_max_area_rect(rects)
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        leftEye = shape[lstart:lend]
        rightEye = shape[rstart:rend]
        mouth = shape[mstart:mend]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        EAR = (leftEAR + rightEAR) / 2.0
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [mouth], -1, (0, 255, 0), 1)
        MAR = mouth_aspect_ratio(mouth)

        if EAR < EAR_THRESHOLD:
            FRAME_COUNT_EAR += 1
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
            if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                # sendDjango('P1', 'DROWSINESS', ws)
                cv2.putText(frame, "DROWSINESS ALERT!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            FRAME_COUNT_EAR = 0

        if MAR > MAR_THRESHOLD:
            FRAME_COUNT_MAR += 1
            cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)
            if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES:
                # sendDjango('P1', 'YAWNING', ws)
                cv2.putText(frame, "YOU ARE YAWNING!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            FRAME_COUNT_MAR = 0
        FRAME_COUNT_DISTR = 0
    else:
        FRAME_COUNT_DISTR += 1

        if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
            # sendDjango('P1', 'NO EYES WERE DETECTED', ws)
            cv2.putText(frame, "EYES ON ROAD PLEASE!!!", (270, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    frameDict[rpiName] = frame
    montages = build_montages(frameDict.values(), (w, h), (2, 2))

    # display the montage(s) on the screen
    for (i, montage) in enumerate(montages):
        cv2.imshow("Home pet location monitor ({})".format(i),
            montage)

    key = cv2.waitKey(1) & 0xFF    
    if key == ord("q"):
        break
    
cv2.destroyAllWindows()
