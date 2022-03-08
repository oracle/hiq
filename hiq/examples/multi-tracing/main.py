import os
import time

from hiq.utils import download_from_http, execute_cmd, random_str


count = 0


def create_and_read(k=102400):
    _100mb_file = "/tmp/" + random_str() + ".bin"
    if not os.path.exists(_100mb_file):
        execute_cmd(
            f"dd if=/dev/zero of={_100mb_file} bs=1024 count={k}", verbose=False
        )
    with open(_100mb_file) as f:
        s = f.read()


def func1():
    global count
    if count == 5:
        create_and_read(1024 * 10)
        count += 1
        return
    elif count > 5:
        return
    count += 1
    func4()


def func2():
    time.sleep(0.1)
    func1()


def func3():
    time.sleep(0.12)
    func2()


def func4():
    if count == 0:
        create_and_read(1024 * 5)
    if count == 3:
        download_from_http(
            "https://www.gardeningknowhow.com/wp-content/uploads/2017/07/hardwood-tree.jpg",
            "/tmp/tree.jpg",
        )
    time.sleep(0.2)
    func2()
    func3()


def func5():
    time.sleep(0.24)


def fit(model="awesome_model", data="awesome_data"):
    time.sleep(0.35)
    func4()


def predict(model="awesome_model", data="awesome_data"):
    time.sleep(0.16)
    func5()


def main():
    for i in range(4):
        fit(data={}, model=[i])
        predict(model=f"awesome_model_{i}", data=i)


if __name__ == "__main__":
    main()
