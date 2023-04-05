import hiq
from hiq.constants import HIQ_TABLE_SIO_RD, TAU_TABLE_DIO_RD, TAU_TABLE_NIO_GET
import time


def run_translate():
    hiq_quadruple = [
        ["transformers.pipelines.base", "", "infer_framework_load_model", "f1"],
        ["transformers", "AutoConfig", "from_pretrained", "from_pretrained"],
        ["transformers", "Pipeline", "__call__", "pp_call"],
        ["torch", "", "load", "torch_load"],
    ]

    driver = hiq.HiQTransformerGPUMemory(
        hiq_table_or_path=hiq_quadruple,
        attach_timestamp=True,
        max_hiq_size=1,
        extra_metrics={hiq.ExtraMetrics.ARGS},
        # extra_hiq_table=[TAU_TABLE_DIO_RD],
    )
    hiq.mod("t5_translation").translate()
    driver.show()


if __name__ == "__main__":
    run_translate()
