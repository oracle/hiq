import os
import hiq

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    _ = hiq.HiQLatency(f"{here}/hiq.conf")
    hiq.mod("main").main()


if __name__ == "__main__":
    import time

    os.environ["LMK"] = "1"
    run_main()
    time.sleep(2)
