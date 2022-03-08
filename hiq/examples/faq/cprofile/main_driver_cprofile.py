import hiq
import time
import cProfile
from hiq.utils import SilencePrint


def run_main():
    driver = hiq.HiQLatency(
        hiq_table_or_path=[
            ["main", "", "main", "main"],
            ["main", "", "func1", "func1"],
            ["main", "", "func2", "func2"],
        ]
    )
    # driver.disable_hiq()
    m = hiq.mod("main")
    with cProfile.Profile() as pr:
        start = time.monotonic()
        m.main()
        end = time.monotonic()
    print(end - start)
    pr.dump_stats("result.pstat")
    driver.show()


if __name__ == "__main__":
    run_main()
