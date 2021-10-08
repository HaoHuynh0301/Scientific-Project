import json
import websocket
from datetime import datetime

class Socket:
    def __init__(self, ws):
        self.ws = ws
        
    def sendAlertToServer(self, message, sendDateTime):
        pp = json.dumps({
            "command": 'alert',
            'name': message,
            'time': sendDateTime,
        })
        print(self.ws)
        try:
            self.ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
            
    def getDeterminedRoomCode(self, raspId):
        pp = json.dumps({
            "command": 'getRoomCode',
            "piDeviceID": raspId
        })
        try:
            self.ws.send(pp)
        except Exception as err:
            print(str(err))
            
    
