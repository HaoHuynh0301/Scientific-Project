# USAGE
# python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2

# import the necessary packages
import mysql.connector
from mysql.connector import errorcode
from connectmysql import *
# from rasp4 import sendToDjango
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

imageHub = imagezmq.ImageHub()
time.sleep(2)

while True:
    rpiName, frame = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    frame = imutils.resize(frame, width=400)
    cv2.putText(frame, "PRESS 'q' TO EXIT", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
    cv2.imshow("DEMO", frame)
    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
# do a bit of cleanup
cv2.destroyAllWindows()