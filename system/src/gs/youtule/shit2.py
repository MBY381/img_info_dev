import cv2
import time

print(cv2.__version__)
cap=cv2.VideoCapture("/dev/video0",cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1440)
cap.set(cv2.CAP_PROP_FPS,30)
if  not cap.isOpened():
	print("cant open camera")
	exit()


while True:
	ret , frame = cap .read()
	if ret:
		print("got a frame")
		print(time.time()*1000)
	height,width,_=frame.shape
	print(width)
	print(height)
	w=width//3
	h=int(width*72/128)
	out=frame[0:480,0:w]
	res=cv2.resize(out,(1280,720))
	print(ret)
	cv2.imshow("frame",res)

	if cv2.waitKey(1) & 0xFF== ord('q'):
		break

cap.release()
cv2.destroyAllWindows()