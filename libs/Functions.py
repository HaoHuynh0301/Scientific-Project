# import the necessary packages
# from rasp4 import sendToDjango
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from imutils import build_montages
from datetime import datetime
from model.EAR_calculator import *
from imutils import face_utils
from matplotlib import style
import base64
import socket
import datetime as dt
import numpy as np
import argparse
import imutils
import cv2
import time
import json

def receive_requestcut_term(temp_start_time, temp_end_time):
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
        
def receive_requestcut(tmpDateTime, message):
    ResultStr = []
    cap = cv2.VideoCapture(message + tmpDateTime + '.avi')
    for frame in cap:
        frame = cv2.resize(frame, (720, 480))
        fframe = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
        ResultStr.append(fframe)
        
        
        
def delete_video(temp_FLAT, temp_size, temp_filepath):
    if temp_FLAT == 1:
        if temp_size >= 100:
            try:
                os.remove(temp_filepath)
                print('[INFOR]: Remove video successfully!!!')
            except Exception as e:
                print('[INFOR]: '+str(e))
    else:
        print('[INFOR]: Delete Unsuccessfully!!!')
        
def sendDjango(name, message, temp_ws):
    pp = json.dumps({
        "command": 'alert',
        'name': name,
        'time': str(datetime.now()),
        'activity': message,
    })
    try:
        temp_ws.send(pp)
    except Exception as e:
        print("[INFOR]: " + str(e))
        
def getDateName():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dt_string = dt_string.replace("/", "")
    dt_string = dt_string.replace(" ", "")
    dt_string = dt_string.replace(":", "")
    return dt_string
        
def cutVideo(name, start_time, end_time, temp_ws):
    pp = json.dumps({
        'name': name,
        'start_time': start_time,
        'end_time': end_time
    })
    try:
        temp_ws.send(pp)
    except Exception as e:
        print("[INFOR]: " + str(e))
        
        
        
