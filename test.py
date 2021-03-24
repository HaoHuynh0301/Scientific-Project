import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import json
import socket
from libs.Functions import *

# Connect to Django Server
ws = websocket.WebSocket()
# ws.connect('ws://10.10.34.158:8000/ws/realtime/')
ws.connect('ws://localhost:8000/ws/realtimeData/')
# ws.connect('ws://192.168.123.147:8000/ws/realtime/')

dateTime = getDateName()

try:
    pp = json.dumps({
    'command': "getInfo",
    'name': "Pi 2",
    'time': dateTime
    })
    ws.send(pp)
    ws.close()
    
except Exception as e:
    print("[INFOR]: " + str(e))

        
