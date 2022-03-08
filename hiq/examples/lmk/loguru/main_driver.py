import os

import hiq
from loguru import logger

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    _ = hiq.HiQLatency(
        f"{here}/hiq.conf", lmk_logger=logger, lmk_path="/tmp/lmk_guru.log"
    )
    hiq.mod("main").main()


if __name__ == "__main__":
    import time

    os.environ["LMK"] = "1"
    run_main()
    time.sleep(2)
