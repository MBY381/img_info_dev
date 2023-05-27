import threading


def print1():
    print(1)


def print2():
    print(2)


def print3():
    print(3)


def print4():
    print(4)


def print5():
    print(5)


# 定义一个线程函数用于执行指定的函数，并等待其他线程执行完毕
def run_thread(func, barrier):
    func()
    # 等待其他线程也执行完毕
    barrier.wait()


# 定义一个函数用于创建和启动多个线程
def run_threads(functions):
    # 创建一个同步屏障对象，用于同步多个线程的执行
    barrier = threading.Barrier(len(functions))

    # 创建并启动每个线程
    threads = []
    for func in functions:
        t = threading.Thread(target=run_thread, args=(func, barrier))
        t.start()
        threads.append(t)

    # 主线程等待所有子线程结束
    for t in threads:
        t.join()


# 要执行的函数列表
functions = [print1, print2, print3, print4, print5]

if __name__ == '__main__':
    while True:
        run_threads(functions)
        print("\nnn")
