import websocket
try:
    import thread
except ImportError:
    import _thread as thread
from datetime import datetime
import json
import time

RASPBERRY_ID = '12'
SERVER_ID = 'localhost:8000'
companyRoomCode = 'general'

def connectWebsocket(url):
    ws = websocket.WebSocketApp(url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    
def on_error(ws, error):
    print('[Socket Error]: ' + error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        try:
            ws.send(
                json.dumps({
                   'command': 'getRoomCode',
                   'id': '12',
                   'roomCode': 'lsRHGGT111'
                })
            )
            time.sleep(0.5)
        except Exception as err:
            print('[INFOR]' + str(err))
        print("thread terminating...")
        
if __name__ == '__main__':
    try:
        connectWebsocket(f'ws://{SERVER_ID}/ws/realtime/{companyRoomCode}/{RASPBERRY_ID}/')
    except Exception as err:
        print('[WEBSOCKET INFOR]: ' + str(err))