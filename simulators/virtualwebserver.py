import websocket
try:
    import thread
except ImportError:
    import _thread as thread
from libs.Socket import Socket
from datetime import datetime
from libs.Socket import *
import json

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    

def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        
        print("thread terminating...")


if __name__ == "__main__":
    url = 'ws://localhost:8000/ws/realtimeData/'

    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()