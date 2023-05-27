import cv2
import numpy as np
import json
import os
import glob

IMAGES_FOLDER = './corners_images'


# 输入图片名、输出json文件名、输出图片名
def corners_finder(input_filename='', json_filename="", image_filename="", max_corners=450, min_distance=18,
                   text_size=0.3):
    # 读取图片
    img1 = cv2.imread(input_filename)

    img = cv2.resize(img1, (1280, 720), interpolation=cv2.INTER_AREA)  # 指定720P透视变换
    # 设置参数
    quality_level = 0.01  # 表示角点的最小质量
    block_size = 3  # 表示计算角点时使用的窗口大小

    # 寻找角点
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, max_corners, quality_level, min_distance, blockSize=block_size, mask=None,
                                      useHarrisDetector=True, k=0.04)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
    corners = corners.astype(np.float64)

    print("testm")
    print(corners)
    print(corners[0][0])

    # 构建保存结果的字典
    result_dict = {}
    for i, corner in enumerate(corners):
        x, y = corner.ravel()
        # x, y = np.round(x, 12), np.round(y, 12)  # 将像素位置四舍五入到小数点后12位
        result_dict[str(i)] = {"x": float(x), "y": float(y)}

    # 将结果保存为json文件
    with open(f'./points/{json_filename}', 'w') as f:
        json.dump(result_dict, f, indent=4)

    # 显示角点
    for i in range(len(corners)):
        x, y = corners[i][0]
        cv2.circle(img, (int(x), int(y)), 2, (0, 255, 0), -1)
        cv2.putText(img, str(i).replace("8", "+").replace("6", "~").replace("3", "-"), (int(x) - 13, int(y) + 13),
                    cv2.FONT_HERSHEY_SIMPLEX, text_size, (255, 0, 0), 1)

    # 显示结果
    cv2.imshow(image_filename, img)
    cv2.imwrite(f'./out_images/{image_filename}', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def process(img_name="", m_corners=450, m_distance=15, t_size=0.3):
    head = img_name[:img_name.index('.') - 12]  # -12消除_undistorted后缀
    # 测试
    print("mby")
    print(t_size)
    corners_finder(IMAGES_FOLDER + "/" + img_name, head + "_corners.json",
                   head + "_corners.jpg", m_corners, m_distance, t_size)


if __name__ == '__main__':
    max_corners = [400, 450, 500, 600, 700, 800]  # 图片最大角点数挡位
    min_distance = [10, 12, 15, 18, 20]  # 角点最小间距挡位
    text_size = [0.3, 0.35, 0.4]  # 文字大小挡位，用于精确定位点，更改此项不影响角点的查找结果与顺序
    # process("1.jpg", max_corners[3], min_distance[4], text_size[2])
    process("top_undistorted.jpg", max_corners[4], 18, text_size[2])  # 18
    process("left_undistorted.jpg", max_corners[4], 16, text_size[0])  # 16
    process("right_undistorted.jpg", max_corners[4], 18, text_size[0])  # 18
    process("bottom_left_undistorted.jpg", max_corners[4], 15, text_size[0])  # 15
    process("bottom_right_undistorted.jpg", max_corners[4], 14, text_size[0])  # 14
    exit()
    for filename in image_names:
        for path in image_paths:
            name = os.path.basename(path)
            image_names.append(name)
        print(image_names)
        image_paths = glob.glob(os.path.join(IMAGES_FOLDER, '*.jpg'))
        image_names = []
        head = filename[:filename.index('.jpg')]
        print("current image: ", head)
        if head == "top":
            corners_finder(IMAGES_FOLDER + "/" + filename, f"{head}_points.json",
                           f"{head}_corners.jpg", max_corners[0], min_distance[0])
        elif head == "bottom":
            corners_finder(IMAGES_FOLDER + "/" + filename, f"{head}_points.json",
                           f"{head}_corners.jpg", max_corners[1], min_distance[1])
        elif head == "left":
            corners_finder(IMAGES_FOLDER + "/" + filename, f"{head}_points.json",
                           f"{head}_corners.jpg", max_corners[2], min_distance[2])
        elif head == "right":
            corners_finder(IMAGES_FOLDER + "/" + filename, f"{head}_points.json",
                           f"{head}_corners.jpg", max_corners[3], min_distance[3])

# cv2.goodFeaturesToTrack()
# - `gray_src`：输入的灰度图像。
# - `corners`：输出的角点坐标矩阵，每个角点坐标为一个二元组 (x, y)。
# - `max_corners`：最多返回的角点数量。
# - `qualityLevel`：角点的最小质量，用于筛选角点，范围在 [0, 1] 之间。
# - `minDistance`：角点之间的最小距离，小于该距离的角点将被忽略。
# - `mask`：掩码图像，与输入图像大小相同，用于指定感兴趣区域或排除某些区域。
# - `blockSize`：计算角点时使用的窗口大小。
# - `useHarrisDetector`：是否使用 Harris 角点检测器。
# - `k`：Harris 角点检测器的自由参数。

# 尝试自动排序，效果不佳
# corners_with_indices = np.zeros((corners.shape[0], 3))
#
# # Store the pixel coordinates and their indices in the new array
# corners_with_indices[:, :2] = corners.reshape(-1, 2)
# corners_with_indices[:, 2] = np.arange(corners.shape[0])
#
# # Sort the corners by their y-coordinate first, then by their x-coordinate
# corners_with_indices = corners_with_indices[corners_with_indices[:, 1].argsort()]
# corners_with_indices = corners_with_indices[corners_with_indices[:, 0].argsort(kind='mergesort')]
#
# # Remove the pixel coordinates and keep only the indices
# corners_indices = corners_with_indices[:, 2].astype(int)
#
# # Create a new array with the corners sorted by their indices
# corners_sorted = corners[corners_indices]
#
# # Print the sorted corners
# print(corners_sorted)
# # corners_copy = corners.copy()
# # corners_copy = corners_copy.reshape(-1, 2)
# # corners_copy = corners_copy[np.lexsort((corners_copy[:, 0], corners_copy[:, 1]))]
# #
# # # 获取角点在corners中的下标，并存储在corners_array中
# # corners_array = corners_copy.reshape(-1, 1, 2)
# #
# # corners_index = np.argsort(corners_copy[:, 1] * img.shape[1] + corners_copy[:, 0])
# # corners_array = corners_array[corners_index]
#
# #
# # np.set_printoptions(precision=12)
# print(corners[0][0])
# # print(corners_copy[0])
# # print(corners_copy[1])
# print("testb")
# print(corners_indices)
# # print(corners_array[0][0])
# # print(corners_array)
