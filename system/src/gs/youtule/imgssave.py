import cv2
import time
import os

print(cv2.__version__)
cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_FPS, 30)
if not cap.isOpened():
    print("Can't open camera")
    exit()

count = 0
output_folder = "output/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

while True:
    ret, frame = cap.read()
    if ret:
        print("Got a frame")
        print(time.time() * 1000)
        height, width, _ = frame.shape
        print(width)
        print(height)
        w = width // 3
        h = int(width * 72 / 128)
        out = frame[0:480, 0:w]
        res = cv2.resize(out, (1280, 720))

        # Split the image into four parts
        parts = []
        for i in range(0, 2):
            for j in range(0, 2):
                part = res[i * 360:(i + 1) * 360, j * 640 : (j + 1) * 640]
                part_resized = cv2.resize(part, (1280, 720))
                parts.append(part_resized)

        # Save first 60 frames to different folders
        if count < 60:
            for i in range(len(parts)):
                output_path = f"{output_folder}{i}/"
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                cv2.imwrite(f"{output_path}{count}.jpg", parts[i])

        count += 1
        cv2.imshow("frame", res)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
