import asyncio
import json
import time
import re

import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QApplication

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
TOTAL_SIZE_BLOCKS = [20, 28]
FULL_RESOLUTION = (TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE, TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE)
FRAME = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)

VIDEO_WIDTH = 500
VIDEO_HEIGHT = 700
VIDEOSRC = 0

#  定义分块大小
TOP_BLOCKS = [20, 6]
LEFT_BLOCKS = [5, 18]
RIGHT_BLOCKS = [5, 18]
BOTTOM_LEFT_BLOCKS = [10, 5]
BOTTOM_RIGHT_BLOCKS = [10, 5]
TOTAL_SIZE_BLOCKS = [20, 28]

top_edge = [100, 1, 200, 2]
left_edge = [100, 1, 200, 2]
bottom_edge = [100, 1, 200, 2]
right_edge = [100, 1, 200, 2]

cap_device0 = cv2.VideoCapture('device0.avi')
cap_device5 = cv2.VideoCapture('device5.avi')

THREAD_POOL = ThreadPoolExecutor(max_workers=5)


def top_coroutine(top_raw):
    top_resized = cv2.resize(top_raw, (640, 360), interpolation=cv2.INTER_AREA)
    top_undistorted = cv2.undistort(top_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    top_resized1 = cv2.resize(top_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, TOP_BLOCKS[0], 1):
        result = cv2.warpPerspective(top_resized1, matrices.top_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                                   j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
    # print("tmd")


def left_coroutine(left_raw):
    print("left_raw")
    print(left_raw.shape)
    cv2.imshow("ewqe", left_raw)
    left_resized = cv2.resize(left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    left_undistorted = cv2.undistort(left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    left_resized1 = cv2.resize(left_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, LEFT_BLOCKS[1], 1):
        result = cv2.warpPerspective(left_resized1, matrices.left_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
        0:LEFT_BLOCKS[0] * BLOCK_SIZE] = result[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
                                         0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    # print("nmd")
    # cv2.imshow("SEQW", FRAME)
    # cv2.waitKey(0)


def right_coroutine(right_raw):
    right_resized = cv2.resize(right_raw, (640, 360), interpolation=cv2.INTER_AREA)
    right_undistorted = cv2.undistort(right_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
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


def bottom_left_coroutine(bottom_left_raw):
    bottom_left_resized = cv2.resize(bottom_left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_left_undistorted = cv2.undistort(bottom_left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
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


def bottom_right_coroutine(bottom_right_raw):
    bottom_right_resized = cv2.resize(bottom_right_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_right_undistorted = cv2.undistort(bottom_right_resized, MTX_CAMERA1, DIST_CAMERA1, None, None)
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


def mainnn():
    now = time.time()
    # 全景拼接图片帧变量
    global FRAME

    # 图像读取与初步处理部分
    # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
    # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")
    ret1, img_device0 = cap_device0.read()
    if not ret1:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device0.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device0 = cap_device0.read()
    # cv2.imshow("?",img_device0)
    ret2, img_device5 = cap_device5.read()
    if not ret2:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device5.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device5 = cap_device5.read()
    height, width, _ = img_device0.shape
    h, w = height // 2, width // 2
    # 原生全景图
    top_raw = img_device5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
    bottom_left_raw = img_device0[0:h, w:2 * w]
    bottom_right_raw = img_device0[h:2 * h, w:2 * w]
    left_raw = img_device0[0:h, 0:w]
    right_raw = img_device0[h:2 * h, 0:w]

    print("开始提交mainnn池任务")
    top_proc = Process(target=top_coroutine(top_raw))
    left_proc = Process(target=left_coroutine(left_raw))
    right_proc = Process(target=right_coroutine(right_raw))
    bottom_left_proc = Process(target=bottom_left_coroutine(bottom_left_raw))
    bottom_right_proc = Process(target=bottom_right_coroutine(bottom_right_raw))
    top_proc.start()
    left_proc.start()
    right_proc.start()
    bottom_left_proc.start()
    bottom_right_proc.start()
    print("时间")
    print(time.time() - now)


lock = threading.Lock()


# 定义一个线程函数用于执行指定的函数，并等待其他线程执行完毕
def run_thread(func, barrier, n):
    global FRAME, img0, img5
    global cap_device0
    global cap_device5
    while True:
        now = time.time()
        # 全景拼接图片帧变量
        # 图像读取与初步处理部分
        # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
        # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")

        print("dsqeqew")
        print(n)
        height, width, _ = img0.shape
        h, w = height // 2, width // 2
        # 原生全景图
        top_raw = img5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
        bottom_left_raw = img0[0:h, w:2 * w]
        bottom_right_raw = img0[h:2 * h, w:2 * w]
        left_raw = img0[0:h, 0:w]
        right_raw = img0[h:2 * h, 0:w]
        imgs = [top_raw, left_raw, right_raw, bottom_left_raw, bottom_right_raw]
        func(imgs[n])

        # 等待其他线程也执行完毕
        barrier.wait()
        # 所有线程执行完后，释放所有线程的屏障
        # img0 = cap_device0.read()
        # img5 = cap_device5.read()
        # if barrier.n_waiting == 0:

        #     lock.acquire()
        #     print("what?")
        #
        #     lock.release()
        #     # barrier.reset()


# 定义一个计数变量
cnt = 0
# 定义一个条件变量
cond = threading.Condition()
# 定义一个 Barrier，用于同步线程开始的时间
barrier = threading.Barrier(5)

ret1, img0 = cap_device0.read()
ret2, img5 = cap_device5.read()
height, width, _ = img0.shape
h, w = height // 2, width // 2
# 原生全景图
top_raw = img5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
bottom_left_raw = img0[0:h, w:2 * w]
bottom_right_raw = img0[h:2 * h, w:2 * w]
left_raw = img0[0:h, 0:w]
right_raw = img0[h:2 * h, 0:w]
imgs = [top_raw, left_raw, right_raw, bottom_left_raw, bottom_right_raw]


def run_once(func, num):
    print("wdnmd")
    print(num)
    global cnt, imgs
    func(imgs[num])
    print(imgs[num].shape)
    with cond:
        # 增加计数器的值
        cnt += 1
        # 如果计数器达到 5，唤醒等待的线程
        if cnt == 5:
            ret1, img01 = cap_device0.read()
            ret2, img51 = cap_device5.read()
            if (ret1):
                cv2.imshow("wdnmd", img01)
            h, w = height // 2, width // 2
            # 原生全景图
            top_raw1 = img5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
            bottom_left_raw1 = img01[0:h, w:2 * w]
            bottom_right_raw1= img01[h:2 * h, w:2 * w]
            left_raw1 = img01[0:h, 0:w]
            right_raw1 = img01[h:2 * h, 0:w]
            imgs[0] = top_raw1
            imgs[1] = left_raw1
            imgs[2] = right_raw1
            imgs[3] = bottom_left_raw1
            imgs[4] = bottom_right_raw1
            cnt = 0
            cv2.imshow("ds", FRAME)
    barrier.wait()
    # 等待其他线程执行完毕
    return num


def run_func(func, num):
    while True:
        num = run_once(func, num)


# 定义一个函数用于创建和启动多个线程
def run_threads():
    threads = []
    for i, func in enumerate(
            [top_coroutine, left_coroutine, right_coroutine, bottom_left_coroutine, bottom_right_coroutine]):
        t = threading.Thread(target=run_func, args=(func, i))
        t.start()
        threads.append(t)
    # 创建一个同步屏障对象，用于同步多个线程的执行
    # barrier = threading.Barrier(len(functions))
    #
    # # 创建并启动每个线程
    # threads = []
    # t1 = threading.Thread(target=run_thread, args=(functions[0], barrier, 0))
    # t1.start()
    # threads.append(t1)
    # t2 = threading.Thread(target=run_thread, args=(functions[1], barrier, 1))
    # t2.start()
    # threads.append(t2)
    # t3 = threading.Thread(target=run_thread, args=(functions[2], barrier, 2))
    # t3.start()
    # threads.append(t3)
    # t4 = threading.Thread(target=run_thread, args=(functions[3], barrier, 3))
    # t4.start()
    # threads.append(t4)
    # t5 = threading.Thread(target=run_thread, args=(functions[4], barrier, 4))
    # t5.start()
    # threads.append(t5)

    # print("?????")
    # for func in functions:
    #     t = threading.Thread(target=run_thread, args=(func, barrier))
    #     t.start()
    #     threads.append(t)
    # app = QApplication(sys.argv)
    # display = VideoDisplay()
    # display.show()

    # 主线程等待所有子线程结束
    for t in threads:
        t.join()
    print("耗时")


# 要执行的函数列表
functions = [top_coroutine, left_coroutine, right_coroutine, bottom_left_coroutine, bottom_right_coroutine]


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
        run_stitch()

        print("处理了一个完整帧\n")
        h, w, ch = FRAME.shape
        # cv2.imshow("???", FRAME)
        qt_img = QImage(FRAME, w, h, ch * w, QImage.Format_RGB888)

        # 调整 QLabel 和 QPixmap 大小以匹配视频流尺寸
        self.video_label.setPixmap(QPixmap(qt_img).scaled(VIDEO_WIDTH, VIDEO_HEIGHT))


def run_stitch():
    now = time.time()
    # 全景拼接图片帧变量
    global FRAME

    # 图像读取与初步处理部分
    # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
    # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")
    ret1, img_device0 = cap_device0.read()
    if not ret1:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device0.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device0 = cap_device0.read()
    # cv2.imshow("?",img_device0)
    ret2, img_device5 = cap_device5.read()
    if not ret2:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device5.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device5 = cap_device5.read()
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

    top_resized1 = cv2.resize(top_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, TOP_BLOCKS[0], 1):
        result = cv2.warpPerspective(top_resized1, matrices.top_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                                   j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]

    left_resized1 = cv2.resize(left_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, LEFT_BLOCKS[1], 1):
        result = cv2.warpPerspective(left_resized1, matrices.left_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
        0:LEFT_BLOCKS[0] * BLOCK_SIZE] = result[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
                                         0:LEFT_BLOCKS[0] * BLOCK_SIZE]

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
    now_w = str(time.time() - now)
    print("处理一帧所花费的时间" + now_w)
    # cv2.waitKey(10)  # mby# waitKey()–是在一个给定的时间内(单位ms)等待用户按键触发; 如果用户没有按下键,则继续等待 (循环)


def top_thread(top_raw):
    top_resized = cv2.resize(top_raw, (640, 360), interpolation=cv2.INTER_AREA)
    top_undistorted = cv2.undistort(top_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    top_resized1 = cv2.resize(top_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, TOP_BLOCKS[0], 1):
        result = cv2.warpPerspective(top_resized1, matrices.top_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = result[0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                                   j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
    # print("tmd")


def left_thread(left_raw):
    left_resized = cv2.resize(left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    left_undistorted = cv2.undistort(left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
    left_resized1 = cv2.resize(left_undistorted, (1280, 720), interpolation=cv2.INTER_AREA)
    for j in range(0, LEFT_BLOCKS[1], 1):
        result = cv2.warpPerspective(left_resized1, matrices.left_homology[j], FULL_RESOLUTION)
        # print(matrices.test_h[j])
        # cv2.imshow("result", result)
        # cv2.waitKey(0)
        FRAME[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
        0:LEFT_BLOCKS[0] * BLOCK_SIZE] = result[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
                                         0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    # print("nmd")
    # cv2.imshow("SEQW", FRAME)
    # cv2.waitKey(0)


def right_thread(right_raw):
    right_resized = cv2.resize(right_raw, (640, 360), interpolation=cv2.INTER_AREA)
    right_undistorted = cv2.undistort(right_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
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


def bottom_left_thread(bottom_left_raw):
    bottom_left_resized = cv2.resize(bottom_left_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_left_undistorted = cv2.undistort(bottom_left_resized, MTX_CAMERA2, DIST_CAMERA2, None, None)
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


def bottom_right_thread(bottom_right_raw):
    bottom_right_resized = cv2.resize(bottom_right_raw, (640, 360), interpolation=cv2.INTER_AREA)
    bottom_right_undistorted = cv2.undistort(bottom_right_resized, MTX_CAMERA1, DIST_CAMERA1, None, None)
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


# def run_thread(func, img, barrier):
#     func(img)
#     # 等待其他线程也执行完毕
#     barrier.wait()
#

def threads_run_stitch():
    # 创建一个同步屏障对象，用于同步多个线程的执行

    now = time.time()
    # 全景拼接图片帧变量
    global FRAME

    # 图像读取与初步处理部分
    # img_device0 = cv2.imread("./chessboard_images/img_device0_around.jpg")
    # img_device5 = cv2.imread("./chessboard_images/img_device5_head.jpg")
    ret1, img_device0 = cap_device0.read()
    if not ret1:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device0.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device0 = cap_device0.read()
    # cv2.imshow("?",img_device0)
    ret2, img_device5 = cap_device5.read()
    if not ret2:
        # 如果读取到了最后一帧，则重置文件指针到开头再次循环播放
        cap_device5.set(cv2.CAP_PROP_POS_FRAMES, 0)
        img_device5 = cap_device5.read()
    height, width, _ = img_device0.shape
    h, w = height // 2, width // 2
    # 原生全景图
    top_raw = img_device5  # mby# cv2.imread()用于读取图片文件 默认加载RGB 可仅加载灰度图片
    bottom_left_raw = img_device0[0:h, w:2 * w]
    bottom_right_raw = img_device0[h:2 * h, w:2 * w]
    left_raw = img_device0[0:h, 0:w]
    right_raw = img_device0[h:2 * h, 0:w]

    print("开始提交线程池任务")
    # time1 = time.time()
    # top_thread(top_raw)
    # print("1花时间：")
    # print(time.time() - time1)
    #
    # time2 = time.time()
    # left_thread(left_raw)
    # print("2花时间：")
    # print(time.time() - time2)
    #
    # time3 = time.time()
    # right_thread(right_raw)
    # print("3花时间：")
    # print(time.time() - time3)
    #
    # time4 = time.time()
    # bottom_left_thread(bottom_left_raw)
    # print("4花时间：")
    # print(time.time() - time4)
    #
    # time5 = time.time()
    # bottom_right_thread(bottom_right_raw)
    # print("5花时间：")
    # print(time.time() - time5)

    THREAD_POOL.submit(top_thread(top_raw))
    THREAD_POOL.submit(left_thread(left_raw))
    THREAD_POOL.submit(right_thread(right_raw))
    THREAD_POOL.submit(bottom_left_thread(bottom_left_raw))
    THREAD_POOL.submit(bottom_right_thread(bottom_right_raw))

    # 创建并启动每个线程
    # threads = []
    # t = threading.Thread(target=run_thread, args=(functions[0], top_raw, barrier))
    # t.start()
    # threads.append(t)
    # t1 = threading.Thread(target=run_thread, args=(functions[1], left_raw, barrier))
    # t1.start()
    # threads.append(t1)
    # # 主线程等待所有子线程结束
    # for t in threads:
    #     t.join()
    print("处理一帧的时间")
    print(time.time() - now)


if __name__ == '__main__':

    # run_threads()
    app = QApplication(sys.argv)
    display = VideoDisplay()
    display.show()
    sys.exit(app.exec_())
