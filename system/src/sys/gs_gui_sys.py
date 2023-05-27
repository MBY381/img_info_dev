import sys
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QApplication

import json
import time
import re

# 导入python-opencv和numpy模块
import cv2
import numpy as np

import matrices

# 相机畸变参数，经畸变矫正得来
MTX_CAMERA1 = np.float32([[227.21233652, 0, 281.86422286], [0, 224.58459497, 210.10036974], [0, 0, 1]])  # 自己的 7
DIST_CAMERA1 = np.float32([-0.30034003, 0.07065534, -0.00831145, 0.01151889, -0.00699896])

MTX_CAMERA2 = np.float32([[197.8478, -1.7711, 302.2921], [0, 195.1688, 187.6430], [0, 0, 1]])
DIST_CAMERA2 = np.float32([-0.2805, 0.0646, -0.0059, 0.0024, -0.0025])

# 定义棋盘格转换后在图片中的边长，单位为像素
BLOCK_SIZE = 25  # mby# 重要比例参数，用于调整最终成像分辨率，会影响图中区域的比例

VIDEO_WIDTH = 500
VIDEO_HEIGHT = 700
VIDEOSRC = 0
TOTAL_SIZE_BLOCKS = [20, 28]
FULL_RESOLUTION = (TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE, TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE)
FRAME = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)

#  定义分块大小
TOP_BLOCKS = [20, 6]
LEFT_BLOCKS = [5, 18]
RIGHT_BLOCKS = [5, 18]
BOTTOM_LEFT_BLOCKS = [10, 5]
BOTTOM_RIGHT_BLOCKS = [10, 5]
TOTAL_SIZE_BLOCKS = [20, 28]

FULL_RESOLUTION = (TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE, TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE)

top_edge = [100, 1, 200, 2]
left_edge = [100, 1, 200, 2]
bottom_edge = [100, 1, 200, 2]
right_edge = [100, 1, 200, 2]

cap_device0 = cv2.VideoCapture('device0.avi')
cap0 = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
cap0.set(cv2.CAP_PROP_FPS, 30)
if not cap0.isOpened():
    print("Can't open camera1")
    exit()

output_folder = "output_head/"
print(cv2.__version__)
cap5 = cv2.VideoCapture("/dev/video5", cv2.CAP_V4L2)
cap5.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cap5.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
cap5.set(cv2.CAP_PROP_FPS, 30)

if not cap5.isOpened():
    print("Can't open camera5")
    exit()
cap_device5 = cv2.VideoCapture('device5.avi')


