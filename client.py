from imutils.video import VideoStream
import sys
import numpy as np
import cv2
import argparse
import imagezmq
import socket
import time
import PIL
import numpy as np
from numpy import asarray
from matplotlib import image
from matplotlib import pyplot
from PIL import Image

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-s", "--server-ip", required=True,
# 	help="ip address of the server to which the client will connect")
# args = vars(ap.parse_args())
# # initialize the ImageSender object with the socket address of the
# # server
# sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
# 	args["server_ip"]))

# rpiName = socket.gethostname ()
# vs = VideoStream (src = 0).start ()
# # vs = VideoStream(src=0).start()
# time.sleep (2.0)

# while True:
#     # read the frame from the camera and send it to the server
#     frame = vs.read ()
#     sender.send_image (rpiName, frame)

#Convert image into nparray
image = Image.open('/Users/macos/Downloads/125963723_710602699579378_2583582351400280391_o.jpg')
# convert image to numpy array
data = asarray(image)

sender = imagezmq.ImageSender()
image_window_name = 'From Sender'
while True:  # press Ctrl-C to stop image sending program
    # Increment a counter and print it's value to console
    print('Sending')
    # Add counter value to the image and send it to the queue
    sender.send_image(image_window_name, data)
    time.sleep(1)