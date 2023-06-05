import cv2

# 读取原始图像
img1 = cv2.imread('./imgs/bottom_left_undistorted.jpg')
img2 = cv2.imread('./imgs/bottom_right_undistorted.jpg')
img3 = cv2.imread('./imgs/left_undistorted.jpg')
img4 = cv2.imread('./imgs/right_undistorted.jpg')
img5 = cv2.imread('./imgs/top_undistorted.jpg')

# 将图像resize到720p大小（为了保持长宽比，这里使用cv2.INTER_AREA插值模式）
resized_img1 = cv2.resize(img1, (1280, 720), interpolation=cv2.INTER_AREA)
resized_img2 = cv2.resize(img2, (1280, 720), interpolation=cv2.INTER_AREA)
resized_img3 = cv2.resize(img3, (1280, 720), interpolation=cv2.INTER_AREA)
resized_img4 = cv2.resize(img4, (1280, 720), interpolation=cv2.INTER_AREA)
resized_img5 = cv2.resize(img5, (1280, 720), interpolation=cv2.INTER_AREA)

# 保存resize后的图像
cv2.imwrite('bottom_left_undistorted.jpg', resized_img1)
cv2.imwrite('bottom_right_undistorted.jpg', resized_img2)
cv2.imwrite('left_undistorted.jpg', resized_img3)
cv2.imwrite('right_undistorted.jpg', resized_img4)
cv2.imwrite('top_undistorted.jpg', resized_img5)
