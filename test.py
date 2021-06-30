import json

f = open('RoomCode.json')
updatedRoomCode = {
    'roomCode': 'hello'
}
json.dump(updatedRoomCode, f)