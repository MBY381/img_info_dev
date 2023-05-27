import threading

def print1():
    print(1)

def print2():
    print(2)

def print3():
    print(3)

def print4():
    print(4)

def print5(num):
    print(num)

def create_threads():
    t1 = threading.Thread(target=print1)
    t2 = threading.Thread(target=print2)
    t3 = threading.Thread(target=print3)
    t4 = threading.Thread(target=print4)
    t5 = threading.Thread(target=print5, args=(5,))
    t1.start()
    t1.join()
    t2.start()
    t2.join()
    t3.start()
    t3.join()
    t4.start()
    t4.join()
    t5.start()
    t5.join()

if __name__ == '__main__':
    while True:
        create_threads()
        print("\nnn")
