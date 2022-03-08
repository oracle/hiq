import hiq
import traceback, sys
from hiq.hiq_utils import get_global_hiq_status, set_global_hiq_status
from unittest.mock import MagicMock


def run_target_code():
    hiq_quadruple = [
        ("target_code", "", "func1", "f1"),
        ("target_code", "", "func2", "f2"),
        ("target_code", "", "func3", "f3"),
        ("target_code", "", "func4", "f4"),
    ]
    _g_tau_original = get_global_hiq_status()
    set_global_hiq_status(True)
    tau = hiq.HiQMemory(
        hiq_quadruple, attach_timestamp=True, max_hiq_size=1
    ).enable_hiq()

    for i in range(4):
        tau.get_tau_id = MagicMock(return_value=i)
        try:
            hiq.mod("target_code").fit(data={}, model=[i])
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    tau.show()

    tau.disable_hiq()
    print("-^" * 20, "disable HiQ", "-^" * 20)
    hiq.mod("target_code").fit(data={}, model=[i])
    set_global_hiq_status(_g_tau_original)


if __name__ == "__main__":
    run_target_code()
