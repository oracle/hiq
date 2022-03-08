import os
import time

from hiq.vendor_oci_apm import HiQOciApmContext


def fun():
    with HiQOciApmContext(
        service_name="hiq_test_apm",
        span_name="fun_test",
    ):
        time.sleep(5)
        print("hello")


if __name__ == "__main__":
    os.environ["TRACE_TYPE"] = "oci-apm"
    fun()
