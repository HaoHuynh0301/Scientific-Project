import json
import websocket
from datetime import datetime

class Socket:
    def __init__(self, ws):
        self.ws = ws
        
    def sendToDjango(self, message, senddatetime, temp_ws):
        pp = json.dumps({
            "command": 'alert',
            'name': message,
            'time': senddatetime,
        })
        try:
            temp_ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
            
    def generalSending(self, raspID, tmp_ws):
        pp = json.dumps({
            "command": 'getRoomCode',
            "id": raspID
        })
        try:
            tmp_ws.send(pp)
        except Exception as e:
            print(str(e))
            
    def virtualWebserver(self, time, activity, ws):
        pp = json.dumps({
            'command': 'getInfo',
            'time': time,
            'activity': activity
        })
        try:
            ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
    
