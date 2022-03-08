import hiq


def run_main():
    driver = hiq.HiQLatency(
        hiq_table_or_path=[
            ["main", "", "main", "main"],
            ["main", "", "func1", "func1"],
            ["main", "", "func2", "func2"],
        ]
    )
    hiq.mod("main").main()
    driver.show()


if __name__ == "__main__":
    run_main()
