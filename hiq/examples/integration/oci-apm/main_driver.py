import hiq
import os

from hiq.vendor_oci_apm import HiQOciApmContext

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with HiQOciApmContext(
        service_name="hiq_doc",
        span_name="main_driver",
    ):
        _ = hiq.HiQLatency(f"{here}/hiq.conf")
        hiq.mod("main").main()


if __name__ == "__main__":
    os.environ["TRACE_TYPE"] = "oci-apm"
    run_main()
