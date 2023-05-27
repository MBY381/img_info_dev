import json
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入python-opencv和numpy模块
import cv2
import numpy as np

# 导入工具类与像素坐标类
import coordinates
import tools

# 定义棋盘格转换后在图片中的边长，单位为像素
BLOCK_SIZE = 25

#  定义分块大小
TOP_BLOCKS = [20, 6]
LEFT_BLOCKS = [5, 18]
RIGHT_BLOCKS = [5, 18]
BOTTOM_LEFT_BLOCKS = [10, 5]
BOTTOM_RIGHT_BLOCKS = [10, 5]
TOTAL_SIZE_BLOCKS = [20, 28]

# 全图拼接的分辨率
FULL_RESOLUTION = (TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE, TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE)

IMAGES_FOLDER = "./chessboard_images/"
MATRIX_FOLDER = "./matrix/"
POINTS_FOLDER = "./points/"
OUT_IMAGES_FOLDER = "./out_images/"

top_edge = [100, 1, 200, 2]
left_edge = [100, 1, 200, 2]
right_edge = [100, 1, 200, 2]
bottom_left_edge = [100, 1, 200, 2]
bottom_right_edge = [100, 1, 200, 2]

TOP_IMAGE = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)
LEFT_IMAGE = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)
RIGHT_IMAGE = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)
BOTTOM_LEFT_IMAGE = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)
BOTTOM_RIGHT_IMAGE = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)
FRAME = np.zeros([FULL_RESOLUTION[1], FULL_RESOLUTION[0], 3], np.uint8)


