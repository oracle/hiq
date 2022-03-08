import hiq
import os
import time
import random
from prometheus_client import start_http_server

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext():
        start_http_server(8681)
        count = 0
        while count < 10:
            with hiq.HiQLatency(f"{here}/hiq.conf") as driver:
                hiq.mod("main").main()
                driver.show()
            time.sleep(random.random())
            count += 1


if __name__ == "__main__":
    os.environ["TRACE_TYPE"] = "prometheus"
    run_main()
