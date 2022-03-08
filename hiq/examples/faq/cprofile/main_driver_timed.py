import hiq
import time
import cProfile


def run_main():
    driver = hiq.HiQLatency(
        hiq_table_or_path=[
            ["main", "", "main", "main"],
            ["main", "", "func1", "func1"],
            ["main", "", "func2", "func2"],
        ]
    )
    start = time.monotonic()
    with cProfile.Profile() as pr:
        hiq.mod("main").main()
    print(time.monotonic() - start)
    pr.dump_stats("result.pstat")
    driver.show()


if __name__ == "__main__":
    run_main()
