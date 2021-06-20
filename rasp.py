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

#Fils, and folders intialize
HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)
COMPANY_ROOM_CODE = "lsRHGGT111"
ID = "1"
DATETIME = DateTime()
TMPDATETIME = ''
MODEL_PATH = 'model/custom_landmark_model.dat'

# Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFO]: Loading the predictor ...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)
vs = VideoStream(usePiCamera=True, resolution = (320,240)).start()
time.sleep(1.0)
print("[INFO]: Predictor is ready!")

#MQ3 sensor intialize
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(25, 0)
count = 0
print("[INFO]: MQ3 SENSOR is ready!")

    
def connect_websocket():
    url = f"ws://192.168.1.4:8000/ws/realtime/{COMPANY_ROOM_CODE}/{ID}/"
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    listFrame = []
    sendImage = False
    
    if data['piDeviceID'] == ID:
        try:
            VIDEO_FUNCTION = VideoActivity()
<<<<<<< HEAD
            #alertTime = DATETIME.getSendingDateNameFormat(data['time'])
            listFrame = VIDEO_FUNCTION.receiveRequestcut('20062021113507', 'yawning')
=======
            alertTime = DATETIME.getSendingDateNameFormat(data['time'])
            listFrame = VIDEO_FUNCTION.receiveRequestcut(alertTime, data['activity'])
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
            sendImage = True
        except Exception as e:
            print('[INFOR] Rasp1:'+ str(e))         
            
        if sendImage:       
            try:
                ws.send(
                    json.dumps({
                        'command': 'sendImgToBrowser',
                        'messageType': 'sendImg',
                        'driveID': data["driveID"],
                        'frame': listFrame,
                    })
                )
                time.sleep(0.5)  

            except Exception as e:
                print("[INFOR]" + str(e))

def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print("[SOCKET INFORMATION]: Can not connect to Websocket ...")
    detecteOparation(vs, detector, predictor, count, ws, False)

def on_open(ws):
    def run(*args):
        print("[SOCKET INFORMATION]: Connect to Websocket ...")
        detecteOparation(vs, detector, predictor, count, ws, True)
    thread.start_new_thread(run, ()) 

def detecteOparation(vs, detector, predictor, count, ws, connect):
    #Model, saving video path intialize
    GENERAL_VIDEO_PATH = 'media/general/rasp_' + str(datetime.now()) + "_connected.avi"
    if connect:
        GENERAL_VIDEO_PATH = 'media/general/rasp_' + str(datetime.now()) + "_disconnected.avi"
        SOCKET = Socket(ws)

    GENERAL_VIDEO = VideoActivity(GENERAL_VIDEO_PATH)
    COUNT_FRAME = 0

    EAR_THRESHOLD = 0.2

    MAR_THRESHOLD = 10

    CONSECUTIVE_FRAMES = 20
    CONSECUTIVE_FRAMES_MOUTH = 7

    # Initialize two counters
    YAWN_COUNT = 0
    FRAME_COUNT_EAR = 0
    FRAME_COUNT_MAR = 0
    FRAME_COUNT_DISTR = 0
    
    #Websocket connection detection
    FRAME_COUNT_CONNECT = 0
    if connect:
        print("[INFOR]: Start online dectecting ...")
    else:
        print("[INFOR]: Start offline dectecting ...")
    
    while True:
        #Alcolho detection
        my_input=wiringpi.digitalRead(25)
        if(my_input):
         pass
        else:
         count=count+1
        if count == 5:
         sendTime = str(datetime.now())
         print("[DETECTION INFOR]: Alcohol Detected")
         if connect:
             SOCKET.sendToDjango('Alcohol Detected', sendTime, ws)
         count = 0
        
<<<<<<< HEAD
        #Get frames
        frame = vs.read()
        COUNT_FRAME = COUNT_FRAME + 1
        frame = imutils.resize(frame, width=300)
        GENERAL_VIDEO.writeFrames(frame)
        (h, w) = frame.shape[:2]
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
                    writterDrowsiness.writeFrames(frame)
                if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                    print('[DETECTION INFOR]: DROWSINESS DETECTED !')
                    if connect:
                        SOCKET.sendToDjango('Drowsiness', sendTime, ws)
                    writterDrowsiness.releaseVideo()
