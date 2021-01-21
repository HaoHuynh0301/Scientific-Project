import imutils
import imagezmq
import socket
import cv2
import time
from imutils.video import VideoStream

server_ip = "192.168.1.11"
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()
time.sleep(1.0)

while True:
 frame = vs.read()
 sender.send_image(rpiName, frame)