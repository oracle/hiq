import hiq
from hiq.constants import *


def run_main():
    with hiq.HiQStatusContext():
        driver = hiq.HiQLatency(
            hiq_table_or_path=[
                ["main", "", "main", "main"],
                ["main", "", "create_and_read", "cr"],
                ["main", "", "fun1", "f1"],
                ["main", "", "fun2", "f2"],
            ],
            extra_hiq_table=[TAU_TABLE_DIO_RD],
        )
        hiq.mod("main").main()
        driver.show()


if __name__ == "__main__":
    run_main()
