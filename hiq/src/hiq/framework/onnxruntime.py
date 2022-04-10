import hiq
import os
from typing import *
import time
from hiq.memory import get_memory_mb
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)
from hiq.utils import get_env_int

TAU_ORT = "onnxruntime.capi.onnxruntime_inference_collection"

TAU_TBL_ORT = [
    (TAU_ORT, "Session", "run", "ort_run"),
    (TAU_ORT, "Session", "__init__", "sess_init"),
    (TAU_ORT, "Session", "run_with_ort_values", "run_with_ort_values"),
    (TAU_ORT, "Session", "run_with_iobinding", "run_with_iobinding"),
    (TAU_ORT, "InferenceSession", "_create_inference_session", "create_inference_session"),
    (TAU_ORT, "InferenceSession", "_reset_session", "reset_session"),
]

def get_ort_session(sess_options):
    if "HIQ_ORT_INTRA_OPS_THREAD" in os.environ:
        import onnxruntime as ort
        if sess_options is None:
            sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = get_env_int("HIQ_ORT_INTRA_OPS_THREAD")
    return sess_options

class OrtHiQLatency(hiq.HiQSimple):
    
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
        extra_hiq_table += TAU_TBL_ORT
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
        s.o_ort_session = hiq.mod(TAU_ORT).InferenceSession.__init__

        @s.inserter
        def ort_session(self,
                path_or_bytes,
                sess_options=None,
                providers=None,
                provider_options=None):
            return s.o_ort_session(
                    self, path_or_bytes, get_ort_session(sess_options), providers, provider_options
                )
        hiq.mod(TAU_ORT).InferenceSession.__init__ = ort_session

    def custom_disable(s):
        hiq.mod(TAU_ORT).InferenceSession.__init__ = s.o_ort_session


class OrtHiQMemory(hiq.HiQMemory):
    
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
        extra_hiq_table += TAU_TBL_ORT
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
        s.o_ort_session = hiq.mod(TAU_ORT).InferenceSession.__init__

        @s.inserter
        def ort_session(self,
                path_or_bytes,
                sess_options=None,
                providers=None,
                provider_options=None):
            return s.o_ort_session(
                    self, path_or_bytes, get_ort_session(sess_options), providers, provider_options
                )
        hiq.mod(TAU_ORT).InferenceSession.__init__ = ort_session

    def custom_disable(s):
        hiq.mod(TAU_ORT).InferenceSession.__init__ = s.o_ort_session
