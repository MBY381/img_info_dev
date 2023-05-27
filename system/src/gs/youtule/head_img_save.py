import cv2
import time
import os

output_folder = "output_head/"
print(cv2.__version__)
cap = cv2.VideoCapture("/dev/video5", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
cap.set(cv2.CAP_PROP_FPS, 30)
if not cap.isOpened():
    print("Can't open camera")
    exit()

count = 0
while True:
    ret, frame = cap.read()
    if ret:
        print("Got a frame")
        print(time.time() * 1000)
        height, width, _ = frame.shape
        print(height)
        print(width)

        w = width // 3
        h = int(width * 72 / 128)
        out = frame[0:240, 0:w]
        res = cv2.resize(out, (1280, 720))
        print(ret)
        cv2.imshow("frame", res)

        # Save first 60 frames to PNG format
        if count < 60:
            output_path = f"{output_folder}/{count}.png"
            cv2.imwrite(output_path, res)
            count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
