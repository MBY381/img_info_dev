import cv2
import time

print(cv2.__version__)
cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_FPS, 30)
if not cap.isOpened():
    print("cant open camera")
    exit()

while True:
    ret, frame = cap.read()
    if ret:
        print("got a frame")
        print(time.time() * 1000)
        height, width, _ = frame.shape
        print(width)
        print(height)
        w = width // 3
        h = int(width * 72 / 128)
        out = frame[0:480, 0:w]
        res = cv2.resize(out, (1280, 720))

        # 对裁切后的4份图像分别进行大小调整并分别输出视频流
        resize_ratio = 720 / h
        h_mid = int(height / 2)
        w_mid = int(width / 2)
        crop_h = int(h * resize_ratio / 2 + 0.5)  # 加0.5保证得到最近的整数
        crop_w = int(w * resize_ratio / 2 + 0.5)

        for i in range(2):
            for j in range(2):
                cropped_image = frame[(i * h_mid) + crop_h:(i * h_mid) + (h * resize_ratio) - crop_h + 1,  # 加1保证取到右下角
                                (j * w_mid) + crop_w:(j * w_mid) + (w * resize_ratio) - crop_w + 1]  # 加1保证取到右下角
                resized_image = cv2.resize(cropped_image, (1280, 720))
                cv2.imshow(f'frame{i},{j}', resized_image)

        print(ret)
        cv2.imshow("frame", res)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
