import websocket
import socket
import time
import json
import dlib
import cv2
import imutils
from threading import Thread
import threading
try:
    import thread
except ImportError:
    import _thread as thread
from model.EAR_calculator import *
from libs.videoutils import VideoUtils
from libs.datetime import DateTime
from libs.socket import Socket
from libs.utils import Utils, SoundThread
from imutils import face_utils
from imutils.video import VideoStream
from datetime import datetime
from os import system, name
import signal
# import wiringpi as wiringpi
import subprocess

EAR_THRESHOLD = 0.2

CONSECUTIVE_FRAMES = 25

MODEL_PATH = 'model/custom_model_20_6_2021.dat'

# Initialize two counters
FRAME_COUNT_EAR = 0
FRAME_COUNT_DISTR = 0

def play(audio_file_path):
    subprocess.call(["afplay", audio_file_path])

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO] Loading the predictor ...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)

vs = cv2.VideoCapture(0)
vs.set(3, 160)
vs.set(4, 120)

print("[INFO] Predictor is ready!")

while True:
    ret, frame = vs.read()
    (h, w) = frame.shape[:2]
    rects = detector(frame, 0)
    
    if len(rects) > 0:
        rect = get_max_area_rect(rects)
        (x, y, w, h) = face_utils.rect_to_bb(rect)
        shape = predictor(frame, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[0:6]
        rightEye = shape[6:12]

        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        EAR = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)

        if EAR < EAR_THRESHOLD:
            FRAME_COUNT_EAR += 1
            if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                cv2.putText(frame, "DROWSINESS ALERT!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            FRAME_COUNT_EAR = 0

        FRAME_COUNT_DISTR = 0
    else:
        FRAME_COUNT_DISTR += 1

        if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
            cv2.putText(frame, "EYES ON ROAD, PLEASE!", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("output", frame)

    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()