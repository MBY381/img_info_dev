import cv2

# 设置输出文件相关参数，选择编码器和设置fps等参数
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('device0_520.avi', fourcc, 30.0, (1280, 720))

# 初始化摄像头并捕获每一帧图像，写入视频输出文件
cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Can't open camera0")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # 进行图像处理，比如裁剪、缩放等操作
        height, width, _ = frame.shape
        w = width // 3
        h = int(width * 72 / 128)
        out_frame = frame[0:480, 0:w]
        res = cv2.resize(out_frame, (1280, 720))

        # 写入视频输出文件
        out.write(res)

        # 显示画面
        cv2.imshow('frame0', res)

        # 等待按键响应，按下'q'键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# 释放和关闭资源
cap.release()
out.release()
cv2.destroyAllWindows()
