# import the necessary packages
from functions import *
from imutils import build_montages
from calculator_functions import *
from imutils import face_utils
from datetime import datetime
import dlib
import imagezmq
import imutils
import cv2
import time

COUNT_FRAME = 0

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
CONSECUTIVE_FRAMES_MOUTH = 20


# model_path = 'model/shape_predictor_68_face_landmarks.dat'
model_path = 'model/custom_landmark_model.dat'

# Initialize two counters
BLINK_COUNT = 0
FRAME_COUNT_EAR = 0
FRAME_COUNT_MAR = 0
FRAME_COUNT_DISTR = 0

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO] Loading the predictor ...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

cap = cv2.VideoCapture(0)

count_sleep = 0
count_yawn = 0

print("[INFO] Predictor is ready!")

while True:
    ret, frame = cap.read()
    cv2.putText(frame, str(COUNT_FRAME), (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
    COUNT_FRAME=COUNT_FRAME+1
    # if rpiName not in lastActive.keys():
    #     print("[INFO] receiving data from {}...".format(rpiName))
    # lastActive[rpiName] = datetime.now()
    # imageHub.send_reply(b'OK')
    cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

    frame = imutils.resize(frame, width=500)
    (h, w) = frame.shape[:2]
    rects = detector(frame, 0)
    
    if len(rects) > 0:
        rect = get_max_area_rect(rects)
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[0:6]
        rightEye = shape[6:12]
        mouth = shape[12:32] 

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
                cv2.putText(frame, "DROWSINESS ALERT!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                FRAME_COUNT_EAR = 0
        else:
            FRAME_COUNT_EAR = 0

        if MAR > MAR_THRESHOLD:
            FRAME_COUNT_MAR += 1
            cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)
            if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES:
                cv2.putText(frame, "YOU ARE YAWNING!", (270, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                FRAME_COUNT_MAR = 0
        else:
            FRAME_COUNT_MAR = 0

        FRAME_COUNT_DISTR = 0
    else:
        FRAME_COUNT_DISTR += 1

        if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
            cv2.putText(frame, "EYES ON ROAD PLEASE!!!", (270, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("output", frame)
    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF
    
    # set the last active check time as current time
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()