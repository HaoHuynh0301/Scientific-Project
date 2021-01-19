# USAGE
# python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2

# import the necessary packages
# from rasp4 import sendToDjango
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
import datetime as dt
import numpy as np
import dlib
import imagezmq
import argparse
import imutils
import cv2
import time

list_frame=[]

lastActiveCheck = datetime.now()

ESTIMATED_NUM_PIS = 4
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

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
# print(type(imageHub))
# initialize the ImageHub object

# start looping over all the frames
while True:
    rpiName, frame = imageHub.recv_image()
    frame = imutils.resize(frame, width=400)
    # receive RPi name and frame from the RPi and acknowledge
    # the receipt
    imageHub.send_reply(b'OK')
    cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

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
                    # sendToDjango("Con di me m")
                    cv2.putText(frame, "DROWSINESS ALERT!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_EAR = 0

            # Check if the person is yawning
            if MAR > MAR_THRESHOLD:
                FRAME_COUNT_MAR += 1

                cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)

                if FRAME_COUNT_MAR >= 10:
                    # sendToDjango("YOU R YAWNING")                 
                    cv2.putText(frame, "YOU ARE YAWNING!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_MAR = 0
        else:
            FRAME_COUNT_DISTR += 1

            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                # sendToDjango("EYES ON ROAD PLEASE")
                cv2.putText(frame, "EYES ON ROAD PLEASE!!!", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                FRAME_COUNT_DISTR = 0
                    
            # build a montage using images in the frame dictionary
            # detect any kepresses
        cv2.imshow("DEMO", frame)
            # detect any kepresses
        key = cv2.waitKey(1) & 0xFF
            # set the last active check time as current time
            # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    
cv2.destroyAllWindows()
