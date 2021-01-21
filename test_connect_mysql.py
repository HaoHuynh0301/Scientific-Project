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

# Connect to Mysql Server
try:
    cnx=mysql.connector.connect(user='root', password='hao152903', database='ras')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
    else:
        print(err)
else:
    print('Done')

add_status('Yawning', 'M01', 'X01', cnx)
