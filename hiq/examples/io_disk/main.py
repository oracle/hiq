import os, time
from hiq.utils import execute_cmd, random_str


def create_and_read(k=102400):
    time.sleep(2)
    _100mb_file = "/tmp/" + random_str() + ".bin"
    if not os.path.exists(_100mb_file):
        execute_cmd(
            f"dd if=/dev/zero of={_100mb_file} bs=1024 count={k}", verbose=False
        )
    with open(_100mb_file) as f:
        s = f.read()
        print(f"🥰 read file size: {len(s)} bytes")


def fun1():
    time.sleep(2)
    create_and_read(k=3)
    fun2()


def fun2():
    time.sleep(1)
    create_and_read(k=2)


def main():
    fun1()


if __name__ == "__main__":
    main()
