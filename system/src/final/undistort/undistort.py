import cv2
import numpy as np


MTX_CAMERA = np.float32([[197.8478, -1.7711, 302.2921], [0, 195.1688, 187.6430], [0, 0, 1]])
DIST_CAMERA = np.float32([-0.2805, 0.0646, -0.0059, 0.0024, -0.0025])
MTX_CAMERA1 = np.float32([[227.21233652, 0, 281.86422286], [0, 224.58459497, 210.10036974], [0, 0, 1]])  # 自己的 7
DIST_CAMERA1 = np.float32([-0.30034003, 0.07065534, -0.00831145, 0.01151889, -0.00699896])


def undistort_img(filename="", out=""):
    img = cv2.imread('./imgs/' + filename)
    resized = cv2.resize(img, (640, 360), interpolation=cv2.INTER_AREA)
    img_undistorted = cv2.undistort(resized, MTX_CAMERA1, DIST_CAMERA1, None, None)
    cv2.imshow("result", img_undistorted)
    cv2.imwrite('./out_images/' + out, img_undistorted)
    cv2.waitKey(0)


if __name__ == '__main__':
    undistort_img("top.jpg", "top_undistorted_my.jpg")
    # undistort_img("left.jpg", "left_undistorted.jpg")
    # undistort_img("right.jpg", "right_undistorted.jpg")
    # undistort_img("bottom_left.jpg", "bottom_left_undistorted.jpg")
    # undistort_img("bottom_right.jpg", "bottom_right_undistorted.jpg")