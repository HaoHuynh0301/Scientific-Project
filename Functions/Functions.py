# import the necessary packages
import mysql.connector
from mysql.connector import errorcode
# from rasp4 import sendToDjango
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from imutils import build_montages
from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
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

def receive_requestcut(temp_ip, temp_start_temp, temp_end_time):
    try:        
       ffmpeg_extract_subclip("raspberrypi.mp4", temp_start_temp, temp_end_time, targetname="aftercut.mp4")
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
        
        
