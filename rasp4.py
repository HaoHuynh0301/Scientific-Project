import cv2
import datetime
import base64
import websocket
import json
import random

def sendToDjango(message):
    ws = websocket.WebSocket()
    ws.connect('ws://192.168.123.147:8000/ws/sendVideo/')

    pp = json.dumps({
        'imgByte': f'Xin chao {message}'
    })
    try:
        ws.send(pp)
    except Exception as e:
        print(str(e))
    

    