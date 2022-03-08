import os
import hiq
from inspect import currentframe as cf
from hiq.constants import *


class MyHiQ(hiq.HiQSimple):
    def custom(self):
        @self.inserter
        def __my_main(data={}, model={}) -> int:
            if "img_path" in data:
                print(f"🌴 print log for img_path: {data['img_path']}")
            if "img_size" in data:
                print(f"🌴 print log for img_size: {data['img_size']}")
            return self.o_main(data=data, model=model)

        self.o_main = hiq.mod("main").main
        hiq.mod("main").main = __my_main

    def custom_disable(self):
        hiq.mod("main").main = self.o_main


def run_main():
    with hiq.HiQStatusContext():
        _ = MyHiQ()
        hiq.mod("main").main(
            model={"data": "abc"}, data={"img_path": "/tmp/hello.jpg", "img_size": 1024}
        )


if __name__ == "__main__":
    run_main()
