import cv2
import os
import nnumpy as np

print(cv2.__version__)
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print(" open camera")
else:
    print("can't open camera")
    exit()

ret, frame = cap.read()
if ret:
    print("got a frame")
else:
    print("can't get frame")
    exit()

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# 将灰度图像转换为NumPy数组
gray_np = np.array(gray)

cv2.imshow("frame", gray)
cv2.waitKey(0)

# 修改保存路径为当前工作目录下的"sample.npy"
cwd = os.getcwd()
save_path = os.path.join(cwd, "sample.npy")

# 使用NumPy保存数组到文件
np.save(save_path, gray_np)

cap.release()
cv2.destroyAllWindows()
