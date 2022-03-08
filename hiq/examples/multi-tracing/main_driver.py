import os
import hiq
import traceback, sys
from hiq.hiq_utils import get_global_hiq_status, set_global_hiq_status, HiQIdGenerator
from unittest.mock import MagicMock

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    _g_driver_original = get_global_hiq_status()
    set_global_hiq_status(True)
    driver = hiq.HiQLatency(
        hiq_table_or_path=f"{here}/hiq.conf",
        max_hiq_size=4,
    )

    for i in range(3):
        driver.get_tau_id = HiQIdGenerator()
        try:
            hiq.mod("main").fit(data={}, model=[i])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    driver.show(show_key=True)

    driver.disable_hiq()
    print("-^" * 20, "disable HiQ", "-^" * 20)
    hiq.mod("main").fit(data={}, model=[i])
    set_global_hiq_status(_g_driver_original)


if __name__ == "__main__":
    run_main()
