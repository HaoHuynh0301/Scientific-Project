from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from imutils import build_montages
from imutils import face_utils
from imutils.video import VideoStream
import os
import base64
import imutils
import cv2
import time
import json

class VideoUtils:
    def __init__(self, path=None):
        super().__init__()
        if(path):
            self.videoPath = path
            self.videoWritter = self.createVideo()
            
    def writeFrames(self, frame):
        frame = cv2.resize(frame, (225,320))
        self.videoWritter.write(frame)
        
    def releaseVideo(self):
        self.videoWritter.release()
        
    def createVideo(self):
        fps = 30.0
        size = (225,320)
        writter = cv2.VideoWriter(self.videoPath, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
        return writter
    
    @staticmethod
    def deleteVideoWritter(videoPath):
        os.remove(videoPath)
    
    @staticmethod
    def getRequestVideo(tmpDateTime, message):
        frames = []
        cap = cv2.VideoCapture("media/detail/" + message + "/" + message + tmpDateTime + ".avi") 
        sendingFrameCount = 0     
        while(cap.isOpened()):
            sendingFrameCount += 1
            if sendingFrameCount == 4: break
            ret, frame = cap.read()
            if ret == False:
                break
            frame = cv2.resize(frame, (640, 464))
            fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
            frames.append(fframe)
        return frames
