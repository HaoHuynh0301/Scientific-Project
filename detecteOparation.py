import websocket
import socket
try:
    import thread
except ImportError:
    import _thread as thread
from model.EAR_calculator import *
from libs.VideoActivity import VideoActivity
from libs.Socket import Socket
from imutils import face_utils
from libs.DateTime import DateTime
from imutils.video import VideoStream
from datetime import datetime
import wiringpi as wiringpi
from time import sleep
import time
import json
import dlib
import cv2
import imutils

def detecteOparation(GENERAL_VIDEO_PATH, MODEL_PATH, ws,connect):
    GENERAL_VIDEO = VideoActivity(GENERAL_VIDEO_PATH)
    if connect:
        SOCKET = Socket(ws)
        
    lastActive = datetime.now()
    send = False
    COUNT_FRAME = 0

    frameDict = {}
    lastActiveCheck = datetime.now()

    # Predict and display
    ESTIMATED_NUM_PIS = 4
    ACTIVE_CHECK_PERIOD = 10
    ACTIVE_CHECK_SECONDS = 1

    # Parameter
    distracton_initlized = False
    eye_initialized = False
    mouth_initialized = False

    EAR_THRESHOLD = 0.2

    MAR_THRESHOLD = 10

    CONSECUTIVE_FRAMES = 18
    CONSECUTIVE_FRAMES_MOUTH = 5

    # Initialize two counters
    BLINK_COUNT = 0
    FRAME_COUNT_EAR = 0
    FRAME_COUNT_MAR = 0
    FRAME_COUNT_DISTR = 0

    # Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
    print("[INFO]: Loading the predictor ...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(MODEL_PATH)
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    count_sleep = 0
    count_yawn = 0
    print("[INFO]: Predictor is ready!")
    
    #MQ3 sensor code
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(25, 0)
    count = 0
    print("[INFO]: MQ3 SENSOR is ready!")

    while True:
        
        #Alcolho detected
        my_input=wiringpi.digitalRead(25)
        if(my_input):
         pass
        else:
         count=count+1
        if count == 5:
         sendTime = str(datetime.now())
         print("[INFOR]: Alcohol Detected")
         SOCKET.sendToDjango('Alcohol Detected', sendTime, ws)
         count = 0
        
        #Get frames
        frame = vs.read()
        frame = cv2.resize(frame, (720,480))
        GENERAL_VIDEO.writeFrames(frame)
        COUNT_FRAME = COUNT_FRAME + 1

        frame = imutils.resize(frame, width=400)
        (h, w) = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(frame, 0)

        if len(rects) > 0:
            rect = get_max_area_rect(rects)
            shape = predictor(frame, rect)
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
                if FRAME_COUNT_EAR == 0:
                    saveTime, sendTime = DATETIME.getDateNameFormat()
                    writterDrowsiness = VideoActivity('media/detail/drowsiness/drowsiness' + saveTime + '.avi')
                    FRAME_COUNT_EAR += 1
                else:
                    FRAME_COUNT_EAR += 1
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
                    frame = cv2.resize(frame, (720,480))
                    writterDrowsiness.writeFrames(frame)
                if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                    if connect:
                        SOCKET.sendToDjango('Drowsiness', sendTime, ws)
                    writterDrowsiness.releaseVideo()
                    FRAME_COUNT_EAR = 0
            else:
                FRAME_COUNT_EAR = 0

            if MAR > MAR_THRESHOLD:
                if FRAME_COUNT_MAR == 0:
                    saveTime, sendTime = DATETIME.getDateNameFormat()
                    writterYawning = VideoActivity('media/detail/yawning/yawning' + saveTime + '.avi')
                    FRAME_COUNT_MAR += 1
                else:
                    FRAME_COUNT_MAR += 1
                    frame = cv2.resize(frame, (720,480))
                    writterYawning.writeFrames(frame)
                print(FRAME_COUNT_MAR)
                  
                if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES_MOUTH:
                    print('[INFOR]: YOU ARE YAWNING')
                    if connect:
                        SOCKET.sendToDjango('Yawning', sendTime, ws)
                    print('[INFOR]: YOU ARE YAWNING')
                    FRAME_COUNT_MAR = 0
                
            else:
                FRAME_COUNT_MAR = 0

            FRAME_COUNT_DISTR = 0
        else:
            FRAME_COUNT_DISTR += 1

            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                print("[INFOR]: NO EYES")
                print("WARNING: HU' HU' HU'")
                            
    GENERAL_VIDEO.releaseVideo()
    print("thread terminating...")
    if connect:
        ws.close()
