import hiq
import os

from hiq.distributed import HiQOpenTelemetryContext, OtmExporterType

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with HiQOpenTelemetryContext(exporter_type=OtmExporterType.ZIPKIN_JSON):
        _ = hiq.HiQLatency(f"{here}/hiq.conf")
        hiq.mod("main").main()


if __name__ == "__main__":
    run_main()
