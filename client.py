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
from imutils.video import VideoStream

SENCOND_SEND = 5
DEVICES_NAME = 'Pi 1'

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    # print(data['noti'])


def on_error(ws, error):
    # print(error)
    pass


def on_close(ws):
    print("### closed ###")


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

        server_ip = "192.168.123.210"
        sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
        rpiName = socket.gethostname()

        vs = VideoStream(usePiCamera=True).start()
        time.sleep(1.0)

        fps = 10

        size=(320, 240)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        result = cv2.VideoWriter('raspberrypi.avi', cv2.VideoWriter_fourcc('M','J','P','G'), fps, size)

        print("[INFOR]: Connecting to server")

        while True:
            try:
                frame = vs.read()
                result.write(frame)
                frame=cv2.resize(frame, (300, 200))
                #frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sender.send_image(rpiName, frame)
            except Exception as err:
                print("[INFOR]: "+str(err))

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
        # print("thread terminating...")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    url = 'ws://192.168.123.147:8000/ws/realtimeData/'
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()