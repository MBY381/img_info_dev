# 棋盘宽度和高度

# 打印棋盘坐标
def print_matrix(width=20, height=8, direction=True, sx=0, sy=0):
    if direction:
        for row in range(height):
            for col in range(width):
                x = col
                y = row
                print(f"[{x + sx}, {y + sy}]", end=",")
            print()
    else:
        for col in range(width):
            for row in range(height):
                x = col
                y = row
                print(f"[{x}, {y}]", end=",")
            print()
# 棋盘宽度和高度

# 打印棋盘坐标
def print_matrix1(width=20, height=8, x=0, y=0):
    for i in range(height - y):
        for j in range(width - x):
            print(f"[{x + j}, {y + i}]", end=",")
        print()



if __name__ == '__main__':
    print_matrix(11, 5, True, 10,24)