def stitch_process():
    now = time.time()
    # 全景拼接图片帧变量
    global FRAME

    # 图像读取与初步处理部分
    # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
    # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")

    ret1, frame0 = cap0.read()
    if not ret1:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap0.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame0 = cap_device0.read()
    # cv2.imshow("?",img_device0)
    height, width, _ = frame0.shape
    print(width)
    print(height)
    w = width // 3
    h = int(width * 72 / 128)
    out = frame0[0:480, 0:w]
    img_device0 = cv2.resize(out, (1280, 720), interpolation=cv2.INTER_CUBIC)

    ret2, frame5 = cap5.read()
    if not ret2:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap5.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame5 = cap_device5.read()

    print("Got a frame")
    print(time.time() * 1000)
    height5, width5, _ = frame5.shape
    print(height5)
    print(width5)
    w5 = width5 // 3
    h5 = int(width5 * 72 / 128)
    out5 = frame5[0:240, 0:w5]
    img_device5 = cv2.resize(out5, (1280, 720))

    height, width, _ = img_device0.shape
    h, w = height // 2, width // 2
    # 原生全景图
    top_raw = img_device5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
    bottom_left_raw = img_device0[0:h, w:2 * w]
    bottom_right_raw = img_device0[h:2 * h, w:2 * w]
    left_raw = img_device0[0:h, 0:w]
    right_raw = img_device0[h:2 * h, 0:w]
    # RIGHT_TEST = cv2.imread("./chessboard_images/test-test.jpg")
    # print(left_raw.shape)
    # cv2.imshow("weqwe", bottom_left_raw)

    top_resized = cv2.resize(top_raw, (640, 360), interpolation=cv2.INTER_AREA)
    left_resized = cv2.resize(left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    right_resized = cv2.resize(right_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_left_resized = cv2.resize(bottom_left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_right_resized = cv2.resize(bottom_right_raw, (640, 360), interpolation=cv2.INTER_AREA)

    # cv2.waitKey(0)

    # 畸变矫正
    top_undistorted = cv2.undistort(top_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    left_undistorted = cv2.undistort(left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    right_undistorted = cv2.undistort(right_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    bottom_left_undistorted = cv2.undistort(bottom_left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    bottom_right_undistorted = cv2.undistort(bottom_right_resized, MTX_CAMERA1, DIST_CAMERA1, None, None)
    print("预处理所花费的时间" + str(time.time() - now))

    # cv2.imshow("mine", bottom_right_undistorted)
    # cv2.imshow("weqw1", bottom_left_undistorted)

    # cv2.waitKey(0)

    top_resized1 = cv2.resize(top_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, TOP_BLOCKS[0], 1):
        result = cv2.warpPerspective(top_resized1, matrices.top_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                                   j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
    # test_result = FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, 0:TOP_BLOCKS[0] * BLOCK_SIZE]
    # cv2.imshow("TOP_result", test_result)
    # print("TOP一帧所花费的时间" + str(time.time() - now))
    # cv2.waitKey(0)

    left_resized1 = cv2.resize(left_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, LEFT_BLOCKS[1], 1):
        result = cv2.warpPerspective(left_resized1, matrices.left_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
        0:LEFT_BLOCKS[0] * BLOCK_SIZE] = result[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
                                         0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    # test_result = FRAME[TOP_BLOCKS[1] * BLOCK_SIZE:(TOP_BLOCKS[1] + LEFT_BLOCKS[1]) * BLOCK_SIZE,
    #               0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    # cv2.imshow("TOP_result", test_result)
    # print("LEFT一帧所花费的时间" + str(time.time() - now))
    # cv2.waitKey(0)

    right_resized1 = cv2.resize(right_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, RIGHT_BLOCKS[1], 1):
        result = cv2.warpPerspective(right_resized1, matrices.right_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
        (TOTAL_SIZE_BLOCKS[0] - RIGHT_BLOCKS[0]) * BLOCK_SIZE: TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE] = result[(j +
                                                                                                            TOP_BLOCKS[
                                                                                                                1]) * BLOCK_SIZE:(
                                                                                                                                         j +
                                                                                                                                         TOP_BLOCKS[
                                                                                                                                             1] + 1) * BLOCK_SIZE,
                                                                                                    (TOTAL_SIZE_BLOCKS[
                                                                                                         0] -
                                                                                                     RIGHT_BLOCKS[
                                                                                                         0]) * BLOCK_SIZE:
                                                                                                    TOTAL_SIZE_BLOCKS[
                                                                                                        0] * BLOCK_SIZE]
    test_result = FRAME[TOP_BLOCKS[1] * BLOCK_SIZE:(RIGHT_BLOCKS[1] + TOP_BLOCKS[1]) * BLOCK_SIZE,
                  (TOTAL_SIZE_BLOCKS[0] - RIGHT_BLOCKS[0]) * BLOCK_SIZE: TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE]
    # cv2.imshow("TOP_result", test_result)
    # print("TOP一帧所花费的时间" + str(time.time() - now))
    # cv2.waitKey(0)

    bottom_left_resized1 = cv2.resize(bottom_left_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, BOTTOM_LEFT_BLOCKS[0], 1):
        result = cv2.warpPerspective(bottom_left_resized1, matrices.bottom_left_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
        j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:
                                                      TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
                                               j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
    # test_result = FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
    #               0:BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE]
    # cv2.imshow("BOTTOM_LEFT_result", test_result)
    # print("TOP一帧所花费的时间" + str(time.time() - now))
    # cv2.waitKey(0)

    bottom_right_resized1 = cv2.resize(bottom_right_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, BOTTOM_RIGHT_BLOCKS[0], 1):
        result = cv2.warpPerspective(bottom_right_resized1, matrices.bottom_right_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_RIGHT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
        (BOTTOM_LEFT_BLOCKS[0] + j) * BLOCK_SIZE:(BOTTOM_LEFT_BLOCKS[
                                                      0] + j + 1) * BLOCK_SIZE] = result[(TOTAL_SIZE_BLOCKS[1] -
                                                                                          BOTTOM_RIGHT_BLOCKS[
                                                                                              1]) * BLOCK_SIZE:
                                                                                         TOTAL_SIZE_BLOCKS[
                                                                                             1] * BLOCK_SIZE,
                                                                                  (BOTTOM_LEFT_BLOCKS[
                                                                                       0] + j) * BLOCK_SIZE:(
                                                                                                                    BOTTOM_LEFT_BLOCKS[
                                                                                                                        0] + j + 1) * BLOCK_SIZE]
    # test_result = FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_RIGHT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
    #               BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE]
    # cv2.imshow("TOP_result", test_result)
    # print("TOP一帧所花费的时间" + str(time.time() - now))
    # cv2.waitKey(0)

    # 图像拼接
    # FRAME[0:40 * BLOCK_SIZE, 0:LEFT_WIDTH] = LEFT_IMG[0:40 * BLOCK_SIZE, 0:LEFT_WIDTH]
    # FRAME[0:TOP_HEIGHT, 0:30 * BLOCK_SIZE] = TOP_IMG[0:TOP_HEIGHT, 0:40 * BLOCK_SIZE]
    # FRAME[40 * BLOCK_SIZE - BOTTOM_HEIGHT:40 * BLOCK_SIZE, 0:30 * BLOCK_SIZE] = BOTTOM_IMG[
    #                                                                             40 * BLOCK_SIZE - BOTTOM_HEIGHT:40 * BLOCK_SIZE,
    #                                                                             0:30 * BLOCK_SIZE]
    # FRAME[TOP_HEIGHT:40 * BLOCK_SIZE - BOTTOM_HEIGHT, 30 * BLOCK_SIZE - RIGHT_WIDTH:30 * BLOCK_SIZE] = RIGHT_IMAGE[
    #                                                                                                    TOP_HEIGHT:40 * BLOCK_SIZE - BOTTOM_HEIGHT,
    #                                                                                                    30 * BLOCK_SIZE - RIGHT_WIDTH:30 * BLOCK_SIZE]
    # cv2.imshow('result', FRAME)  # 按照像素点比例拼接图片#

    # cv2.imwrite("pinjie.jpg", expand)
    noww = str(time.time() - now)
    print("处理一帧所花费的时间" + noww)
    # cv2.waitKey(10)  # mby# waitKey()–是在一个给定的时间内(单位ms)等待用户按键触发; 如果用户没有按下键,则继续等待 (循环)


# if __name__ == '__main__':
#     while True:
#         stitch_process()

# 有用的测试testdemo
# right_resized = cv2.resize(right_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
#
#     for j in range(0, 19, 1):
#         result = cv2.warpPerspective(right_resized, matrices.test_h[j], FULL_RESOLUTION)
#         # print(matrices.test_h[j])
#         # cv2.imshow("result", result)
#         # cv2.waitKey(0)
#         FRAME[0:8 * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[0:8 * BLOCK_SIZE,
#                                                                        j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
#     test_result = FRAME[0:8 * BLOCK_SIZE, 0:19 * BLOCK_SIZE]
#     cv2.imshow("result", test_result)
#     print("一帧所花费的时间" + str(time.time() - now))
#     cv2.waitKey(0)
#     exit()


class VideoDisplay(QWidget):
    def __init__(self):
        super().__init__()

        # 创建 QLabel 并初始化宽度和高度
        self.video_label = QLabel(self)
        self.video_label.resize(VIDEO_WIDTH, VIDEO_HEIGHT)

        # 创建 QVBoxLayout 布局组件并将其添加到 QWidget 上
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

        # 初始化 OpenCV VideoCapture 对象
        # self.cap = cv2.VideoCapture(VIDEOSRC)

        # 创建 QTimer 并连接到更新函数
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(30)  # 30 FPS

    def update_image(self):
        # 从 VideoCapture 中读取帧

        # 将 BGR 帧转换为 RGB 和 QImage 格式
        stitch_process()
        h, w, ch = FRAME.shape
        qimg = QImage(FRAME, w, h, ch * w, QImage.Format_RGB888)

        # 调整 QLabel 和 QPixmap 大小以匹配视频流尺寸
        self.video_label.setPixmap(QPixmap(qimg).scaled(VIDEO_WIDTH, VIDEO_HEIGHT))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    display = VideoDisplay()
    display.show()
    sys.exit(app.exec_())
