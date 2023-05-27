import cv2

# 读取四合一图片
img = cv2.imread('frame.jpg')

# 获取四个小图像的宽和高
height, width, _ = img.shape
h, w = height // 2, width // 2

# 将四合一图片等分成四个小图，并展示出来
for i in range(2):
    for j in range(2):
        x, y = j * w, i * h
        crop_img = img[y:y + h, x:x + w]
        cv2.imshow("crop_{}{}".format(i, j), crop_img)
        cv2.imwrite("./crop_{}{}.jpg".format(i, j), crop_img)
        print(crop_img.shape)

cv2.waitKey(0)
cv2.destroyAllWindows()
