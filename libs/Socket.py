import json
import websocket
from datetime import datetime

class Socket:
    
    def __init__(self, ws):
        self.ws = ws
        
    def sendToDjango(self, name, message, senddatetime, temp_ws):
        pp = json.dumps({
            "command": 'alert',
            'name': name,
            # 'time': str(datetime.now()),
            'time': senddatetime,
            'activity': message,
        })
        try:
            temp_ws.send(pp)
        except Exception as e:
            print("[INFOR]: " + str(e))
        
    