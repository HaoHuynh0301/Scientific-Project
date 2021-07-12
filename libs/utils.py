import json

class Utils:
    
    @staticmethod
    def getCompanyCode():
        JSON_PATH = 'data/RoomCode.json'
        isConnected = True
        f = open(JSON_PATH)
        jsonData = json.load(f)
        companyRoomCode = str(jsonData['roomCode'])
        f.close()
        if companyRoomCode == 'general':
            isConnected = False
        return isConnected, companyRoomCode