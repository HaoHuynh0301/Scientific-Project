import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
from imutils.video import VideoStream
from Functions import *
from datetime import datetime
import json
import dlib
import cv2
import imutils
import random
import getch


SENCOND_SEND = 5
DEVICES_NAME = 'Pi 1'

def on_message(ws, message):
    data = json.loads(message)
    # print(data)
    send =  False
    #name, start, end
    if data['name'] == 'Pi 2':
        try:
            list_frame = receive_requestcut(data['time_start'], data['time_end'])
            send = True
        except Exception as e:
            print('[INFOR]: '+ str(e))
        if send:
            try:
                ws.send(
                    json.dumps({
                        'name': DEVICES_NAME,
                        'sending_code': "SENDING_CODE",
                        'list_frames': list_frame#Use for frame in list_frame to display whole video
                    })
                )
            except Exception as e:
                print("[INFOR]: " + str(e))

def on_error(ws, error):
    # print(error)
    pass

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        lastActive = datetime.now()
        # send = False
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

        CONSECUTIVE_FRAMES = 20
        CONSECUTIVE_FRAMES_MOUTH = 20
        model_path = 'model/custom_landmark_model.dat'

        # Initialize two counters
        BLINK_COUNT = 0
        FRAME_COUNT_EAR = 0
        FRAME_COUNT_MAR = 0
        FRAME_COUNT_DISTR = 0

        # Now, intialize the dlib's face detector model as 'detector' and the landmark predictor model as 'predictor'
        print("[INFO]: Loading the predictor ...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(model_path)

        vs = VideoStream(src=0, resolution=(1280, 720)).start() 
        # vs = cv2.VideoCapture(0)#usePiCamera=True
        time.sleep(1.0)
        count_sleep = 0
        count_yawn = 0

        print("[INFO]: Predictor is ready!")
        
        fps = 10
        size = (1280, 720) 
        #result = cv2.VideoWriter('raspberrypi.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, size)
        result = cv2.VideoWriter('raspberrypi.avi', cv2.VideoWriter_fourcc('M','J','P','G'), fps, size)
        Flag = False
        while Flag == False:
            frame = vs.read()
            # frame = cv2.resize(frame, (1280, 720))
            result.write(frame)
            COUNT_FRAME=COUNT_FRAME+1

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
                    FRAME_COUNT_EAR += 1
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)
                    if FRAME_COUNT_EAR >= CONSECUTIVE_FRAMES:
                        # sendDjango('Pi 1', 'Drowsiness', ws)
                        FRAME_COUNT_EAR = 0
                else:
                    FRAME_COUNT_EAR = 0

                if MAR > MAR_THRESHOLD:
                    FRAME_COUNT_MAR += 1
                    cv2.drawContours(frame, [mouth], -1, (0, 0, 255), 1)
                    if FRAME_COUNT_MAR >= CONSECUTIVE_FRAMES:
                        print("YOU ARE YAWNING")
                        Flag = True
                        # sendDjango('Pi 1', 'Yawning', ws)
                        FRAME_COUNT_MAR = 0
                else:
                    FRAME_COUNT_MAR = 0

                FRAME_COUNT_DISTR = 0
            else:
                FRAME_COUNT_DISTR += 1

                if FRAME_COUNT_DISTR >= CONSECUTIVE_FRAMES:
                    print("No eyes")
                    # sendDjango('Pi 1', 'No eyes detected', ws)

            try:
                ws.send(
                    json.dumps({
                        'name': DEVICES_NAME,
                        'time': str(lastActive),
                    }))
            except Exception as e:
                print(str(e))

            # while True:
            #     if datetime.now().minute - lastActive.minute >= 1:
            #         send = True

            #     else:
            #         if datetime.now().second - lastActive.second >= 2:
            #             send = True

            #     if send:
            #         try:
            #             ws.send(
            #                 json.dumps({
            #                     'name': DEVICES_NAME,
            #                     'time': str(datetime.now())
            #                 }))
            #             send = False
            #             lastActive = datetime.now()
            #         except Exception as e:
            #             print(str(e))   
                        
        result.release()
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    # websocket.enableTrace(True)
    # url = 'ws://localhost:8000/ws/realtimeData/'
    url = 'ws://localhost:8000/ws/realtimeData/'


    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()