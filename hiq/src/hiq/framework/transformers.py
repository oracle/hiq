import time
import hiq
from hiq.memory import get_memory_mb, total_gpu_memory_mb
import os
import hiq
from typing import *
import time
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)
from hiq.utils import get_env_int


class TransformerMixin(object):
    def custom(self):
        self.o_signature = hiq.mod("inspect").signature
        hiq.mod("inspect").signature = hiq.utils.signature

    def custom_disable(self):
        hiq.mod("inspect").signature = self.o_signature


class HiQTransformerMemory(TransformerMixin, hiq.HiQMemory):
    pass


class HiQTransformerGPUMemory(TransformerMixin, hiq.HiQMemory):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, total_gpu_memory_mb],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),  # EXTRA_METRIC_FILE
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
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


class HiQTransformerFullMemory(TransformerMixin, hiq.HiQMemory):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, get_memory_mb, total_gpu_memory_mb],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),  # EXTRA_METRIC_FILE
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
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


class HiQTransformerLatency(TransformerMixin, hiq.HiQLatency):
    pass
