import hiq
import os

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with hiq.HiQStatusContext():
        driver = hiq.HiQLatency(f"{here}/hiq.conf")
        try:
            hiq.mod("main").main()
        except Exception as e:
            print(e)
        driver.show()


if __name__ == "__main__":
    run_main()
