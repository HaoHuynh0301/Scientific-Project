import imutils
import imagezmq
import socket
import cv2
import time
from imutils.video import VideoStream

server_ip = "192.168.1.8"
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(server_ip))
rpiName = socket.gethostname()
# vs = VideoStream(src=0).start()
# time.sleep(1.0)

#define size for saving video
# Get current width of frame
frame_width = 680
frame_height = 480
fps = 15.0

video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
result = cv2.VideoWriter('test.mp4', fourcc, fps, size)

while True:
    ret, frame = video_capture.read()
    if ret==True:
        # print('Write Frame')
        # cv2.imshow("Frame", frame)
        result.write(frame)
        sender.send_image(rpiName, frame)
        key = cv2.waitKey (1) & 0xFF
        if key == ord("q"):
            break
    else:
        break

# video_capture.release()
result.release()
# do a bit of cleanup
cv2.destroyAllWindows()
