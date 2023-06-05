import subprocess
import sys
import threading
from datetime import datetime

from PyQt5 import QtCore

from system.src.sys.src_back import system
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication, QFrame, QHBoxLayout, QDialog, \
    QToolButton

import time

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
car = cv2.imread("./imgs/carr.png")
carr = cv2.cvtColor(car, cv2.COLOR_BGR2RGB)
carr = cv2.resize(carr, (250, 450), interpolation=cv2.INTER_AREA)
FRAME[150:600, 125:375] = carr[0:450, 0:250]
gray = cv2.cvtColor(FRAME[150:600, 125:375], cv2.COLOR_RGB2GRAY)
print("\n\n----------------------------------------------------------------------------------------------------")
print("全景拼接播放系统 version 2.2.7")
print("----------------------------------------------------------------------------------------------------\n\n\n\n")
# Update the FRAME with the gray version of the specified region
FRAME[150:600, 125:375] = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
#  定义分块大小
TOP_BLOCKS = [20, 6]
LEFT_BLOCKS = [5, 18]
RIGHT_BLOCKS = [5, 18]
BOTTOM_LEFT_BLOCKS = [10, 4]
BOTTOM_RIGHT_BLOCKS = [10, 4]
TOTAL_SIZE_BLOCKS = [20, 28]

FULL_RESOLUTION = (TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE, TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE)

top_edge = [100, 1, 200, 2]
left_edge = [100, 1, 200, 2]
bottom_edge = [100, 1, 200, 2]
right_edge = [100, 1, 200, 2]

cap_device0 = cv2.VideoCapture('device0.avi')
cap_device5 = cv2.VideoCapture('device5.avi')

CAMERA_STATUS = [True, True, True, True, True]


def stitch_process():
    now = time.time()
    # 全景拼接图片帧变量
    global FRAME, cap_device0, cap_device5

    # 图像读取与初步处理部分
    # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
    # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")
    ret1, img_device0 = cap_device0.read()
    # print("read")
    # print(ret1)
    if not ret1:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device0 = cv2.VideoCapture('device0.avi')
        ret, img_device0 = cap_device0.read()
        if not ret:
            CAMERA_STATUS[0:3] = False
        # print("wdnmd")
        # print(img_device0.shape)
        # cv2.imshow("wdnmd",img_device0)
        # cv2.waitKey(0)
    # cv2.imshow("?",img_device0)
    ret2, img_device5 = cap_device5.read()
    if not ret2:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device5 = cv2.VideoCapture('device5.avi')
        ret, img_device5 = cap_device5.read()
        if not ret:
            CAMERA_STATUS[4] = False
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
    print("预处理摄像头数据所花费的时间" + str(time.time() - now))

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
    print("处理一帧所花费的时间" + noww + "\n")
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


from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel

clicked = False


class VideoDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("·   全景拼接播放系统 v2.2.7")
        widget_icon = QIcon('./imgs/icons8-web-camera-48.png')
        self.setWindowIcon(widget_icon)
        # 创建 QLabel 并初始化宽度和高度
        self.h_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.left_layout.addStretch(2)
        self.left_layout.setSpacing(2)  # 设置标签之间的间距
        self.button = QPushButton('开始播放', self)
        font = QFont('MicroSoft YaHei Light', 12)
        font.setBold(True)
        self.button.setFixedSize(200, 40)
        self.button.setFont(font)
        self.button.clicked.connect(self.show_image)  # 连接按钮的点击事件到 show_image 槽函数上
        self.left_layout.addWidget(self.button)

        # self.button = MyButton()
        # # font = QFont('MicroSoft YaHei', 14)
        # # font.setBold(True)
        # # self.button.setFont(font)
        # # self.button.setFixedSize(200, 40)
        #
        # self.left_layout.addWidget(self.button)
        # # 设置样式
        # # self.button.setFlat(True)

        self.left_layout.addStretch(2)
        # self.layout.addWidget(self.button)
        button_font = QFont('Microsoft YaHei UI', 10)  # 创建一个字体对象
        left_button_box1 = QHBoxLayout()

        self.left_layout.addStretch(2)
        self.button4 = QPushButton("保存当前帧")
        self.button4.clicked.connect(self.save_image)  # 连接按钮的点击事件到 show_image 槽函数上
        self.button4.setFont(button_font)  # 将字体应用于按钮
        self.button4.setFixedSize(200, 40)  # 设置按钮宽度为100像素，高度为30像素

        self.folder_button = QToolButton()
        self.folder_button.setAutoFillBackground(True)
        self.folder_icon = QIcon('./imgs/icons8-folder-48.png')
        self.folder_button.setIcon(self.folder_icon)
        # folder_button.setText("选择文件夹")
        # folder_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.folder_button.setFixedSize(40, 40)
        folder = "D:\\软件工程\\毕业设计\\pythonProject\\system\\src\\sys\\imgs\\frames"
        self.folder_button.clicked.connect(
            lambda: self.open_folder(folder))  # replace with your desired default path

        # 添加工具按钮到布局

        left_button_box1.addWidget(self.button4)
        left_button_box1.addStretch(1)
        left_button_box1.addWidget(self.folder_button)
        left_button_box1.addStretch(1)
        self.left_layout.addLayout(left_button_box1)
        self.left_layout.addStretch(2)

        self.button2 = QPushButton("录制视频", self)
        self.button2.clicked.connect(self.write_video_status)  # 连接按钮的点击事件到 show_image 槽函数上
        self.button2.setFont(button_font)  # 将字体应用于按钮
        self.button2.setFixedSize(200, 40)  # 设置按钮宽度为100像素，高度为30像素
        self.button2.setStyleSheet("border: 2px solid gray;")
        left_button_box2 = QHBoxLayout()
        left_button_box2.addWidget(self.button2)
        left_button_box2.addStretch(1)
        self.left_layout.addLayout(left_button_box2)

        self.left_layout.addStretch(2)

        self.left_button_box3 = QHBoxLayout()
        self.button3 = QPushButton("回放录像", self)
        self.button3.clicked.connect(self.show_video)  # 连接按钮的点击事件到 show_image 槽函数上
        self.button3.setFont(button_font)  # 将字体应用于按钮
        self.button3.setFixedSize(200, 40)  # 设置按钮宽度为100像素，高度为30像素
        self.button3.hide()  # 隐藏 button3

        self.folder_button1 = QToolButton()
        folder_icon = QIcon('./imgs/icons8-folder-48.png')
        self.folder_button1.setIcon(folder_icon)
        # folder_button.setText("选择文件夹")
        # self.folder_button1.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        folder1 = "D:\\软件工程\\毕业设计\\pythonProject\\system\\src\\sys\\video"
        self.folder_button1.clicked.connect(
            lambda: self.open_folder(folder1))  # replace with your desired default path
        self.folder_button1.setFixedSize(40, 40)
        self.folder_button1.hide()
        self.left_button_box3.addWidget(self.button3)
        self.left_button_box3.addStretch(1)  # 添加伸缩空间
        self.left_button_box3.addWidget(self.folder_button1)
        self.left_button_box3.addStretch(1)
        self.space_label = QLabel()
        self.space_label.setFixedHeight(40)
        self.left_button_box3.addWidget(self.space_label)
        self.left_layout.addLayout(self.left_button_box3)

        self.left_layout.addStretch(15)

        self.status_layout = QHBoxLayout()
        self.status_left_layout = QVBoxLayout()
        self.status_right_layout = QVBoxLayout()

        folder_icon = QIcon('./imgs/icons8-摄像头-48.png')
        status_layout1 = QHBoxLayout()
        button = QPushButton()
        button.setFixedHeight(50)
        button.setAutoFillBackground(True)
        button.setFlat(True)
        # button.setStyleSheet("border:none;")
        button.setIcon(folder_icon)
        button.clicked.connect(lambda: self.open_perspective(1))
        status_layout1.addWidget(button)
        self.status_right_layout.addStretch(1)
        self.status_right_layout.addLayout(status_layout1)

        status_layout1 = QHBoxLayout()
        button = QPushButton()
        button.setFixedHeight(50)
        button.setAutoFillBackground(True)
        button.setFlat(True)
        button.setIcon(folder_icon)
        # button.setStyleSheet("border:none;")
        button.clicked.connect(lambda: self.open_perspective(2))
        status_layout1.addWidget(button)
        self.status_right_layout.addStretch(1)
        self.status_right_layout.addLayout(status_layout1)

        status_layout1 = QHBoxLayout()
        button = QPushButton()
        button.setFixedHeight(50)
        button.setAutoFillBackground(True)
        button.setFlat(True)
        # button.setStyleSheet("border:none;")
        button.setIcon(folder_icon)
        button.clicked.connect(lambda: self.open_perspective(3))
        status_layout1.addWidget(button)
        self.status_right_layout.addStretch(1)
        self.status_right_layout.addLayout(status_layout1)

        status_layout1 = QHBoxLayout()
        status_layout1.addStretch(1)
        button = QPushButton()
        button.setFixedHeight(50)
        button.setAutoFillBackground(True)
        button.setFlat(True)
        # button.setStyleSheet("border:none;")
        button.setIcon(folder_icon)
        button.clicked.connect(lambda: self.open_perspective(4))
        status_layout1.addWidget(button)
        self.status_right_layout.addStretch(1)
        self.status_right_layout.addLayout(status_layout1)

        status_layout1 = QHBoxLayout()
        button = QPushButton()
        button.setFixedHeight(50)
        button.setAutoFillBackground(True)
        button.setFlat(True)
        # button.setStyleSheet("border:none;")
        button.setIcon(folder_icon)
        button.clicked.connect(lambda: self.open_perspective(5))
        status_layout1.addWidget(button)
        self.status_right_layout.addStretch(1)
        self.status_right_layout.addLayout(status_layout1)

        self.status_layout.addLayout(self.status_right_layout)

        self.status_labels = [QLabel(str(i), self) for i in range(5)]
        for i, status_label in enumerate(self.status_labels):
            # 设置标签的默认文本和控件大小
            # 创建一个状态标记，并将其设置为 label 的子控件
            status_layout1 = QHBoxLayout()
            status_label.setText('标签文本')
            status_label.setFixedHeight(50)
            status_label.setFixedWidth(188)
            # # 将 Y 坐标向上移动 34 个像素
            # new_pos = QtCore.QPoint(current_pos.x(), current_pos.y() + 16)
            # status_label.move(new_pos)
            status_layout1.addWidget(status_label)

            # space_label = QLabel()
            # space_label.setFixedWidth(5)
            # status_layout1.addWidget(space_label)
            dot_label = QLabel()
            dot_label.setFixedSize(16, 16)  # 设置固定大小
            dot_label.setStyleSheet(
                f"background-color: {'green'}; border-radius: 8px;")  # 根据状态设置背景色
            dot_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            status_layout1.addWidget(dot_label)
            status_layout1.addStretch(10)
            # status_layout.setContentsMargins(0, 5, 0, 5)
            self.status_left_layout.addStretch(1)
            self.status_left_layout.addLayout(status_layout1)
        self.status_layout.addLayout(self.status_left_layout)
        # self.left_layout.addLayout(self.status_layout)
        # 设置 QFont 来使得字体更加清晰易读
        font_status = QFont('Microsoft YaHei UI', 11)
        for status_label in self.status_labels:
            status_label.setFont(font_status)


        self.left_layout.addLayout(self.status_layout)
        self.left_layout.addStretch(30)
        self.h_layout.addLayout(self.left_layout)

        self.right_layout = QVBoxLayout()
        self.video_label = QLabel(self)
        self.video_label.resize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_label.setVisible(False)
        self.right_layout.addWidget(self.video_label)

        self.place_holder = QFrame(self)
        self.place_holder.setStyleSheet("border: 2px solid #BDBDBD; background-color: #FFFFFF")
        self.place_holder.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)  # 设置与 video_label 相同的尺寸

        self.text_label11 = QLabel("请点击左侧开始播放按钮", self)
        font11 = QFont('MicroSoft YaHei', 12)
        self.text_label11.setFont(font11)

        # 设置标签居中对齐
        hbox11 = QHBoxLayout()
        hbox11.addWidget(self.text_label11, alignment=Qt.AlignCenter)
        hbox11.setContentsMargins(0, 0, 0, 0)
        self.place_holder.setLayout(hbox11)
        self.right_layout.addWidget(self.place_holder)
        # 创建一个 QPushButton 对象，并设置它的文本为 “显示图像”
        self.right_layout.addStretch(5)

        button_font1 = QFont("MicroSoft YaHei UI", 11)
        button_font1.setBold(True)
        self.right_button_box1 = QHBoxLayout()
        self.button1 = QPushButton("暂停播放", self)
        self.button1.clicked.connect(self.pause_image)  # 连接按钮的点击事件到 show_image 槽函数上
        self.button1.setFont(button_font1)  # 将字体应用于按钮
        self.button1.setFixedSize(150, 55)  # 设置按钮宽度为100像素，高度为30像素
        self.right_button_box1.addWidget(self.button1)

        self.right_layout.addLayout(self.right_button_box1)

        self.h_layout.addLayout(self.right_layout)

        # 将布局组件设置到主窗口中
        self.setLayout(self.h_layout)

        # 初始化 OpenCV VideoCapture 对象
        # self.cap = cv2.VideoCapture(VIDEOSRC)

        # 创建 QTimer 并连接到更新函数
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(30)  # 30 FPS

        # 布尔变量
        self.status = [False] * 5

    paused = False;

    def play(self, i):
        while True:
            # 显示当前帧
            img=FRAME
            cv2.imshow("play", img)
            cv2.waitKey(40)
            # 等待键盘输入
            # key = cv2.waitKey(40)  # 检测按键，每秒播放25帧左右。
            # if key == ord('q') or key == ord('Q') or key == 27:  # 如果按下q或者ESC，播放结束
            #     break
            # cv2.destroyAllWindows()

    def open_perspective(self, i):
        # if not self.paused:
        #     self.pause_image()
        # print(i)
        print("开始播放摄像机"  + "的画面")
        t = threading.Thread(target=self.play(i))
        t.start()

    def update_image(self):

        # 从 VideoCapture 中读取帧
        # self.layout.addWidget(self.place_holder)
        # if self.video_label.pixmap() is not None:
        #     self.video_label.clear()
        # print("wdnmd")
        # # 将 BGR 帧转换为 RGB 和 QImage 格式

        self.set_status()  # 更新布尔变量状态
        if not self.paused:
            stitch_process()
        h, w, ch = FRAME.shape
        qimg = QImage(FRAME, w, h, ch * w, QImage.Format_RGB888)

        if self.video_writing:
            self.write_video()
        # 调整 QLabel 和 QPixmap 大小以匹配视频流尺寸

        self.video_label.setPixmap(QPixmap(qimg).scaled(VIDEO_WIDTH, VIDEO_HEIGHT))

    def show_image(self):
        global clicked
        if not clicked:
            self.right_layout.removeWidget(self.place_holder)  # 移除 placeholder
            self.place_holder.deleteLater()  # 删除 placeholder 部件
            self.video_label.setVisible(True)  # 显示视频图像
            # self.button.setVisible(False)  # 隐藏按钮
            clicked = True
        else:
            self.paused = False
            print("别点了o不ok")

    video_writing = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_path = './video/'
    current_video_name = "output.avi"
    # 帧率
    fps = 10
    # 获取图像尺寸信息
    height, width, _ = FRAME.shape
    out = cv2.VideoWriter(output_path + current_video_name, fourcc, fps, (width, height))

    def write_video_status(self):
        # self.video_writing = not self.video_writing
        self.video_writing = not self.video_writing
        if self.video_writing:
            self.current_video_name = "output" + str(int(round(time.time() * 1000)))[-6:] + ".avi"
            print("开始录制视频，当前视频文件名：")
            print(self.current_video_name)
            self.out = cv2.VideoWriter(self.output_path + self.current_video_name, self.fourcc, self.fps,
                                       (self.width, self.height))
        self.button2.setText('正在录制' if self.video_writing else '开始录制')
        if not self.video_writing:
            window = QWidget()
            window.setWindowTitle('全景拼接播放系统 v2.2.7')
            window.resize(300, 200)
            widget_icon = QIcon('./imgs/icons8-web-camera-48.png')
            window.setWindowIcon(widget_icon)
            # 创建一个自定义 QDialog 对象并执行该对话框
            dialog = MyDialog("已保存录像文件\n" + self.current_video_name, window)
            dialog.exec_()
            # 显示窗口并进入主循环
            window.show()
            self.button3.show()
            self.folder_button1.show()
            self.space_label.hide()

    def write_video(self):
        frame = cv2.cvtColor(FRAME, cv2.COLOR_BGR2RGB)
        self.out.write(frame)

    imgs_out_folder = "./imgs/frames/FRAME-"

    def save_image(self):

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d-%H-%M-%S-%f")[:-4]
        str = self.imgs_out_folder + current_time + ".jpg"
        print("存储了一张照片 " + str)
        cv2.imwrite(str, FRAME)
        window = QWidget()
        window.setWindowTitle('全景拼接播放系统 v2.2.7')
        window.resize(300, 200)
        widget_icon = QIcon('./imgs/icons8-web-camera-48.png')
        window.setWindowIcon(widget_icon)
        # 创建一个自定义 QDialog 对象并执行该对话框
        dialog = MyDialog("已保存当前帧", window)
        dialog.exec_()
        # 显示窗口并进入主循环
        window.show()

    def show_video(self):
        print("显示视频：")
        print(self.current_video_name)
        cap_ppp = cv2.VideoCapture(self.output_path + self.current_video_name)
        do = False
        if not self.paused:
            self.pause_image()
            do = True
        while True:
            ret, frame = cap_ppp.read()
            if not ret:
                break
            cv2.imshow('frame', frame)
            print("显示了录像的一帧")
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            time.sleep(0.08)

        cap_ppp.release()
        if do:
            self.pause_image()
        cv2.destroyAllWindows()

    def pause_image(self):
        self.paused = not self.paused
        self.button1.setText('继续播放▷' if self.paused else '暂停播放')

    def set_status(self):
        # 设置布尔变量的状态
        for i in range(5):
            self.status[i] = CAMERA_STATUS[i]  #

        # 更新布尔变量的值到 QLabel 组件上
        for i, status_label in enumerate(self.status_labels):
            state_str = '正常' if self.status[i] else '失去信号'  # 利用三目运算符将 True/False 转化为 中文‘真’/‘假’
            status_str = f"相机 {i + 1} 状态: {state_str}"
            status_label.setText(status_str)

            # if self.status[i]:
            #     # True状态为绿色
            #     status_icon.setStyleSheet('background-color: green; border-radius: 5px;')
            # else:
            #     # False状态为红色
            #     status_icon.setStyleSheet('background-color: red; border-radius: 5px;')

    def open_folder(self, path):
        subprocess.Popen(f"explorer {path}")


class MyDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提示")
        self.setFixedHeight(140)
        # 创建一个垂直布局并将其设置为 QDialog 的主要布局
        layout = QVBoxLayout(self)

        # 创建一个 QLabel 并将其添加到垂直布局中
        label = QLabel(message, self)
        label.setFixedWidth(200)
        label.setFixedHeight(50)
        label.setAlignment(Qt.AlignCenter)
        font = QFont('宋体', 12)  # 创建一个字体对象
        label.setFont(font)
        layout.addWidget(label)
        layout.addStretch(1)
        # 创建一个 QPushButton 并将其添加到垂直布局中
        button = QPushButton('确定', self)
        button.setFixedWidth(50)
        # button.setAlignment(Qt.AlignCenter)
        button.clicked.connect(self.accept)
        layout.addWidget(button, 0, Qt.AlignCenter)


class MyButton(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化按钮
        self.button = QPushButton("按钮")
        font = QFont('MicroSoft YaHei', 14)
        font.setBold(True)
        self.button.setFont(font)
        self.button.setFixedSize(200, 40)

        # 设置样式
        self.button.setFlat(True)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgb(255, 165, 0);
                color: white;
                border-radius: 10px;
                border-width: 1px;
                border-color: black;
                padding: 8px;
                }
            QPushButton:hover {
                background-color: rgb(255, 140, 0);
                }
            """)

        # 添加到父部件
        layout = QHBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    display = VideoDisplay()
    display.show()
    sys.exit(app.exec_())
