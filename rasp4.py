import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
from datetime import datetime
import json
import random

SENCOND_SEND = 5
DEVICES_NAME = 'Pi 1'

def on_message(ws, message):
    data = json.loads(message)
    # print(data['noti'])

def on_error(ws, error):
    # print(error)
    pass

def on_close(ws):
    f.close()
    print("### closed ###")

def on_open(ws):
    def run(*args):
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

        vs = VideoStream(usePiCamera=True).start() #usePiCamera=True
        time.sleep(1.0)

        count_sleep = 0
        count_yawn = 0

        print("[INFO]: Predictor is ready!")

        while True:
            frame = vs.read()
            cv2.putText(frame, str(COUNT_FRAME), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
            COUNT_FRAME=COUNT_FRAME+1
            cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)

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
            if key == ord("q"):
                break

        try:
            ws.send(
                json.dumps({
                    'name': DEVICES_NAME,
                    'time': str(lastActive),
                }))
            
        except Exception as e:
            print(str(e))

        while True:
            if datetime.now().minute - lastActive.minute >= 1:
                send = True

            else:
                if datetime.now().second - lastActive.second >= 2:
                    send = True

            if send:
                try:
                    ws.send(
                        json.dumps({
                            'name': DEVICES_NAME,
                            'time': str(datetime.now())
                        }))
                    send = False
                    lastActive = datetime.now()
                except Exception as e:
                    print(str(e))

        ws.close()
        # print("thread terminating...")
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