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
from os import system, name
# import wiringpi as wiringpi
from time import sleep
import time
import json
import dlib
import cv2
import imutils

# Intialize files, and folders
ID = "12"
HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)
SERVER_ID = "10.10.33.74"
MODEL_PATH = 'model/custom_model_20_6_2021.dat'
DATETIME = DateTime()
TMPDATETIME = ''

# Opening JSON file, and return JSON data
f = open('data/RoomCode.json')
JSON_DATA = json.load(f)
COMPANY_ROOM_CODE = JSON_DATA['roomCode']
f.close()

CONNECT_GENERAL_STATUS = True
if COMPANY_ROOM_CODE == 'general':
    CONNECT_GENERAL_STATUS = False

# Intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print("[INFOR]: Loading the predictor ...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)
vs = cv2.VideoCapture(0)
time.sleep(0.5)
print("[INFOR]: Predictor is ready!")

# MQ3 sensor intialize
# wiringpi.wiringPiSetupGpio()
# wiringpi.pinMode(25, 0)
count = 0
print("[INFOR]: MQ3 SENSOR is ready!")

def UnaddingOparation(ws, connect):
    if connect:
        SOCKET = Socket(ws)
        SOCKET.generalSending(ID, ws)    
    print("[WEBSOCKET INFOR]: No determine room code detected!")
    time.sleep(2.0)

def connect_websocket(url):
    print(CONNECT_GENERAL_STATUS)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def on_message(ws, message):
    # Load message data
    data = json.loads(message)
    print(data)
    listFrame = []
    
    # Get message when server wanna get drowsiness video
    if data.get('piDeviceID')== ID:
        alertTime = DATETIME.getDateNameFormat2(data['time-occured'])
        VIDEO_FUNCTION = VideoActivity()
        frames = VIDEO_FUNCTION.receiveRequestcut(alertTime, 'drowsiness')    
        for frame in frames:       
            try:
                ws.send(
                    json.dumps({
                        'command': 'sendImgToBrowser',
                        'messageType': 'sendImg',
                        'driveID': data["driveID"],
                        'frame': frame,
                        'time-happened': str(datetime.now())
                    })
                )
                time.sleep(0.5)
            except Exception as e:
                print("[INFOR]" + str(e))
    
    # Get determine roomCode  
    if data.get('command') == 'getRoomCode':
        if data["id"] == ID:
            COMPANY_ROOM_CODE = data.get('command')
            # Update roomCode JSON file
            f = open('data/RoomCode.json', 'w')
            JSON_DATA = {
                'roomCode': COMPANY_ROOM_CODE
            }
            json.dump(JSON_DATA, f)
            f.close()
            CONNECT_GENERAL_STATUS = True
            connect_websocket(f"ws://2a3b6495b1e4.ngrok.io/ws/realtime/{COMPANY_ROOM_CODE}/{ID}/")
        
def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print("[SOCKET INFORMATION]: Can not connect to Websocket ...")
    detecteOparation(vs, detector, predictor, count, ws, False)

def on_open(ws):
    def run(*args):
        
        print("[SOCKET INFORMATION]: Connect to Websocket ...")
        if CONNECT_GENERAL_STATUS:
            detecteOparation(vs, detector, predictor, count, ws, True)
        else:
            UnaddingOparation(ws, True)
    thread.start_new_thread(run, ()) 

def detecteOparation(vs, detector, predictor, count, ws, connect):
    # Intialize saving video path
    GENERAL_VIDEO_PATH = 'media/general/rasp_' + str(datetime.now()) + "_connected.mp4"
    if connect:
        GENERAL_VIDEO_PATH = 'media/general/rasp_' + str(datetime.now()) + "_disconnected.mp4"
        SOCKET = Socket(ws)

    GENERAL_VIDEO = VideoActivity(GENERAL_VIDEO_PATH)
    EAR_THRESHOLD = 0.2
    CONSECUTIVE_FRAMES = 100

    # Initialize two counters
    FRAME_COUNT_EAR = 0
    FRAME_COUNT_DISTR = 0
    
    # Websocket connection detection
    FRAME_COUNT_CONNECT = 0
    
    if connect:
        print("[INFOR]: Start online dectecting ...")
    else:
        print("[INFOR]: Start offline dectecting ...")
    
    while True:
        # Alcolho detection
        # my_input=wiringpi.digitalRead(25)
        # if(my_input):
        #   pass
        # else:
        #  count=count+1
        # if count == 5:
        #  sendTime = str(datetime.now())
        #  print("[DETECTION INFOR]: Alcohol Detected")
        #  if connect:
        #   SOCKET.sendToDjango('Alcohol Detected', sendTime, ws)
        # count = 0
        # Try to connect to Webserver
        if connect == False:
            FRAME_COUNT_CONNECT += 1
            if FRAME_COUNT_CONNECT >= 300:
                connect_websocket(f"ws://2a3b6495b1e4.ngrok.io/ws/realtime/{COMPANY_ROOM_CODE}/{ID}/")
                
        #Get frames from camera      
        ret, frame = vs.read()
        frame = imutils.resize(frame, width=400)
        GENERAL_VIDEO.writeFrames(frame)
        (h, w) = frame.shape[:2]
        rects = detector(frame, 0)

        if len(rects) > 0:
            rect = get_max_area_rect(rects)
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            shape = predictor(frame, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[0:6]
            rightEye = shape[6:12]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            EAR = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if EAR < EAR_THRESHOLD:
                if FRAME_COUNT_EAR == 0:
                    saveTime, sendTime = DATETIME.getDateNameFormat()
                    writterDrowsiness = VideoActivity('media/detail/drowsiness/drowsiness' + saveTime + '.mp4')
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
                    FRAME_COUNT_EAR = 0
            else:
                FRAME_COUNT_EAR = 0

            FRAME_COUNT_DISTR = 0
        else:
            FRAME_COUNT_DISTR += 1
            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                pass
                # print("[DETECTION INFOR]: NO EYES !")
    GENERAL_VIDEO.releaseVideo()
    print("Thread terminating...")
    
    if connect:
        ws.close()
        
if __name__ == "__main__":
    try:
        connect_websocket(f"ws://2a3b6495b1e4.ngrok.io/ws/realtime/{COMPANY_ROOM_CODE}/{ID}/")
    except Exception as err:
        print("[WEBSOCKET INFOR]: " + str(err))

