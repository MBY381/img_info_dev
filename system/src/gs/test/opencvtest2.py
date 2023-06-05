import cv2

print(cv2.__version__)
cap=cv2.VideoCapture("/dev/video0",cv2.CAP_V4L2)
if  not cap.isOpened():
	print("cant open camera")
	exit()


while True:
	ret , frame = cap .read()
	if ret:
		print("got a frame")
	print(ret)
	cv2.imshow("frame",cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY))
	if cv2.waitKey(1) & 0xFF== ord('q'):
		break

cap.release()
cv2.destroyAllWindows()