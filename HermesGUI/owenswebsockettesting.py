import json
import pprint
import websocket
from websocket import create_connection
import _thread
import time

websocket.enableTrace(True)
ws = create_connection("ws://192.168.43.1:8001")

result = ws.recv()
print('Result: {}'.format(result))


# Define WebSocket callback functions
def ws_message(ws, message):
    data = json.loads(message)
    #robotPose.update(data['xx'], data['yy'])
    print("target x ", data['tx'], " target y ", data['ty'], " target a ", data['th'])
    print("actual x ", data['ax'], " actual y ", data['ay'], " actual a ", data['ah'])
    ws.keep_running = True

def ws_open(ws):
    print("connecting...")
    #ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XBT/USD","XRP/USD"]}')

def ws_thread(*args):
    global ws
    ws = websocket.WebSocketApp("ws://192.168.43.1:8001", on_open = ws_open, on_message = ws_message)
    ws.run_forever()
    ws.keep_running = True

# Start a new thread for the WebSocket interface
_thread.start_new_thread(ws_thread, ())

# Continue other (non WebSocket) tasks in the main thread
while True:
    time.sleep(.5)
    #print("Main thread: %d" % time.time())