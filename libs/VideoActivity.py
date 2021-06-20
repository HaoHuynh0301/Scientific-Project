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

class VideoActivity:
    
    def __init__(self, path=None):
        super().__init__()
        if(path):
            self.videoPath = path
            self.videoWritter = self.createVideo()
            
    def writeFrames(self, frame):
        frame = cv2.resize(frame, (225,300))
        self.videoWritter.write(frame)
        
    def releaseVideo(self):
        self.videoWritter.release()
        
    def createVideo(self):
<<<<<<< HEAD
        fps = 10.0
        size = (225,300)
        writter = cv2.VideoWriter(self.videoPath, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
=======
        fps = 10
        size = (720, 480)
        result = cv2.VideoWriter(self.videoPath, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
        return writter
    
    def receiveRequestcut(self, tmpDateTime, message):
        ResultStr = []
        fframe = ""
<<<<<<< HEAD
        cap = cv2.VideoCapture("media/detail/" + message + "/" + message + tmpDateTime + ".avi")      
=======
        cap = cv2.VideoCapture('/media/detail/'+ message + "/" + message + tmpDateTime + '.avi')
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            frame = cv2.resize(frame, (640, 464))
            fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
            ResultStr.append(fframe)
        return ResultStr
