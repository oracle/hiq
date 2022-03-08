import os
import hiq
import traceback, sys
from hiq.hiq_utils import (
    HiQIdGenerator,
    HiQStatusContext,
)

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with HiQStatusContext():
        for i in range(3):
            with hiq.HiQLatency(hiq_table_or_path=f"{here}/hiq.conf") as driver:
                try:
                    hiq.mod("main").fit(data={}, model=[i])
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                finally:
                    driver.show(show_key=True)


if __name__ == "__main__":
    run_main()
