import hiq
from hiq.constants import *


def run_main():
    with hiq.HiQStatusContext():
        driver = hiq.HiQLatency(
            hiq_table_or_path=[
                ["main", "", "main", "main"],
                ["main", "", "func1", "func1"],
                ["main", "", "func2", "func2"],
                ["main", "", "func3", "func3"],
                ["main", "", "func4", "func4"],
                ["main", "", "func5", "func5"],
            ],
            extra_hiq_table=[TAU_TABLE_NIO_GET],
        )
        hiq.mod("main").main()
        driver.show()


if __name__ == "__main__":
    run_main()
