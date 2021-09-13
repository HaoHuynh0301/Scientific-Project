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

# Intialize files,raspberry infor, and folders
Datetime = DateTime()
HOSTNAME = socket.gethostname()
IP_ADDRESS = socket.gethostbyname(HOSTNAME)
RASPBERRY_ID = 17
# http://0dd9113bd398.ngrok.io/
SERVER_ID = '127.0.0.1:8000'
MODEL_PATH = 'model/custom_model_20_6_2021.dat'
JSON_PATH = 'data/RoomCode.json'
DROWSINESS_VIDEO_PATH = 'media/detail/drowsiness/drowsiness'
NOEYES_VIDEO_PATH = 'media/detail/noeye/noeye'
GENERAL_VIDEO_FILE_NAME = 'media/general/rasp_'
generalVideoPath = GENERAL_VIDEO_FILE_NAME + str(datetime.now()) + '.mp4'
generalVideo = VideoUtils(generalVideoPath)

# Opening JSON file, and return JSON data
companyRoomCode = 'general'

# Intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
print('[INFOR]: Loading the predictor ...')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)
vs = cv2.VideoCapture(0)
print('[INFOR]: Predictor is ready!')

# MQ3 sensor intialize
# wiringpi.wiringPiSetupGpio()
# wiringpi.pinMode(25, 0)
sensorCount = 0
print('[INFOR]: MQ3 SENSOR is ready!')

# Ctrl-C pressed handle
def handlerSignal(signum, frame):
    res = input('Ctrl-c was pressed. Do you really want to exit? y/n ')
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
    time.sleep(0.5)
    
def detecteAlert(**kwargs):
    # Intialize saving video path
    if kwargs['isConnected']:
        SocketLocal = Socket(kwargs['ws'])
    
    EAR_THRESHOLD = 0.2
    CONSECUTIVE_FRAMES = 20
    NOEYES_FRAMES = 20

    # Initialize two counters
    FRAME_COUNT_EAR = 0
    FRAME_COUNT_DISTR = 0
    
    # Websocket connecting detection
    RECONNECT_FRAME = 50
    reconnectFrameCount = 0
    
    drowsinessReleaseContext = {
        'isCreated': 'False',
        'videoPath': ''
    }
    
    noeyesReleaseContext = {
        'isCreated': 'False',
        'videoPath': ''
    }
    
    if kwargs['isConnected']:
        print('[INFOR]: Start online dectecting ...')
    else:
        print('[INFOR]: Start offline dectecting ...')
    
    while True:
        time.sleep(0.2)
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
        #   Socket.sendAlertToServer('Alcohol', sendTime)
        # sensorCount = 0
        # Try to connect to Webserver
        if not kwargs['isConnected']:
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
                    drowsinessReleaseContext['isCreated'] = 'True'
                    drowsinessReleaseContext['videoPath'] = str(drosinessVideoWritter.videoPath)
                else:
                    FRAME_COUNT_EAR += 1
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
                    drosinessVideoWritter.writeFrames(frame)
                if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:  
                    print('[DETECTION INFOR]: DROWSINESS DETECTED !')

                    # Play Music on Separate Thread (in background)  
                    soundThread = SoundThread()
                    t = threading.Thread(target = soundThread.playSound)
                    t.start()
                    
                    if kwargs['isConnected']:
                        print("Connect")
                        SocketLocal.sendAlertToServer('Drowsiness', sendTime)
                    drosinessVideoWritter.releaseVideo()
                    FRAME_COUNT_EAR = 0
                    Utils.setReleaseContext(drowsinessReleaseContext, 'False')
            else:
                if drowsinessReleaseContext['isCreated'] == 'True':
                    VideoUtils.deleteVideoWritter(drowsinessReleaseContext['videoPath'])
                    Utils.setReleaseContext(drowsinessReleaseContext, 'False')
                FRAME_COUNT_EAR = 0

            FRAME_COUNT_DISTR = 0
            if noeyesReleaseContext['isCreated'] == 'True':
                VideoUtils.deleteVideoWritter(noeyesReleaseContext['videoPath'])
                Utils.setReleaseContext(noeyesReleaseContext, 'False')
                
        else:
            if FRAME_COUNT_DISTR == 0:
                saveTime, sendTime = Datetime.getDateNameFormat()
                noeyesVideoWritter = VideoUtils(NOEYES_VIDEO_PATH + saveTime + '.mp4')
                FRAME_COUNT_DISTR += 1
                noeyesReleaseContext['isCreated'] = 'True'
                noeyesReleaseContext['videoPath'] = str(noeyesVideoWritter.videoPath)
            else:
                FRAME_COUNT_DISTR += 1
                noeyesVideoWritter.writeFrames(frame)
            if FRAME_COUNT_DISTR >= NOEYES_FRAMES:
                FRAME_COUNT_DISTR = 0
                print('[DETECTION INFOR]: NO EYES !')
                if kwargs['isConnected']:
                    print("Connect")
                    SocketLocal.sendAlertToServer('Noeye', sendTime)
                
                # Play Music on Separate Thread (in background)  
                soundThread = SoundThread()
                t = threading.Thread(target = soundThread.playSound)
                t.start()

                noeyesVideoWritter.releaseVideo()
                Utils.setReleaseContext(noeyesReleaseContext, 'False')
                        
    if kwargs['isConnected']:
        kwargs['ws'].close()

