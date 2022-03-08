import hiq
import os

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext(debug=True):
        with hiq.HiQLatency(f"{here}/hiq.conf") as driver:
            hiq.mod("main").main()
            driver.show()


if __name__ == "__main__":
    run_main()
