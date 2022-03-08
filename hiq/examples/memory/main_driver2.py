import hiq
import os
from hiq.constants import KEY_MEMORY, FORMAT_DATETIME

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext():
        driver = hiq.HiQMemory(f"{here}/hiq.conf", attach_timestamp=True)
        hiq.mod("main").main()
        driver.get_metrics(metrics_key=KEY_MEMORY)[0].show()


if __name__ == "__main__":
    run_main()
