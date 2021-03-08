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
from Functions import receive_requestcut
from imutils.video import VideoStream

# Connect to Django Server
ws = websocket.WebSocket()
ws.connect('ws://localhost:8000/ws/realtimeData/')

pp = json.dumps({
    'name': "Pi 2",
    'time_start': 1,
    'time_end': 3,
})
try:
    ws.send(pp)
except Exception as e:
    print("[INFOR]: " + str(e))

        
