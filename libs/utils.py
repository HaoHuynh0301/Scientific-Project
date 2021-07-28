import json
from playsound import playsound
from threading import Thread
import atexit
import time 
import threading

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
    
    @staticmethod
    def setReleaseContext(context, isCreated):
        context['isCreated'] = isCreated
        context['videoPath'] = ''
    
class SoundThread:
    def startMusic(self):
        i = 0
        @atexit.register
        def goodbye():
            print ("'CLEANLY' kill sub-thread with value: %s [THREAD: %s]" %
                (i, threading.currentThread().ident))
        while True:
            i += 1
            time.sleep(1)
            
    def afterTimeout(self):
        print("KILL MAIN THREAD: %s" % threading.currentThread().ident)
        raise SystemExit
    
    def playSound(self):
        playsound('media/sound/sound-alert-[AudioTrimmer.com]-[AudioTrimmer.com].mp3')