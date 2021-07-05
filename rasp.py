import websocket
import socket
import time
import json
import dlib
import cv2
import imutils
try:
    import thread
except ImportError:
    import _thread as thread
from model.EAR_calculator import *
from libs.videoutils import VideoUtils
from libs.datetime import DateTime
from libs.socket import Socket
from imutils import face_utils
from imutils.video import VideoStream
from datetime import datetime
from os import system, name
import signal
# import wiringpi as wiringpi

# Intialize files,raspberry infor, and folders
Datetime = DateTime()
HOSTNAME = socket.gethostname()
print(HOSTNAME)
IP_ADDRESS = '192.168.1.6'
# socket.gethostbyname(HOSTNAME)
RASPBERRY_ID = '1'
SERVER_ID = 'localhost:8000'
MODEL_PATH = 'model/custom_model_20_6_2021.dat'
JSON_PATH = 'data/RoomCode.json'
DROWSINESS_VIDEO_PATH = 'media/detail/drowsiness/drowsiness'
GENERAL_VIDEO_FILE_NAME = 'media/general/rasp_'
generalVideoPath = GENERAL_VIDEO_FILE_NAME + str(datetime.now()) + '.mp4'
generalVideo = VideoUtils(generalVideoPath)

# Opening JSON file, and return JSON data
f = open(JSON_PATH)
jsonData = json.load(f)
companyRoomCode = jsonData['roomCode']
f.close()

isGeneralRoomConnected = True
if companyRoomCode == 'general':
    isGeneralRoomConnected = False

# Intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print('[INFOR]: Loading the predictor ...')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)
vs = cv2.VideoCapture(0)
time.sleep(0.5)
print('[INFOR]: Predictor is ready!')

# MQ3 sensor intialize
# wiringpi.wiringPiSetupGpio()
# wiringpi.pinMode(25, 0)
sensorCount = 0
print('[INFOR]: MQ3 SENSOR is ready!')

# Ctrl-C pressed handle
def handlerSignal(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        generalVideo.releaseVideo()
        exit(1)
signal.signal(signal.SIGINT, handlerSignal)

def connectWebsocket(url):
    ws = websocket.WebSocketApp(url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
    
def requestDeterminedRoomCode(ws):
    SocketLocal = Socket(ws)
    SocketLocal.getDeterminedRoomCode(RASPBERRY_ID)    
    print('[WEBSOCKET INFOR]: No determined roomcode detected!')
    time.sleep(2.0)
    
def detecteAlert(vs, detector, predictor, sensorCount, ws, isConnected):
    # Intialize saving video path
    if isConnected:
        Socket = Socket(ws)
    generalVideo = VideoUtils(generalVideoPath)
    
    EAR_THRESHOLD = 0.2
    CONSECUTIVE_FRAMES = 100

    # Initialize two counters
    FRAME_COUNT_EAR = 0
    FRAME_COUNT_DISTR = 0
    
    # Websocket connecting detection
    RECONNECT_FRAME = 300
    reconnectFrameCount = 0
    
    if isConnected:
        print('[INFOR]: Start online dectecting ...')
    else:
        print('[INFOR]: Start offline dectecting ...')
        
    while True:
        # Alcolho detection
        # my_input=wiringpi.digitalRead(25)
        # if(my_input):
        #   pass
        # else:
        #  sensorCount += 1
        # if sensorCount == 5:
        #  sendTime = str(datetime.now())
        #  print('[DETECTION INFOR]: Alcohol Detected')
        #  if isConnected:
        #   Socket.sendAlertToServer('Alcohol Detected', sendTime)
        # sensorCount = 0
        # Try to connect to Webserver
        if not isConnected:
            reconnectFrameCount += 1
            if reconnectFrameCount >= RECONNECT_FRAME:
                connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
                
        #Get frames from camera      
        ret, frame = vs.read()
        frame = imutils.resize(frame, width=400)
        generalVideo.writeFrames(frame)
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
                    saveTime, sendTime = Datetime.getDateNameFormat()
                    drosinessVideoWritter = VideoUtils(DROWSINESS_VIDEO_PATH + saveTime + '.mp4')
                    FRAME_COUNT_EAR += 1
                else:
                    FRAME_COUNT_EAR += 1
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
                    drosinessVideoWritter.writeFrames(frame)
                if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                    print('[DETECTION INFOR]: DROWSINESS DETECTED !')
                    if isConnected:
                        Socket.sendAlertToServer('Drowsiness', sendTime)
                    drosinessVideoWritter.releaseVideo()
                    FRAME_COUNT_EAR = 0
            else:
                FRAME_COUNT_EAR = 0

            FRAME_COUNT_DISTR = 0
        else:
            FRAME_COUNT_DISTR += 1
            if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                pass
                # print('[DETECTION INFOR]: NO EYES !')
    if isConnected:
        ws.close()

def on_message(ws, message):
    # Load message data
    messageData = json.loads(message)

    # Get message when server wanna get drowsiness video
    if messageData.get('piDeviceID') == RASPBERRY_ID:
        alertTime = Datetime.getDateNameFormat2(messageData.get('time-occured'))
        VideoUtils = VideoUtils()
        frames = VideoUtils.getRequestVideo(alertTime, 'drowsiness')    
        for frame in frames:       
            try:
                ws.send(
                    json.dumps({
                        'command': 'sendImgToBrowser',
                        'messageType': 'sendImg',
                        'driveID': messageData.get('driveID'),
                        'frame': frame,
                        'time-happened': str(datetime.now())
                    })
                )
                time.sleep(0.5)
            except Exception as err:
                print('[INFOR]' + str(err))
    
    # Get determine roomCode  
    if messageData.get('command') == 'getRoomCode':
        if messageData.get('id') == RASPBERRY_ID:
            companyRoomCode = messageData.get('command')
            # Update roomCode JSON file
            f = open(JSON_PATH, 'w')
            JSON_DATA = {
                'roomCode': companyRoomCode
            }
            json.dump(JSON_DATA, f)
            f.close()
            isGeneralRoomConnected = True
            connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
        
def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print('[SOCKET INFORMATION]: Can not connect to Websocket ...')
    detecteAlert(vs, detector, predictor, sensorCount, ws, False)

def on_open(ws):
    def run(*args):
        print('[SOCKET INFORMATION]: Connect to Websocket ...')
        if isGeneralRoomConnected:
            detecteAlert(vs, detector, predictor, sensorCount, ws, True)
        else:
            requestDeterminedRoomCode(ws)
    thread.start_new_thread(run, ()) 
        
if __name__ == '__main__':
    try:
        connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
    except Exception as err:
        print('[WEBSOCKET INFOR]: ' + str(err))
        