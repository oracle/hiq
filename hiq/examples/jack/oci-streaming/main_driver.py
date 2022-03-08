import os
import hiq
from hiq.hiq_utils import HiQIdGenerator

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext():
        driver = hiq.HiQLatency(f"{here}/hiq.conf", max_hiq_size=0)
        for _ in range(4):
            driver.get_tau_id = HiQIdGenerator()
            hiq.mod("main").main()
            driver.show()


if __name__ == "__main__":
    import time

    os.environ["JACK"] = "1"
    os.environ["HIQ_OCI_STREAMING"] = "1"
    os.environ[
        "OCI_STM_END"
    ] = "https://cell-1.streaming.us-phoenix-1.oci.oraclecloud.com"
    os.environ[
        "OCI_STM_OCID"
    ] = "ocid1.stream.oc1.phx.amaaaaaa74akfsaawjmfsaeepurksns4oplsi5tobleyhfuxfqz24vc42k7q"

    run_main()
    time.sleep(2)
