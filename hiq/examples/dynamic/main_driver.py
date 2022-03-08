import hiq
import time


def run_main():
    # create an `hiq.HiQLatency` object and HiQ is enabled by default
    with hiq.HiQStatusContext():
        driver = hiq.HiQLatency(
            hiq_table_or_path=[
                ["main", "", "main", "main"],
                ["main", "", "func1", "func1"],
                ["main", "", "func2", "func2"],
            ]
        )
        print("*" * 20, "HiQ is enabled", "*" * 20)
        start = time.time()
        hiq.mod("main").main()
        print(f"{time.time()-start} second")
        driver.show()

        # disable HiQ in `driver`
        print("*" * 20, "disable HiQ", "*" * 20)
        driver.disable_hiq(reset_trace=True)
        start = time.time()
        hiq.mod("main").main()
        print(f"{time.time()-start} second")
        driver.show()

        # enable HiQ in `driver` again
        print("*" * 20, "re-enable HiQ", "*" * 20)
        driver.enable_hiq(reset_trace=True)
        start = time.time()
        hiq.mod("main").main()
        print(f"{time.time()-start} second")
        driver.show()


if __name__ == "__main__":
    run_main()
