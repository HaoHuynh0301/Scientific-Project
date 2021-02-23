import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
from datetime import datetime
import json
import random
import imutils
import imagezmq
import socket
import cv2
import Functions
from functions import receive_requestcut
from imutils.video import VideoStream

SENCOND_SEND = 5
DEVICES_NAME = 'Pi 1'
SENDING_CODE = 'NCMHAHA'

def on_message(ws, message):
    data = json.loads(message)
    send =  False
    print(data)
    if data['name'] == DEVICES_NAME:
        try:
            list_frame = receive_requestcut(data['time_start'], data['time_end'])
            send = True
        except Exception as e:
            print('[INFOR]: '+ str(e))
        if send:
            ws.send(
                json.dumps({
                    'name': DEVICES_NAME,
                    'sending_code': SENDING_CODE,
                    'list_frames': list_frame
                })
            )
        
def on_error(ws, error):
    print("[INFOR]: " + str(error))


def on_close(ws):
    print("[INFOR]: Closed")


def on_open(ws):
    def run(*args):
        lastActive = datetime.now()
        send = False

        try:
            ws.send(
                json.dumps({
                    'name': DEVICES_NAME,
                    'activeTime': str(lastActive),
                }))
        except Exception as e:
            print(str(e))

        server_ip = "localhost" #replace with your server's IP
        sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
        rpiName = socket.gethostname()
        vs = VideoStream(src=0).start() #PiCamera=True
        time.sleep(1.0)
        
        #Save video while streaming
        fps = 15.0
        size=(1280, 720)
        result = cv2.VideoWriter('raspberrypi.avi', cv2.VideoWriter_fourcc('M','J','P','G'), fps, size)

        while True:
            try:
                frame = vs.read()
                result.write(frame)
                frame=cv2.resize(frame, (720, 480))
                sender.send_image(rpiName, frame)
            except Exception as err:
                print("[INFOR]: " + str(err))

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
                            'activeTime': str(datetime.now())
                        }))
                    send = False
                    lastActive = datetime.now()
                except Exception as e:
                    print(str(e))

        ws.close()

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    url = 'ws://192.168.123.147:8000/ws/realtimeData/'
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()