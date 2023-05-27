import cv2

# 读取图像
img = cv2.imread("sample.png")
cv2.imshow("Cropped Image", img)
cv2.waitKey(0)
# 计算裁剪窗口的大小和位置
width, height, _ = img.shape
window_width = width // 3
window_height = int(window_width * 720 / 1280)
window_x = (width - window_width) // 2
window_y = (height - window_height) // 2

# 从原始图像中裁剪指定区域的子图像
cropped_img = img[0:window_x, 0:window_y]

# 调整子图像大小以匹配目标比例（1280x720）
resized_img = cv2.resize(cropped_img, (1280, 720))

# 显示裁剪后的图像
cv2.imshow("Cropped Image", resized_img)

# 保存裁剪后的图像
cv2.imwrite("cropped_image.png", resized_img)

# 等待按键操作，然后关闭所有窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
