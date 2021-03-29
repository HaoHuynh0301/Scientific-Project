from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from imutils import build_montages
from imutils import face_utils
from matplotlib import style
import os
import base64
import socket
import imutils
import cv2
import time
import json

class VideoActivity:
    
    def __init__(self):
        super().__init__()
        
    def receive_requestcut_term(self, temp_start_time, temp_end_time):
        ResultStr = []
        try:
            temp_video = VideoFileClip("/Users/macos/Documents/Ras/raspberrypi.avi").subclip(temp_start_time, temp_end_time)
            n_frames = temp_video.reader.nframes
            for temp_video_frame in range(0, n_frames):
                fframe = ""
                frame = temp_video.get_frame(temp_video_frame)  
                frame = cv2.resize(frame, (720, 480))
                fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
                ResultStr.append(fframe)
                
            print("[INFRO]: Cutting video successfully")
            return fframe
        except Exception as e:
            print('[INFOR] Functions: ' + str(e))
            
    def receive_requestcut(self, tmpDateTime, message):
        ResultStr = []
        fframe = ""
        cap = cv2.VideoCapture("/Users/macos/Documents/ScientificProject/media/yawning24032021135136.avi")
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == False:
                break
            fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
            
        return fframe
    
    def delete_video(self, temp_FLAT, temp_size, temp_filepath):
        if temp_FLAT == 1:
            if temp_size >= 100:
                try:
                    os.remove(temp_filepath)
                    print('[INFOR]: Remove video successfully!!!')
                except Exception as e:
                    print('[INFOR]: '+str(e))
        else:
            print('[INFOR]: Delete Unsuccessfully!!!')