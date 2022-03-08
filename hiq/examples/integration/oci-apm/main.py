import time


def func1():
    time.sleep(1.5)
    print("func1")
    func2()


def func2():
    time.sleep(2.5)
    print("func2")


def main():
    func1()


if __name__ == "__main__":
    main()
