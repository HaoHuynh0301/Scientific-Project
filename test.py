import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import json
import socket

# Connect to Django Server
ws = websocket.WebSocket()
ws.connect('ws://localhost:8000/ws/realtimeData/')

try:
    pp = json.dumps({
    'name': "Pi 2",
    'time_start': 1,
    'time_end': 2,
    })
    ws.send(pp)
    
except Exception as e:
    print("[INFOR]: " + str(e))

        
