# import the necessary packages
from rasp4 import *
from Functions import *
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from datetime import datetime
import base64
import websocket
import json
import random
import datetime as dt
import numpy as np
import dlib
import imagezmq
import imutils
import cv2
import time

COUNT_FRAME=0

# Connect to Django Server
# ws = websocket.WebSocket()
# ws.connect('ws://192.168.123.147:8000/ws/realtimeData/')

# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
frameDict = {}
# was made was now
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
CONSECUTIVE_FRAMES_MOUTH = 20

model_path = 'shape_predictor_68_face_landmarks.dat'

# Initialize two counters
BLINK_COUNT = 0
FRAME_COUNT_EAR = 0
FRAME_COUNT_MAR = 0
FRAME_COUNT_DISTR = 0

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO] Loading the predictor ...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# Grab the indexes of the facial landamarks for the left and right eye respectively
(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

count_sleep = 0
count_yawn = 0

print("[INFO] Predictor is ready!")

print("[INFO] Loading ImageHub ...")
imageHub = imagezmq.ImageHub()
time.sleep(2)
print("[INFO] Start recv_image!")

while True:
    (rpiName, frame) = imageHub.recv_image()
    cv2.putText(frame, str(COUNT_FRAME), (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
    COUNT_FRAME=COUNT_FRAME+1
    if rpiName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(rpiName))
    lastActive[rpiName] = datetime.now()
    imageHub.send_reply(b'OK')
    cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

    frame = imutils.resize(frame, width=500)
    (h, w) = frame.shape[:2]
    gray = frame
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
                # sendDjango('Pi 1', 'Drowsiness', ws)
                cv2.putText(frame, "DROWSINESS ALERT!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                FRAME_COUNT_EAR = 0
        else:
            FRAME_COUNT_EAR = 0

        if MAR > MAR_THRESHOLD:
            FRAME_COUNT_MAR += 1
            cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)
            if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES:
                # sendDjango('Pi 1', 'Yawning', ws)
                cv2.putText(frame, "YOU ARE YAWNING!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                FRAME_COUNT_MAR = 0
        else:
            FRAME_COUNT_MAR = 0

        FRAME_COUNT_DISTR = 0
    else:
        FRAME_COUNT_DISTR += 1

        if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
            # sendDjango('Pi 1', 'MissingFace', ws)
            cv2.putText(frame, "EYES ON ROAD PLEASE!!!", (270, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # # build a montage using images in the frame dictionary
    # # detect any kepresses
    # frameDict[rpiName] = frame

    # # build a montage using images in the frame dictionary
    # montages = build_montages(frameDict.values(), (w, h), (2, 2))

    # # display the montage(s) on the screen
    # for (i, montage) in enumerate(montages):
    #     cv2.imshow("Home pet location monitor ({})".format(i), montage)
    cv2.imshow("output", frame)
    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF
    
    # set the last active check time as current time
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()