def top_matrix_compute(filename="top_matrix.txt"):
    global TOP_IMAGE
    global FRAME
    print("top_matrix_compute\n")
    if os.path.isfile(MATRIX_FOLDER + filename):
        os.remove(MATRIX_FOLDER + filename)
    top_image = cv2.imread(IMAGES_FOLDER + "top_corners.jpg")
    # 求取透视变换矩阵
    top_index = tools.read_index(filename=POINTS_FOLDER + 'top.txt', edge=top_edge)
    # print(top_index)
    origin_points = tools.read_origin_points(filename=POINTS_FOLDER + 'top_corners.json')
    # 像素坐标
    src_point = np.float32(np.empty([0, 2]))
    for i in top_index[top_index >= 0]:
        x = origin_points.get(str(i)).get('x')
        y = origin_points.get(str(i)).get('y')
        src_point = np.append(src_point, [[x, y], ], axis=0)
    # print(src_point)
    # 空间坐标
    dst_point = np.float32(np.empty([0, 2]))
    dst_point = np.append(dst_point, coordinates.top_coordinates, axis=0)
    dst_point = dst_point[top_index >= 0]
    # print(dst_point)
    print("\n")

    homography_top_list = []
    new_dst = []
    new_src = []
    for j in range(0, TOP_BLOCKS[0], 1):
        for i in range(0, len(dst_point)):
            if j + 1 >= dst_point[i][0] >= j:
                new_dst.append([dst_point[i][0].item(), dst_point[i][1].item()])
                new_src.append([src_point[i][0].item(), src_point[i][1].item()])
                continue
        new_src = np.float32(new_src)
        new_dst = np.float32(new_dst) * BLOCK_SIZE
        print(new_dst)
        print(len(new_dst))
        print("##")
        print(len(new_src))
        print(new_src)
        # 至少要4个点，一一对应，找到透视变换矩阵h
        homography_top, s = cv2.findHomography(new_src, new_dst, cv2.RANSAC, 30)
        homography_top_list.append(homography_top)
        with open(MATRIX_FOLDER + filename, 'a') as f:
            f.write(np.array2string(homography_top, separator=', ') + ',\n\n')
        # 输出透视变换矩阵
        print(homography_top)
        new_dst = []
        new_src = []
        # 透视变换
        print(top_image.shape)
        print("what?")
        top_processed = cv2.warpPerspective(top_image, homography_top, FULL_RESOLUTION)
        # 选定区域
        # TopImg = img_top
        print("结果的shape")
        print(top_processed.shape)
        # cv2.imshow('img_left', img_left)
        # cv2.waitKey()

        if j == 0:
            TOP_IMAGE = top_processed
        else:
            TOP_IMAGE[0:TOP_BLOCKS[1] * BLOCK_SIZE, j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = top_processed[
                                                                                           0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                                           j * BLOCK_SIZE:(
                                                                                                                  j + 1) * BLOCK_SIZE]
    FRAME[0:TOP_BLOCKS[1] * BLOCK_SIZE, 0:TOP_BLOCKS[0] * BLOCK_SIZE] = TOP_IMAGE[0:TOP_BLOCKS[1] * BLOCK_SIZE,
                                                                        0:TOP_BLOCKS[0] * BLOCK_SIZE]
    top_array = np.array(homography_top_list)
    result = TOP_IMAGE[0:TOP_BLOCKS[1] * BLOCK_SIZE, 0:TOP_BLOCKS[0] * BLOCK_SIZE]
    print(result.shape)
    cv2.imshow('result', result)
    cv2.imwrite(OUT_IMAGES_FOLDER + "top_out_image.jpg", result)
    print(top_array)
    cv2.waitKey()


def left_matrix_compute(filename="left_matrix.txt"):
    print("left_matrix_compute")
    global LEFT_IMAGE
    if os.path.isfile(MATRIX_FOLDER + filename):
        os.remove(MATRIX_FOLDER + filename)
    left_image = cv2.imread(IMAGES_FOLDER + "left_corners.jpg")
    # 求取透视变换矩阵
    # left透视变换矩阵
    left_index = tools.read_index(filename=POINTS_FOLDER + 'left.txt', edge=left_edge)
    # print(top_index)
    origin_points = tools.read_origin_points(filename=POINTS_FOLDER + 'left_corners.json')
    # 像素坐标
    src_point = np.float32(np.empty([0, 2]))
    for i in left_index[left_index >= 0]:
        x = origin_points.get(str(i)).get('x')
        y = origin_points.get(str(i)).get('y')
        src_point = np.append(src_point, [[x, y], ], axis=0)
    # print(src_point)
    # 空间坐标
    dst_point = np.float32(np.empty([0, 2]))
    dst_point = np.append(dst_point, coordinates.left_coordinates, axis=0)
    dst_point = dst_point[left_index >= 0]
    print(dst_point)
    print("------------------------------------------------------------------------------------------------")

    homography_left_list = []
    new_dst = []
    new_src = []
    for j in range(0, LEFT_BLOCKS[1], 1):
        for i in range(0, len(dst_point)):
            if j + 1 >= dst_point[i][1] - TOP_BLOCKS[1] >= j:
                new_dst.append([dst_point[i][0].item(), dst_point[i][1].item()])
                new_src.append([src_point[i][0].item(), src_point[i][1].item()])
                continue
        new_src = np.float32(new_src)
        new_dst = np.float32(new_dst) * BLOCK_SIZE
        print(new_dst)
        print(len(new_dst))
        print("##")
        print(len(new_src))
        print(new_src)
        # 至少要4个点，一一对应，找到透视变换矩阵h
        homography_left, s = cv2.findHomography(new_src, new_dst, cv2.RANSAC, 30)
        homography_left_list.append(homography_left)
        with open(MATRIX_FOLDER + filename, 'a') as f:
            f.write(np.array2string(homography_left, separator=', ') + ',\n\n')
        # 输出透视变换矩阵
        print(homography_left)
        new_dst = []
        new_src = []
        # 透视变换
        # print(left_image.shape)
        print("what?")
        img_left = cv2.warpPerspective(left_image, homography_left, FULL_RESOLUTION)
        # 选定区域
        print("结果的shape")
        print(img_left.shape)
        # cv2.imshow('img_left', img_left)
        # cv2.waitKey()

        if j == 0:
            LEFT_IMAGE = img_left
        else:
            LEFT_IMAGE[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
            0:LEFT_BLOCKS[0] * BLOCK_SIZE] = img_left[
                                             (j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
                                             0:LEFT_BLOCKS[0] * BLOCK_SIZE]
            # cv2.imshow("temp",LEFT_IMAGE)
            # cv2.waitKey(0)
    homography_left_array = np.array(homography_left_list)
    FRAME[TOP_BLOCKS[1] * BLOCK_SIZE:(TOP_BLOCKS[1] + LEFT_BLOCKS[1]) * BLOCK_SIZE,
    0:LEFT_BLOCKS[0] * BLOCK_SIZE] = LEFT_IMAGE[
                                     TOP_BLOCKS[1] * BLOCK_SIZE:(TOP_BLOCKS[1] + LEFT_BLOCKS[1]) * BLOCK_SIZE,
                                     0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    result = LEFT_IMAGE[TOP_BLOCKS[1] * BLOCK_SIZE:(TOP_BLOCKS[1] + LEFT_BLOCKS[1]) * BLOCK_SIZE,
             0:LEFT_BLOCKS[0] * BLOCK_SIZE]
    print(result.shape)
    cv2.imshow('left_result', result)
    cv2.imwrite(OUT_IMAGES_FOLDER + "left_out_image.jpg", result)
    print(homography_left_array)
    cv2.waitKey()


def right_matrix_compute(filename="right_matrix.txt"):
    print("right_matrix_compute")
    global FRAME, RIGHT_IMAGE
    if os.path.isfile(MATRIX_FOLDER + filename):
        os.remove(MATRIX_FOLDER + filename)
    right_image = cv2.imread(IMAGES_FOLDER + "right_corners.jpg")
    # 求取透视变换矩阵
    right_index = tools.read_index(filename=POINTS_FOLDER + 'right.txt', edge=right_edge)
    # print(right_index)
    origin_points = tools.read_origin_points(filename=POINTS_FOLDER + 'right_corners.json')
    # 像素坐标
    src_point = np.float32(np.empty([0, 2]))
    for i in right_index[right_index >= 0]:
        x = origin_points.get(str(i)).get('x')
        y = origin_points.get(str(i)).get('y')
        src_point = np.append(src_point, [[x, y], ], axis=0)
    # print(src_point)
    # 空间坐标
    dst_point = np.float32(np.empty([0, 2]))
    dst_point = np.append(dst_point, coordinates.right_coordinates, axis=0)
    dst_point = dst_point[right_index >= 0]
    # print(dst_point)
    print("\n")

    homography_right_list = []
    new_dst = []
    new_src = []
    for j in range(0, RIGHT_BLOCKS[1], 1):
        for i in range(0, len(dst_point)):
            if j + 1 >= dst_point[i][1] - TOP_BLOCKS[1] >= j:
                new_dst.append([dst_point[i][0].item(), dst_point[i][1].item()])
                new_src.append([src_point[i][0].item(), src_point[i][1].item()])
                continue
        new_src = np.float32(new_src)
        new_dst = np.float32(new_dst) * BLOCK_SIZE
        print(new_dst)
        print(len(new_dst))
        print("##")
        print(len(new_src))
        print(new_src)
        # 至少要4个点，一一对应，找到透视变换矩阵h
        homography_right, s = cv2.findHomography(new_src, new_dst, cv2.RANSAC, 30)
        homography_right_list.append(homography_right)
        with open(MATRIX_FOLDER + filename, 'a') as f:
            f.write(np.array2string(homography_right, separator=', ') + ',\n\n')
        # 输出透视变换矩阵
        print(homography_right)
        new_dst = []
        new_src = []
        # 透视变换
        print(right_image.shape)
        print("what?")
        right_processed = cv2.warpPerspective(right_image, homography_right, FULL_RESOLUTION)
        # 选定区域
        print("结果的shape")
        print(right_processed.shape)

        if j == 0:
            RIGHT_IMAGE = right_processed
        else:
            RIGHT_IMAGE[(j + TOP_BLOCKS[1]) * BLOCK_SIZE:(j + TOP_BLOCKS[1] + 1) * BLOCK_SIZE,
            (TOTAL_SIZE_BLOCKS[0] - RIGHT_BLOCKS[0]) * BLOCK_SIZE: TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE] = right_processed[
                                                                                                        (j + TOP_BLOCKS[
                                                                                                            1]) * BLOCK_SIZE:(
                                                                                                                                     j +
                                                                                                                                     TOP_BLOCKS[
                                                                                                                                         1] + 1) * BLOCK_SIZE,
                                                                                                        (
                                                                                                                TOTAL_SIZE_BLOCKS[
                                                                                                                    0] -
                                                                                                                RIGHT_BLOCKS[
                                                                                                                    0]) * BLOCK_SIZE:
                                                                                                        TOTAL_SIZE_BLOCKS[
                                                                                                            0] * BLOCK_SIZE]
            # cv2.imshow('img_left', RIGHT_IMAGE)
            # cv2.waitKey()
    # result = LEFT_IMG[0:8 * ratio, TOTAL_SIZE_BLOCKS[0] * ratio]
    FRAME[TOP_BLOCKS[1] * BLOCK_SIZE:(RIGHT_BLOCKS[1] + TOP_BLOCKS[1]) * BLOCK_SIZE,
    (TOTAL_SIZE_BLOCKS[0] - RIGHT_BLOCKS[0]) * BLOCK_SIZE: TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE] = RIGHT_IMAGE[TOP_BLOCKS[
                                                                                                              1] * BLOCK_SIZE:(
                                                                                                                                      RIGHT_BLOCKS[
                                                                                                                                          1] +
                                                                                                                                      TOP_BLOCKS[
                                                                                                                                          1]) * BLOCK_SIZE,
                                                                                                (TOTAL_SIZE_BLOCKS[0] -
                                                                                                 RIGHT_BLOCKS[
                                                                                                     0]) * BLOCK_SIZE:
                                                                                                TOTAL_SIZE_BLOCKS[
                                                                                                    0] * BLOCK_SIZE]
    homography_right_array = np.array(homography_right_list)
    result = RIGHT_IMAGE[TOP_BLOCKS[1] * BLOCK_SIZE:(RIGHT_BLOCKS[1] + TOP_BLOCKS[1]) * BLOCK_SIZE,
             (TOTAL_SIZE_BLOCKS[0] - RIGHT_BLOCKS[0]) * BLOCK_SIZE: TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE]
    print(result.shape)
    cv2.imshow('right_result', result)
    cv2.imwrite(OUT_IMAGES_FOLDER + "right_out_image.jpg", result)
    print(homography_right_array)
    cv2.waitKey()


def bottom_left_matrix_compute(filename="bottom_left_matrix.txt"):
    print("bottom_left_matrix_compute")
    global BOTTOM_LEFT_IMAGE
    global FRAME
    if os.path.isfile(MATRIX_FOLDER + filename):
        os.remove(MATRIX_FOLDER + filename)
    bottom_left_image = cv2.imread(IMAGES_FOLDER + "bottom_left_corners.jpg")
    # 求取透视变换矩阵
    bottom_left_index = tools.read_index(filename=POINTS_FOLDER + 'bottom_left.txt', edge=bottom_left_edge)
    origin_points = tools.read_origin_points(filename=POINTS_FOLDER + 'bottom_left_corners.json')
    # 像素坐标
    src_point = np.float32(np.empty([0, 2]))
    for i in bottom_left_index[bottom_left_index >= 0]:
        x = origin_points.get(str(i)).get('x')
        y = origin_points.get(str(i)).get('y')
        src_point = np.append(src_point, [[x, y], ], axis=0)
    # print(src_point)
    # 空间坐标
    dst_point = np.float32(np.empty([0, 2]))
    dst_point = np.append(dst_point, coordinates.bottom_left_coordinates, axis=0)
    dst_point = dst_point[bottom_left_index >= 0]
    # print(dst_point)
    print("\n")

    homography_bottom_left_list = []
    new_dst = []
    new_src = []
    for j in range(0, BOTTOM_LEFT_BLOCKS[0], 1):
        for i in range(0, len(dst_point)):
            if j + 1 >= dst_point[i][0] >= j:
                new_dst.append([dst_point[i][0].item(), dst_point[i][1].item()])
                new_src.append([src_point[i][0].item(), src_point[i][1].item()])
                continue
        new_src = np.float32(new_src)
        new_dst = np.float32(new_dst) * BLOCK_SIZE
        print(new_dst)
        print(len(new_dst))
        print("##")
        print(len(new_src))
        print(new_src)
        # 至少要4个点，一一对应，找到透视变换矩阵h
        homography_bottom_left, s = cv2.findHomography(new_src, new_dst, cv2.RANSAC, 30)
        homography_bottom_left_list.append(homography_bottom_left)
        with open(MATRIX_FOLDER + filename, 'a') as f:
            f.write(np.array2string(homography_bottom_left, separator=', ') + ',\n\n')
        # 输出透视变换矩阵
        print(homography_bottom_left)
        new_dst = []
        new_src = []
        # 透视变换
        print(bottom_left_image.shape)
        print("what?")
        bottom_left_processed = cv2.warpPerspective(bottom_left_image, homography_bottom_left, FULL_RESOLUTION)
        # 选定区域
        print("结果的shape")
        print(bottom_left_processed.shape)
        # cv2.imshow('img_left', img_left)
        # cv2.waitKey()

        if j == 0:
            BOTTOM_LEFT_IMAGE = bottom_left_processed
        else:
            BOTTOM_LEFT_IMAGE[
            (TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
            j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE] = bottom_left_processed[
                                                   (TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:
                                                   TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
                                                   j * BLOCK_SIZE:(j + 1) * BLOCK_SIZE]
            # cv2.imshow("WHAT", BOTTOM_LEFT_IMAGE)
            # cv2.waitKey(0)
    FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
    0:BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE] = BOTTOM_LEFT_IMAGE[
                                            (TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:
                                            TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
                                            0:BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE]
    bottom_left_array = np.array(homography_bottom_left_list)
    result = BOTTOM_LEFT_IMAGE[
             (TOTAL_SIZE_BLOCKS[1] - BOTTOM_LEFT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
             0:BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE]
    print(result.shape)
    cv2.imshow('result', result)
    cv2.imwrite(OUT_IMAGES_FOLDER + "bottom_left_out_image.jpg", result)
    print(bottom_left_array)
    cv2.waitKey()


def bottom_right_matrix_compute(filename="bottom_right_matrix.txt"):
    print("bottom_right_matrix_compute")
    global BOTTOM_RIGHT_IMAGE
    global FRAME
    if os.path.isfile(MATRIX_FOLDER + filename):
        os.remove(MATRIX_FOLDER + filename)
    bottom_right_image = cv2.imread(IMAGES_FOLDER + "bottom_right_corners.jpg")
    # 求取透视变换矩阵
    bottom_right_index = tools.read_index(filename=POINTS_FOLDER + 'bottom_right.txt', edge=bottom_right_edge)
    origin_points = tools.read_origin_points(filename=POINTS_FOLDER + 'bottom_right_corners.json')
    # 像素坐标
    src_point = np.float32(np.empty([0, 2]))
    for i in bottom_right_index[bottom_right_index >= 0]:
        x = origin_points.get(str(i)).get('x')
        y = origin_points.get(str(i)).get('y')
        src_point = np.append(src_point, [[x, y], ], axis=0)
    # print(src_point)
    # 空间坐标
    dst_point = np.float32(np.empty([0, 2]))
    dst_point = np.append(dst_point, coordinates.bottom_right_coordinates, axis=0)
    dst_point = dst_point[bottom_right_index >= 0]
    # print(dst_point)
    print("\n")

    homography_bottom_right_list = []
    new_dst = []
    new_src = []
    for j in range(0, BOTTOM_RIGHT_BLOCKS[0], 1):
        for i in range(0, len(dst_point)):
            if j + 1 >= dst_point[i][0] - BOTTOM_LEFT_BLOCKS[0] >= j:
                new_dst.append([dst_point[i][0].item(), dst_point[i][1].item()])
                new_src.append([src_point[i][0].item(), src_point[i][1].item()])
                continue
        new_src = np.float32(new_src)
        new_dst = np.float32(new_dst) * BLOCK_SIZE
        print(new_dst)
        print(len(new_dst))
        print("##")
        print(len(new_src))
        print(new_src)
        # 至少要4个点，一一对应，找到透视变换矩阵h
        homography_bottom_right, s = cv2.findHomography(new_src, new_dst, cv2.RANSAC, 30)
        homography_bottom_right_list.append(homography_bottom_right)
        with open(MATRIX_FOLDER + filename, 'a') as f:
            f.write(np.array2string(homography_bottom_right, separator=', ') + ',\n\n')
        # 输出透视变换矩阵
        print(homography_bottom_right)
        new_dst = []
        new_src = []
        # 透视变换
        print(bottom_right_image.shape)
        print("what?")
        bottom_right_processed = cv2.warpPerspective(bottom_right_image, homography_bottom_right, FULL_RESOLUTION)
        # 选定区域
        print("结果的shape")
        print(bottom_right_processed.shape)
        # cv2.waitKey()

        if j == 0:
            BOTTOM_RIGHT_IMAGE = bottom_right_processed
        else:
            BOTTOM_RIGHT_IMAGE[
            (TOTAL_SIZE_BLOCKS[1] - BOTTOM_RIGHT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
            (BOTTOM_LEFT_BLOCKS[0] + j) * BLOCK_SIZE:(BOTTOM_LEFT_BLOCKS[
                                                          0] + j + 1) * BLOCK_SIZE] = bottom_right_processed[(
                                                                                                                     TOTAL_SIZE_BLOCKS[
                                                                                                                         1] -
                                                                                                                     BOTTOM_RIGHT_BLOCKS[
                                                                                                                         1]) * BLOCK_SIZE:
                                                                                                             TOTAL_SIZE_BLOCKS[
                                                                                                                 1] * BLOCK_SIZE,
                                                                                      (BOTTOM_LEFT_BLOCKS[
                                                                                           0] + j) * BLOCK_SIZE:(
                                                                                                                        BOTTOM_LEFT_BLOCKS[
                                                                                                                            0] + j + 1) * BLOCK_SIZE]
    FRAME[(TOTAL_SIZE_BLOCKS[1] - BOTTOM_RIGHT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
    BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE] = BOTTOM_RIGHT_IMAGE[(TOTAL_SIZE_BLOCKS[1] -
                                                                                                BOTTOM_RIGHT_BLOCKS[
                                                                                                    1]) * BLOCK_SIZE:
                                                                                               TOTAL_SIZE_BLOCKS[
                                                                                                   1] * BLOCK_SIZE,
                                                                            BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE:
                                                                            TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE]
    bottom_right_array = np.array(homography_bottom_right_list)
    result = BOTTOM_RIGHT_IMAGE[
             (TOTAL_SIZE_BLOCKS[1] - BOTTOM_RIGHT_BLOCKS[1]) * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[1] * BLOCK_SIZE,
             BOTTOM_LEFT_BLOCKS[0] * BLOCK_SIZE:TOTAL_SIZE_BLOCKS[0] * BLOCK_SIZE]
    print(result.shape)
    cv2.imshow('bottom_right_result', result)
    cv2.imwrite(OUT_IMAGES_FOLDER + "bottom_right_out_image.jpg", result)
    print(bottom_right_array)
    cv2.waitKey()


if __name__ == '__main__':
    # top_matrix_compute()
    # left_matrix_compute()
    # right_matrix_compute()
    bottom_left_matrix_compute()
    # bottom_right_matrix_compute()
    cv2.imshow("FRAME", FRAME)
    cv2.waitKey(0)
