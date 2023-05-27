import json
import re

import numpy as np


def read_txt_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            # 使用正则表达式匹配数字
            nums = re.findall(r'\d+', line)
            # 将数字转换为整数，并添加到data中
            data.append([int(num) for num in nums])
    return data


# 读取txt文件中的角点索引id
def read_index1(filename='./points/index.txt'):
    data = np.loadtxt(filename, dtype=np.int)
    data = data.flatten()
    return data


def read_index(filename='./points/index.txt', edge=None):  # edge上下左右
    if edge is None:
        edge = [0, 0, 0, 0]
    data = np.loadtxt(filename, dtype=np.int)
    # print("txt")
    # print(data)
    # print("shape")
    # print(data.shape)
    # print(data.shape[0])
    for i in range(0, data.shape[0]):
        for j in range(0, data.shape[1]):
            if i <= edge[0] - 1 or i >= data.shape[0] - edge[1] or j <= edge[2] - 1 or j >= data.shape[1] - edge[3]:
                continue
            else:
                data[i][j] = -1
    # print(data)
    data = data.flatten()
    return data


def read_origin_points(filename='./points/demo.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        t = json.load(file)
        return t


if __name__ == '__main__':
    origin_points = read_origin_points(filename='./points/top2_points.json')
    while True:
        temp = input()
        # print(temp)
        # print([origin_points.get(temp).get('x'), origin_points.get(temp).get('y')])
