import time


def func1():
    time.sleep(1.5)
    print("func1")
    y = bytearray(512000000)
    return func2(), y


def func2():
    time.sleep(2.5)
    print("func2")
    x = bytearray(512000000)
    return x


def main():
    return func1()


if __name__ == "__main__":
    main()
