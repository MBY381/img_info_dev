import cv2
import numpy as np


# 检测角点的函数
def find_corners(img, board_size=(9, 9)):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, board_size,
                                             cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (9, 9), (-1, -1),
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        return corners2
    return None


# 获取标定板的三维坐标
def get_objpoints(board_size=(9, 9), square_size=25):
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
    objp = objp * square_size
    print("ob", objp)
    return objp


# 进行相机标定
def calibrate_camera(images, board_size=(9, 9), square_size=25):
    objpoints = []  # 三维坐标
    imgpoints = []  # 二维坐标
    objp = get_objpoints(board_size, square_size)

    for img in images:
        corners = find_corners(img, board_size)
        if corners is not None:
            objpoints.append(objp)
            imgpoints.append(corners)

    print('检测到 %d 张含有角点的图片。' % len(objpoints))

    if len(objpoints) > 0:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,
                                                           images[0].shape[:2], None, None)
        return ret, mtx, dist, rvecs, tvecs
    else:
        return None


# 读取图片
images = []
for i in range(1, 41):
    img_path = './ewimages' + '/img' + str(i) + '.jpg'
    img = cv2.imread(img_path)
    if img is None:
        print('找不到图像：%s' % img_path)
    else:
        # print('添加了一个图片')
        # cv2.imshow('图片展示',img)
        # cv2.waitKey(200)
        images.append(img)

# 进行相机标定
if len(images) > 0:
    result = calibrate_camera(images)
    if result is not None:
        ret, mtx, dist, rvecs, tvecs = result
        # 打印相机内参和畸变参数
        print('内参：\n', mtx)
        print('畸变参数：\n', dist)
        img = cv2.imread('./testimg' + '/img.png')
        resized = cv2.resize(img, (640, 360), interpolation=cv2.INTER_AREA)
        img_undistorted = cv2.undistort(resized, mtx, dist, None, None)
        # 显示去畸变后的图像
        cv2.imshow('result1', img_undistorted)
        img2 = cv2.imread('./testimg' + '/img.png')

        cv2.imshow("original", img2)
        mtx2 = np.float32([[197.8478, -1.7711, 302.2921], [0, 195.1688, 187.6430], [0, 0, 1]])
        dist2 = np.float32([-0.2805, 0.0646, -0.0059, 0.0024, -0.0025])
        img_undistorted2 = cv2.undistort(resized, mtx2, dist2, None, None)
        cv2.imshow("result", img_undistorted2)
        cv2.imwrite('./out_images/outframe.jpg', img_undistorted)
        cv2.waitKey(0)
    else:
        print('没有检测到任何角点，请检查标定板设置和图像是否正确。')
else:
    print('没有找到可以用于标定的图像。')