=======
        while True:
            frame = vs.read()
            frame = cv2.resize(frame, (720, 480))
            GENERAL_VIDEO.writeFrames(frame)
            COUNT_FRAME = COUNT_FRAME + 1

            frame = imutils.resize(frame, width=300)
            (h, w) = frame.shape[:2]
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
                        cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                        cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
                        FRAME_COUNT_EAR += 1
                        writterDrowsiness = VideoActivity('media/detail/drowsiness/drowsiness' + saveTime + '.avi')

                    else:
                        FRAME_COUNT_EAR += 1
                        frame = cv2.resize(frame, (720, 480))
                        writterDrowsiness.writeFrames(frame)

                    if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                        print("DROWSINESS")
                        SOCKET.sendToDjango('Pi 1', 'drowsiness', sendTime, ws)
                        FRAME_COUNT_EAR = 0
                else:
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
                    FRAME_COUNT_EAR = 0
            else:
                FRAME_COUNT_EAR = 0

<<<<<<< HEAD
            if MAR > MAR_THRESHOLD:
                if FRAME_COUNT_MAR == 0:
                    saveTime, sendTime = DATETIME.getDateNameFormat()
                    writterYawning = VideoActivity('media/detail/yawning/yawning' + saveTime + '.avi')
                    FRAME_COUNT_MAR += 1
=======
                if MAR > MAR_THRESHOLD:
                    
                    if FRAME_COUNT_MAR == 0:
                        saveTime, sendTime = DATETIME.getDateNameFormat()
                        writterYawning = VideoActivity('media/detail/yawning/yawning' + saveTime + '.avi')
                        
                    FRAME_COUNT_MAR += 1
                    frame = cv2.resize(frame, (720, 480))
                    writterYawning.writeFrames(frame)    
                      
                    if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES:
                        writterYawning.releaseVideo()
                        print("YOU ARE YAWNING")
                        SOCKET.sendToDjango('Pi 1', 'yawning', sendTime, ws)
                        FRAME_COUNT_MAR = 0
                    
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
                else:
                    FRAME_COUNT_MAR += 1
                    writterYawning.writeFrames(frame)
                print(FRAME_COUNT_MAR)
                if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES_MOUTH:
                    print('[DETECTION INFOR]: YOU ARE YAWNING !')
                    if connect:
                        SOCKET.sendToDjango('Yawning', sendTime, ws)
                    writterYawning.releaseVideo()
                    FRAME_COUNT_MAR = 0
                
            else:
<<<<<<< HEAD
                FRAME_COUNT_MAR = 0

            FRAME_COUNT_DISTR = 0
        else:
            FRAME_COUNT_DISTR += 1

            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                print("[DETECTION INFOR]: NO EYES !")
            
        #Websocket connection detection
        FRAME_COUNT_CONNECT += 1
        if FRAME_COUNT_CONNECT >= 100:
            connect_websocket()
            
    GENERAL_VIDEO.releaseVideo()
    print("Thread terminating...")
    
    if connect:
=======
                FRAME_COUNT_DISTR += 1

                if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                    print("NO EYES")
                    # SOCKET.sendToDjango('Pi 1', 'No eyes detected', ws)

            if send:
                try:
                    ws.send(
                        json.dumps(
                            {
                                "command": "updateActive",
                                "name": DEVICES_NAME,
                                "time": str(datetime.now()),
                            }
                        )
                    )
                    send = False
                    lastActive = datetime.now()
                except Exception as e:
                    print(str(e))
                                
        GENERAL_VIDEO.releaseVideo()
        print("thread terminating...")
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
        ws.close()

if __name__ == "__main__":
<<<<<<< HEAD
    try:
        connect_websocket()
    except Exception as err:
        print("[INFOR]: " + err)
=======
    # url = 'ws://10.10.36.35:8000/ws/realtime/'
    url = 'ws://localhost:8000/ws/realtime/'
    # url = 'ws://localhost:8000/ws/realtimeData/'

    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
