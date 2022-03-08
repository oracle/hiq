import os

import hiq
from hiq.distributed import HiQOpenTelemetryContext, OtmExporterType

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with HiQOpenTelemetryContext(exporter_type=OtmExporterType.JAEGER_THRIFT):
        driver = hiq.HiQLatency(f"{here}/hiq.conf")
        hiq.mod("main").main()
        driver.show()


if __name__ == "__main__":
    run_main()
