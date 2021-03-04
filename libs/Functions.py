# import the necessary packages
import mysql.connector
from mysql.connector import errorcode
# from rasp4 import sendToDjango
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
import base64
import socket
import datetime as dt
import numpy as np
import mysql
import dlib
import imagezmq
import argparse
import imutils
import cv2
import time
import os
import json

def receive_requestcut(temp_start_time, temp_end_time):
    list = []
    fframe = ""
    try:
        temp_video=VideoFileClip("raspberrypi.avi").subclip(temp_start_time, temp_end_time)
        n_frames = temp_video.reader.nframes
        for temp_video_frame in range(0, n_frames):
            frame = temp_video.get_frame(temp_video_frame)
            fframe = base64.b64encode(frame).decode('utf-8')
            list.append(fframe)
        print("[INFRO]: Cutting video successfully")
        return list
    except Exception as e:
        print('[INFOR]: ' + str(e))
        return e
        
def delete_video(temp_FLAT, temp_size, temp_filepath):
    if temp_FLAT==1:
        if temp_size>=100:
            try:
                os.remove(temp_filepath)
                print('[INFOR]: Remove video successfully!!!')
            except Exception as e:
                print('[INFOR]: '+str(e))
    else:
        print('[INFOR]: Delete Unsuccessfully!!!')
        
def sendDjango(name, message, temp_ws):
    pp = json.dumps({
        'name': name,
        'time': str(datetime.now()),
        'activity': message,
    })
    try:
        temp_ws.send(pp)
    except Exception as e:
        print("[INFOR]: " + str(e))
        
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
        
        
        
