#import mysql.connector
#from mysql.connector import errorcode
#from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
#from rasp4 import *
from Functions.Functions import *
from imutils import build_montages
# from EAR_calculator import *
from imutils import face_utils
from matplotlib import style
from datetime import datetime
import datetime as dt
import numpy as np
import mysql
import dlib
# from filecheck import FileCheck, receive_requestcut
import imagezmq
import argparse
import imutils
import cv2
import time

receive_requestcut("raspberrypi.mp4", 0, 7)
