# USAGE
# python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2

# import the necessary packages
import mysql.connector
from mysql.connector import errorcode
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from rasp4 import *
from Functions import *
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
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
ws = websocket.WebSocket()
ws.connect('ws://192.168.123.147:8000/ws/sendVideo/')

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

model_path = '/Users/macos/Documents/Ras/shape_predictor_68_face_landmarks.dat'

# Initialize two counters
BLINK_COUNT = 0
FRAME_COUNT_EAR = 0
FRAME_COUNT_MAR = 0
FRAME_COUNT_DISTR = 0

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO]Loading the predictor.....")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

# Grab the indexes of the facial landamarks for the left and right eye respectively
(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mstart, mend) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

count_sleep = 0
count_yawn = 0

imageHub = imagezmq.ImageHub()
time.sleep(2)

while True:
    (rpiName, frame) = imageHub.recv_image()
    frame = imutils.resize(frame, width=500)
    # receive RPi name and frame from the RPi and acknowledge
    # if a device is not in the last active dictionary then it means
    # that its a newly connected device
    if rpiName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(rpiName))

    # # record the last active time for the device from which we just
    # # received a frame
    lastActive[rpiName] = datetime.now()

    # the receipt
    imageHub.send_reply(b'OK')
    cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

    # # Resize the frame
    frame = imutils.resize(frame, width=400)
    (h, w) = frame.shape[:2]
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces
    rects = detector(frame, 1)
    # Now loop over all the face detections and apply the predictor
    if rects is not None:
        rect = get_max_area_rect(rects)
        if rect is not None:
            shape = predictor(gray, rect)
            # Convert it to a (68, 2) size numpy array
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lstart:lend]
            rightEye = shape[rstart:rend]
            mouth = shape[mstart:mend]

            # Compute the EAR for both the eyes
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            # Take the average of both the EAR
            EAR = (leftEAR + rightEAR) / 2.0

            # Compute the convex hull for both the eyes and then visualize it
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            # Draw the contours
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [mouth], -1, (0, 255, 0), 1)

            MAR = mouth_aspect_ratio(mouth)

            # Check if EAR < EAR_THRESHOLD, if so then it indicates that a blink is taking place
            # Thus, count the number of frames for which the eye remains closed
            if EAR < EAR_THRESHOLD:
                FRAME_COUNT_EAR += 1

                cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)

                if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                    # Add the frame to the dataset ar a proof of drowsy driving
                    pp = json.dumps({
                        'imgByte': f'Xin chao'
                    })
                    try:
                        ws.send(pp)
                    except Exception as e:
                        print(str(e))
                    cv2.putText(frame, "DROWSINESS ALERT!", (270, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_EAR = 0

            # Check if the person is yawning
            if MAR > MAR_THRESHOLD:
                FRAME_COUNT_MAR += 1

                cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)

                if FRAME_COUNT_MAR >= 10:
                    sendToDjango("YOU R YAWNING")
                    cv2.putText(frame, "YOU ARE YAWNING!", (270, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_MAR = 0
        else:
            FRAME_COUNT_DISTR += 1

            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                cv2.putText(frame, "EYES ON ROAD PLEASE!!!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_DISTR = 0

        # build a montage using images in the frame dictionary
        # detect any kepresses
        frameDict[rpiName] = frame

        # build a montage using images in the frame dictionary
        montages = build_montages(frameDict.values(), (w, h), (2, 2))

        # display the montage(s) on the screen
        for (i, montage) in enumerate(montages):
            cv2.imshow("Home pet location monitor ({})".format(i),
                montage)
        # detect any kepresses
        key = cv2.waitKey(1) & 0xFF     
    

    # if current time *minus* last time when the active device check
    # was made is greater than the threshold set then do a check
    if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
        # loop over all previously active devices
        for (rpiName, ts) in list(lastActive.items()):
            # print(ts, datetime.now())
            # remove the RPi from the last active and frame
            # dictionaries if the device hasn't been active recently
            if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
                print("[INFO] lost connection to {}".format(rpiName))
                lastActive.pop(rpiName)
                frameDict.pop(rpiName)

    # set the last active check time as current time
    lastActiveCheck = datetime.now()
    
    # set the last active check time as current time
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# initialize the ImageHub object

# start looping over all the frames

# do a bit of cleanup
cv2.destroyAllWindows()
