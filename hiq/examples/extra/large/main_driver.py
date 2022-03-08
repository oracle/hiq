import os
import pickle

import hiq
import numpy as np
import pandas as pd
import torch
from hiq.constants import ExtraMetrics
from hiq.utils import write_file

here = os.path.dirname(os.path.realpath(__file__))


def large_data_processor(x, func_name=None) -> str:
    if func_name == "__main":
        if isinstance(x, tuple):
            write_file("/tmp/main.args.log", x[2].to_string(), append=True)
        elif isinstance(x, dict):
            with open("/tmp/main.args.pkl", "wb") as handle:
                pickle.dump(x, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return "..."
    else:
        return hiq.hiq_utils.func_args_handler(x, func_name)


def run_main():
    a = torch.rand(2000, 3)
    b = np.random.rand(3, 2000)
    df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))
    series = pd.date_range(start="2016-01-01", end="2020-12-31", freq="D")

    with hiq.HiQStatusContext(debug=False):
        with hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={ExtraMetrics.ARGS},
            func_args_handler=large_data_processor,
        ) as driver:
            hiq.mod("main").main(
                a,
                b,
                df,
                [1, 2, 3],
                b"abc",
                st=set({5, 6, 7}),
                dt={"a": 1},
                pd_time=series,
            )
            driver.show()


if __name__ == "__main__":
    run_main()
