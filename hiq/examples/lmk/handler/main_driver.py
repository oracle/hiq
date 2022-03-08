import os
import hiq


def run_main():
    _ = hiq.HiQLatency(
        hiq_table_or_path=[
            ["main", "", "main", "main"],
            ["main", "", "func1", "func1"],
            ["main", "", "func2", "func2"],
        ],
    )
    hiq.mod("main").main()


if __name__ == "__main__":
    os.environ["LMK"] = "1"
    run_main()
