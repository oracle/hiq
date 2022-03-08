import time


def func1(x, y):
    time.sleep(1.5)
    func2(y)


def func2(y):
    time.sleep(2.5)


def main(x, y):
    func1(x, y)


if __name__ == "__main__":
    main(1, 2)
