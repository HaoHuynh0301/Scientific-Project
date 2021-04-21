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
        self.videoWritter.write(frame)
        
    def releaseVideo(self):
        self.videoWritter.release()
        
    def createVideo(self):
        fps = 10
        size = (720, 480)
        result = cv2.VideoWriter(self.videoPath, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
        return writter
    
    def receiveRequestcut(self, tmpDateTime, message):
        ResultStr = []
        fframe = ""
        cap = cv2.VideoCapture('/media/detail/'+ message + "/" + message + tmpDateTime + '.avi')
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            frame = cv2.resize(frame, (100, 100))
            fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
            ResultStr.append(fframe)
        return ResultStr
    
    def receiveRequestcutTerm(self, temp_start_time, temp_end_time):
        ResultStr = []
        try:
            temp_video = VideoFileClip("/Users/macos/Documents/Ras/raspberrypi.avi").subclip(temp_start_time, temp_end_time)
            n_frames = temp_video.reader.nframes
            for temp_video_frame in range(0, n_frames):
                fframe = ""
                frame = temp_video.get_frame(temp_video_frame)  
                fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
                ResultStr.append(fframe)
                
            print("[INFRO]: Cutting video successfully")
            return fframe
        except Exception as e:
            print('[INFOR] Functions: ' + str(e))
    
    def deleteVideo(self, temp_FLAT, temp_size, temp_filepath):
        if temp_FLAT == 1:
            if temp_size >= 100:
                try:
                    os.remove(temp_filepath)
                    print('[INFOR]: Remove video successfully!!!')
                except Exception as e:
                    print('[INFOR]: '+str(e))
        else:
            print('[INFOR]: Delete Unsuccessfully!!!')