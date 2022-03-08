import logging
import os

import hiq

here = os.path.dirname(os.path.realpath(__file__))


LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
    filename="/tmp/lmk.log", filemode="w", format=LOG_FORMAT, level=logging.INFO
)

logger = logging.getLogger()


def run_main():
    _ = hiq.HiQLatency(f"{here}/hiq.conf", lmk_logger=logger)
    hiq.mod("main").main()


if __name__ == "__main__":
    import time

    os.environ["LMK"] = "1"
    run_main()
    time.sleep(2)
