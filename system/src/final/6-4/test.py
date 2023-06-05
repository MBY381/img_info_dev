import cv2
import numpy as np

# 原图四个像素点坐标
src_points = np.array([
    [402.9012756347656, 311.4797058105469],
    [937.9232177734375, 343.68890380859375],
    [185.02967834472656, 460.3169250488281],
    [1134.5902099609375, 564.267333984375]
], dtype=np.float32)

# 目标图像的左上、右上、左下、右下四个角点的坐标
dst_points = np.array([
    [0, 0],
    [500, 0],
    [0, 150],
    [500, 150]
], dtype=np.float32)

# 计算透视变换矩阵
M = cv2.getPerspectiveTransform(src_points, dst_points)

# 加载原始图片
img = cv2.imread("top_corners.jpg")

# 进行透视变换
result = cv2.warpPerspective(img, M, (500, 150))

# 显示结果图片
cv2.imshow("result", result)
cv2.imwrite("result.jpg",result)
cv2.waitKey(0)
cv2.destroyAllWindows()
