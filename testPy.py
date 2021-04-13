from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2

# initialize the ImageHub object
imageHub = imagezmq.ImageHub()

while True:
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    cv2.imshow("Test", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
    		break


cv2.destroyAllWindows()