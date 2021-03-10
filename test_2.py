import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
from imutils.video import VideoStream
from libs.Functions import *
from datetime import datetime
import json
import dlib
import cv2
import imutils
import random


def on_message(ws, message):
    data = json.loads(message)
    print(data)
def on_error(ws, error):
    # print(error)
    pass

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        try:
            pp = json.dumps({
            'name': "Pi 2",
            'time_start': 1,
            'time_end': 2,
            })
            ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
            
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