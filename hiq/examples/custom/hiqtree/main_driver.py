import os
import hiq
from inspect import currentframe as cf
from hiq.constants import *


class MyHiQ(hiq.HiQSimple):
    def custom(self):
        def __my_main(data={}, model={}, *args, **kwargs) -> int:
            img_path = data["img_path"] if "img_path" in data else None
            img_size = data["img_size"] if "img_size" in data else None

            @self.inserter_with_extra(extra={"img": img_path, "size": img_size})
            def __z(data, model):
                return self.o_main(data=data, model=model)

            return __z(data, model)

        self.o_main = hiq.mod("main").main
        hiq.mod("main").main = __my_main

    def custom_disable(self):
        hiq.mod("main").main = self.o_main


def run_main():
    with hiq.HiQStatusContext():
        driver = MyHiQ()
        hiq.mod("main").main(
            model={"data": "abc"},
            data={"img_path": "/tmp/hello.jpg", "from": "driver", "img_size": 1024},
        )
        driver.show()


if __name__ == "__main__":
    run_main()
