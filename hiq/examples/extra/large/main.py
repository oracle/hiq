import time


def func1(x, y, df):
    time.sleep(1.5)
    func2(y)


def func2(y):
    time.sleep(2.5)


def main(x, y, df, lst, bytes, *args, **kwargs):
    func1(x, y, df)
