import threading
from concurrent.futures import ThreadPoolExecutor

import time

executor = ThreadPoolExecutor(max_workers=5)


def print1(num):
    print(num)


def print2(num):
    print(num)


def print3(num):
    print(num)


def print4(num):
    print(num)


def print5(num):
    print(num)


def execute():
    try:
        # 提交五个任务
        executor.submit(print1)
        executor.submit(print2)
        executor.submit(print3)
        executor.submit(print4)
        executor.submit(print5("wdcm"))
    except:
        print("出错啦")


if __name__ == '__main__':
    start = time.time()
    execute()
    now = time.time()
    print("耗费时间：\n")
    print(now - start)
