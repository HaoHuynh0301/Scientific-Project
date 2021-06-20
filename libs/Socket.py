import json
import websocket
from datetime import datetime

class Socket:
    
    def __init__(self, ws):
        self.ws = ws
        
    def sendToDjango(self, message, senddatetime, temp_ws):
        pp = json.dumps({
            "command": 'alert',
            'time': senddatetime,
            'name': message,
        })
        try:
            temp_ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
            
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
    
