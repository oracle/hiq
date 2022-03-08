import os
import hiq


def run_main():
    driver = hiq.HiQLatency(
        hiq_table_or_path=[
            ["myapp.__main__", "", "main", "main"],
            ["myapp.__main__", "", "add", "add"],
            ["myapp.__main__", "", "multiply", "multiply"],
            ["myapp.__main__", "", "square", "square"],
            ["myapp.__main__", "", "quadratic", "quadratic"],
        ]
    )
    hiq.mod("myapp.__main__").main()
    driver.show()


if __name__ == "__main__":
    os.environ["ZIN_THRESHOLD"] = "0.1"
    run_main()
