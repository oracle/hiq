import time


def func1(model: dict, data: dict) -> int:
    time.sleep(1.5)
    r2 = func2(model, data)
    return r2 * 2


def func2(model: dict, data: dict) -> int:
    time.sleep(2.5)
    return len(data["img_path"])


def main(model: dict, data: dict) -> int:
    r = func1(model, data)
    return r


if __name__ == "__main__":
    res = main(model={"data": "abc"}, data={"img_path": "/tmp/hiq.jpg", "size": 1024})
    print(res)
