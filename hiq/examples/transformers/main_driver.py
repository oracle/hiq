import hiq


def run_main():
    hiq_quadruple = [
        ["transformers.pipelines.base", "", "infer_framework_load_model", "f1"],
        ["transformers", "AutoConfig", "from_pretrained", "from_pretrained"],
        ["transformers", "Pipeline", "__call__", "pp_call"],
    ]

    driver = hiq.HiQTransformerGPUMemory(
        hiq_table_or_path=hiq_quadruple,
        attach_timestamp=True,
        max_hiq_size=1,
        extra_metrics={hiq.ExtraMetrics.ARGS},
    )
    hiq.mod("main").main()
    driver.show()


if __name__ == "__main__":
    run_main()
