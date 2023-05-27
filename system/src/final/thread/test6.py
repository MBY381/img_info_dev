import threading
import time


# 定义五个打印函数
def print1(num):
    print("print1: ")


def print2(num):
    print("print2: ")


def print3(num):
    print("print3: ")


def print4(num):
    print("print4: ")


def print5(num):
    print("print5: ")
    print(num)


# 定义一个计数变量
cnt = 0

# 定义一个条件变量
cond = threading.Condition()

# 定义一个 Barrier，用于同步线程开始的时间
barrier = threading.Barrier(5)


# 定义一个检测计数变量的线程
def check_cnt():
    global cnt
    while True:
        print("what>")
        if cnt == 5:
            with cond:
                # 计数器达到 5，进入等待状态
                cond.wait()
                # 等待结束，进行一些操作
                cond.notify()
            # 改变 Barrier 的状态，让所有线程再次同时开始
            barrier.reset()
        # 睡眠一段时间再继续检测计数器
        time.sleep(0.01)


# 预先创建好检测计数器的线程并启动
t_check = threading.Thread(target=check_cnt)
t_check.start()


# 定义一个包装函数，用于在每个函数执行一次之后再更新参数值
def run_once(func, num):
    global cnt
    func(num)
    with cond:
        # 增加计数器的值
        cnt += 1
        # 如果计数器达到 5，唤醒等待的线程
        if cnt == 5:
            print("wdnmd")
            cnt = 0
    barrier.wait()


    # 等待其他线程执行完毕

    return num


# 定义一个函数用于循环执行指定的函数
def run_func(func, num):
    while True:
        num = run_once(func, num)


# 创建并启动每个线程
threads = []
for i, func in enumerate([print1, print2, print3, print4, print5]):
    t = threading.Thread(target=run_func, args=(func, i + 1))
    t.start()
    threads.append(t)

# 主线程等待所有子线程结束
for t in threads:
    t.join()

# 等待检测计数器的线程结束
t_check.join()
