import os
import hiq
from typing import *
import time
from hiq.memory import get_memory_mb
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)
from hiq.utils import get_env_int

here = os.path.dirname(os.path.realpath(__file__))

HIQ_PADDLEOCR_CONF = hiq.hiq_utils.read_csv_to_list(f"{here}/paddleocr.conf")


class PaddleOcrHiQLatency(hiq.HiQSimple):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        extra_hiq_table += HIQ_PADDLEOCR_CONF
        hiq.HiQSimple.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(s):
        s.o_paddle_run = hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run

        @s.inserter
        def paddle_run(self) -> bool:
            return s.o_paddle_run(self)

        hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run = paddle_run

    def custom_disable(s):
        hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run = s.o_paddle_run


class PaddleOcrHiQMemory(hiq.HiQMemory):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, get_memory_mb],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        extra_hiq_table += HIQ_PADDLEOCR_CONF
        hiq.HiQSimple.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(s):
        s.o_paddle_run = hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run

        @s.inserter
        def paddle_run(self) -> bool:
            return s.o_paddle_run(self)

        hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run = paddle_run

    def custom_disable(s):
        hiq.mod("paddle.fluid.core_avx").PaddleInferPredictor.run = s.o_paddle_run
