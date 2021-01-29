import imutils
import imagezmq
import socket
import cv2
import time
import Functions
from filecheck import FileCheck
from imutils.video import VideoStream


server_ip = "192.168.1.24"
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
rpiName = socket.gethostname()
vs = VideoStream(src=0, resolution=(1280, 720), frame=30.0).start()
# time.sleep(1.0)

#define size for saving video
# Get current width of frame
fps = 15.0

size=(1280, 720)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
result = cv2.VideoWriter('raspberrypi.mp4', fourcc, fps, size)

while True:
    try:
        frame = vs.read()
        result.write(frame)
        sender.send_image(rpiName, frame)
    except Exception as err:
        print("[INFOR]: "+str(err))

vs.release()
result.release()

#Delete video if it is larger than 100GB
filevideo_path='raspberrypi.mp4'
videocheck=FileCheck(filevideo_path)
size_video, FLAG=videocheck.get_filesize()
Functions.delete_video(FLAG, size_video, filevideo_path)

# do a bit of cleanup
cv2.destroyAllWindows()
