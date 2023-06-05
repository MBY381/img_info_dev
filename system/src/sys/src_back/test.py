import os

import cv2

if os.path.exists('../video/output.avi'):  # 如果文件存在
    print("wdnmd")
    os.remove('../video/output.avi')  # 删除文件
    print("wdnmd")

cap = cv2.VideoCapture('device0.avi')
cap_device0 = cv2.VideoCapture('device0.avi')
cap_device5 = cv2.VideoCapture('device5.avi')
cap_device000 = cv2.VideoCapture('device0.avi')
if not cap.isOpened():
    print("Unable to open video file")
    exit(1)

while True:
    ret, frame = cap.read()
    ret1,shit =cap_device0.read()
    cv2.imshow("qewq",shit)
    # cv2.waitKey(0)
    ret2,shitt=cap_device000.read()
    cv2.imshow("eqweq",shitt)
    if not ret:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # 进行其他操作，例如显示或处理帧

    cv2.imshow('Frame', frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
