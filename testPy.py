from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2
import os

cap = cv2.VideoCapture('/Users/macos/Documents/Scientific-Project/media/detail/yawning20210420131000746252.avi')

if (cap.isOpened() == False):
    print("Error opening video stream or file")

while(cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow("Test", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
    	break

cv2.destroyAllWindows()