import hiq
import os
from hiq.constants import ExtraMetrics

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext(debug=False):
        driver1 = hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={ExtraMetrics.FILE},
        )
        hiq.mod("main").main(1, 2)
        driver1.show()
        driver1.disable_hiq()

        driver2 = hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={ExtraMetrics.FUNC},
        )
        hiq.mod("main").main(1, 2)
        driver2.show()
        driver2.disable_hiq()

        driver3 = hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={ExtraMetrics.ARGS},
        )
        hiq.mod("main").main(1, 2)
        driver3.show()
        driver3.disable_hiq()

        driver4 = hiq.HiQLatency(
            f"{here}/hiq.conf",
            extra_metrics={
                ExtraMetrics.FILE,
                ExtraMetrics.FUNC,
                ExtraMetrics.ARGS,
            },
        )
        hiq.mod("main").main(1, 2)
        driver4.show()


if __name__ == "__main__":
    run_main()