def on_message(ws, message):
    # Load message data
    messageData = json.loads(message)
    print(messageData)
    
    # Get message when server wanna get drowsiness video
    if messageData.get('piDeviceID') == str(RASPBERRY_ID):
        alertTime = Datetime.getDateNameFormat2(messageData['time-occured'])
        alertType = messageData['alertType'].lower()
        print(alertType)
        try:
            frames = VideoUtils.getRequestVideo(alertTime, alertType)    
        except Exception as err:
            print(str(err))
        for frame in frames:       
            try:
                ws.send(
                    json.dumps({
                        'command': 'sendImgToBrowser',
                        'messageType': 'sendImg',
                        'driveID': messageData['driveID'],
                        'frame': frame,
                        'time-happened': str(datetime.now())
                    })
                )
                time.sleep(0.5)
            except Exception as err:
                print('[INFOR]' + str(err))
    
    # Get determine roomCode  
    if int(messageData['piDeviceID']) == RASPBERRY_ID:
        if messageData.get('command') == 'getRoomCode': #messageData.get('command') == 'getRoomCode'
            print('GET MESSAGE')
            # Update roomCode JSON fil
            # ws.close()
            companyRoomCode = messageData['roomCode']
            time.sleep(2.0)
            try:
                connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
            except Exception as err:
                print('[WEBSOCKET INFOR]: ' + str(err))
        
def on_error(ws, error):
    print('[SOCKET ERROR]: ' + error)

def on_close(ws):
    print('[SOCKET INFORMATION]: Can not connect to Websocket ...')
    detecteAlert(vs = vs, 
                detector = detector, 
                predictor = predictor, 
                sensorCount = sensorCount,
                ws = ws, 
                isConnected = False)

def on_open(ws):
    def run(*args):
        print('[SOCKET INFORMATION]: Connect to Websocket ...')
        if companyRoomCode == 'general':
            requestDeterminedRoomCode(ws)
            detecteAlert(vs = vs, 
                        detector = detector, 
                        predictor = predictor, 
                        sensorCount = sensorCount,
                        ws = ws, 
                        isConnected = True)     
        else:
            detecteAlert(vs = vs, 
                        detector = detector, 
                        predictor = predictor, 
                        sensorCount = sensorCount,
                        ws = ws, 
                        isConnected = True)  
    thread.start_new_thread(run, ()) 
        
if __name__ == '__main__':
    try:
        print(companyRoomCode)
        connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
    except Exception as err:
        print('[WEBSOCKET INFOR]: ' + str(err))
        