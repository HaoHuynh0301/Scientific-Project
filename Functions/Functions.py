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

def receive_requestcut(temp_start_temp, temp_end_time):
    server_ip = "192.168.123.212" #Your IPServer
    sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
    rpiName = socket.gethostname()
    
    try:
        temp_video=VideoFileClip("raspberrypi.mp4").subclip(temp_start_temp, temp_end_time)
        temp_video=temp_video.to_RGB()
        n_frames = temp_video.reader.nframes
        print(type(temp_video))
        for temp_video_frame in range(0, n_frames):
            frame=temp_video.get_frame(temp_video_frame)
            sender.send_image(rpiName, frame)
            
    except Exception as e:
        print('[INFOR]: '+str(e))
        
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
        'message': message,
    })
    try:
        temp_ws.send(pp)
    except Exception as e:
        print("[INFOR]: " + str(e))
        
# Add the frame to the dataset ar a proof of drowsy driving
                    # pp = json.dumps({
                    #     'name': 'Pi 1',
                    #     'time': str(datetime.now()),
                    #     'message': 'Yawning',
                    # })
                    # try:
                    #     ws.send(pp)
                    # except Exception as e:
                    #     print(str(e), 'loi cua tui')
        
        
