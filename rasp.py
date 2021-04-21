import websocket
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
import time
import json
import dlib
import cv2
import imutils

DEVICES_NAME = 'Pi 1'
DATETIME = DateTime()
TMPDATETIME = ''
MODEL_PATH = 'model/custom_landmark_model.dat'
GENERAL_VIDEO_PATH = 'media/general/rasp' + DEVICES_NAME + '.avi'
SENCOND_SEND = 10

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    listFrame = []
    sendImage = False
    
    if data['command'] == 'getInfo':
        try:
            VIDEO_FUNCTION = VideoActivity()
            alertTime = DATETIME.getSendingDateNameFormat(data['time'])
            listFrame = VIDEO_FUNCTION.receiveRequestcut(alertTime, data['activity'])
            sendImage = True
        except Exception as e:
            print('[INFOR] Rasp1:'+ str(e))         
            
        if sendImage:       
            try:
                ws.send(
                    json.dumps({
                        'command': 'send_video',
                        'name': DEVICES_NAME,
                        'frames': listFrame#Use for frame in list_frame to display whole video
                    })
                )
                time.sleep(0.5)  

            except Exception as e:
                print("[INFOR]" + str(e))

def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        GENERAL_VIDEO = VideoActivity(GENERAL_VIDEO_PATH)
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

        # parameter
        distracton_initlized = False
        eye_initialized = False
        mouth_initialized = False

        EAR_THRESHOLD = 0.2

        MAR_THRESHOLD = 10

        CONSECUTIVE_FRAMES = 50
        CONSECUTIVE_FRAMES_MOUTH = 20

        # Initialize two counters
        BLINK_COUNT = 0
        FRAME_COUNT_EAR = 0
        FRAME_COUNT_MAR = 0
        FRAME_COUNT_DISTR = 0

        # Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
        print("[INFO]: Loading the predictor ...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(MODEL_PATH)

        vs = VideoStream(src=0, resolution=(1280, 720)).start() 
        # vs = cv2.VideoCapture(0)#usePiCamera=True
        time.sleep(0.5)
        count_sleep = 0
        count_yawn = 0

        print("[INFO]: Predictor is ready!")
        
        try:
            ws.send(
                json.dumps(
                    {
                        "command": "updateActive",
                        "name": DEVICES_NAME,
                        "time": str(lastActive),
                    }
                )
            )
        except Exception as e:
            print(str(e))

        if datetime.now().minute - lastActive.minute >= 1:
            send = True

        else:
            if datetime.now().second - lastActive.second >= 2:
                send = True
                
        Flag = False
        
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
                    FRAME_COUNT_EAR = 0

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
                    
                else:
                    FRAME_COUNT_MAR = 0

                FRAME_COUNT_DISTR = 0
            else:
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
        ws.close()
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    # url = 'ws://10.10.36.35:8000/ws/realtime/'
    url = 'ws://localhost:8000/ws/realtime/'
    # url = 'ws://localhost:8000/ws/realtimeData/'

    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()