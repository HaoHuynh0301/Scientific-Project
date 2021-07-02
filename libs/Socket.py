import json
import websocket
from datetime import datetime

class Socket:
    def __init__(self, ws):
        self.ws = ws
        
    def sendAlertToServer(self, message, senddatetime, temp_ws):
        pp = json.dumps({
            "command": 'alert',
            'name': message,
            'time': senddatetime,
        })
        try:
            temp_ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
            
    def getDeterminedRoomCode(self, raspId):
        pp = json.dumps({
            "command": 'getRoomCode',
            "id": raspId
        })
        try:
            self.ws.send(pp)
        except Exception as err:
            print(str(err))
            
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
    
