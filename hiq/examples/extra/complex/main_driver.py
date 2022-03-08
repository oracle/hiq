import hiq
import os
import numpy as np
import pandas as pd
import torch
from hiq.constants import ExtraMetrics

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    a = torch.rand(2000, 3)
    b = np.random.rand(3, 2000)
    df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))
    series = pd.date_range(start="2016-01-01", end="2020-12-31", freq="D")

    with hiq.HiQStatusContext(debug=False):
        with hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={ExtraMetrics.ARGS},
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
